#!/bin/zsh

# Genericization variables:
#   ORG_NETWORK_LOCK_DIR: Lock directory used to prevent overlapping runs. Defaults to /var/tmp/org-network-single-interface.lock.
#   ORG_WIFI_STATE_FILE: State file recording Wi-Fi disablement by policy. Defaults to /var/tmp/org-wifi-disabled-by-policy.

# Use zsh behavior explicitly when Jamf launches the script.
emulate -L zsh

# Prevent overlapping executions.
# Jamf/network-change triggers can fire repeatedly when this script changes Wi-Fi state.
LOCK_DIR="${ORG_NETWORK_LOCK_DIR:-/var/tmp/org-network-single-interface.lock}"
STATE_FILE="${ORG_WIFI_STATE_FILE:-/var/tmp/org-wifi-disabled-by-policy}"

if ! /bin/mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another instance is already running. Exiting."
  exit 0
fi

cleanup() {
  /bin/rmdir "$LOCK_DIR" 2>/dev/null
}
trap 'cleanup' EXIT

NETWORKSETUP="/usr/sbin/networksetup"
IFCONFIG="/sbin/ifconfig"
AWK="/usr/bin/awk"
GREP="/usr/bin/grep"

# Find the Wi-Fi hardware device. Modern macOS uses Wi-Fi; older systems may show AirPort.
wifi_device="$($NETWORKSETUP -listallhardwareports | "$AWK" '
  /Hardware Port: (Wi-Fi|AirPort)/ {
    getline
    if ($1 == "Device:") {
      print $2
      exit
    }
  }
')"

if [[ -z "$wifi_device" ]]; then
  echo "No Wi-Fi hardware device found. Exiting."
  exit 0
fi

# Detect active physical wired Ethernet-like interfaces.
# This intentionally excludes Wi-Fi, Bluetooth PAN, and Thunderbolt Bridge.
wired_devices=("${(@f)$($NETWORKSETUP -listallhardwareports | "$AWK" '
  /Hardware Port:/ {
    port=$0
    getline
    if ($1 == "Device:") {
      device=$2
      if (port ~ /Ethernet|USB.*LAN|USB.*Ethernet|Thunderbolt Ethernet/) {
        print device
      }
    }
  }
')}")

wired_active="false"

for device in "${wired_devices[@]}"; do
  [[ -z "$device" ]] && continue

  if "$IFCONFIG" "$device" 2>/dev/null | "$GREP" -q "status: active"; then
    echo "Active wired interface detected: $device"
    wired_active="true"
    break
  fi
done

wifi_status="$($NETWORKSETUP -getairportpower "$wifi_device" 2>/dev/null | "$AWK" '{print $NF}')"

if [[ "$wired_active" == "true" && "$wifi_status" == "On" ]]; then
  echo "Disabling Wi-Fi because a wired interface is active."
  "$NETWORKSETUP" -setairportpower "$wifi_device" off

  # Record that this script disabled Wi-Fi, so it may safely restore it later.
  /usr/bin/touch "$STATE_FILE"

elif [[ "$wired_active" == "false" && "$wifi_status" == "Off" && -f "$STATE_FILE" ]]; then
  echo "Re-enabling Wi-Fi because no wired interface is active and this script previously disabled it."
  "$NETWORKSETUP" -setairportpower "$wifi_device" on
  /bin/rm -f "$STATE_FILE"

else
  echo "No Wi-Fi state change required. wired_active=$wired_active wifi_status=$wifi_status"
fi

exit 0

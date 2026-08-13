# Prevent Multi-Homing Script Behavior

The script enforces the policy by making Wi-Fi subordinate to wired Ethernet. It does not disable wired interfaces. It only turns Wi-Fi back on when it can prove that this script previously disabled it. The logic here is that if you're on WiFi, and plug Ethernet in, disabling WiFi is safe; if you're already on Ethernet and turn WiFi on, disabling WiFi is safe. Disabling Ethernet is a little less safe, so we avoid that by prefering Ethernet at the expense of WiFi; this is a known limitation as discussed below.

## Expected Benefits Versus the Original Script

The improved script should be more reliable under Jamf network-change triggers because it uses an atomic lock directory to prevent overlapping executions. The original script sleeps after making a change, but that delay does not prevent another copy from starting while the first one is still running.

The improved script is safer operationally because it records when it disabled Wi-Fi. It only re-enables Wi-Fi if that state file exists. This prevents the script from turning Wi-Fi back on after a user, admin, troubleshooting workflow, or MDM policy intentionally disabled it.

The improved script should produce fewer false positives because it looks for wired Ethernet-like hardware ports instead of treating every non-Wi-Fi `enX` device as Ethernet. This reduces the chance that Bluetooth PAN, Thunderbolt Bridge, or other non-Ethernet services cause Wi-Fi to be disabled incorrectly.

The improved script is easier to troubleshoot from Jamf logs because it emits explicit messages for each decision path: active wired interface found, Wi-Fi disabled, Wi-Fi restored, no Wi-Fi hardware found, another instance already running, or no state change required.

## Scenario Behavior

For reference, here are some common scenarios considered and how the script should perform under each of them. 
_At this time (7/23/26), this has not been verified with actual testing_

| Scenario | Expected Behavior |
|---|---|
| No wired Ethernet active, Wi-Fi on | No change. The Mac remains on Wi-Fi. |
| No wired Ethernet active, Wi-Fi off, script did not disable it | No change. Wi-Fi stays off. This avoids overriding a user, admin, or MDM decision. |
| No wired Ethernet active, Wi-Fi off, script previously disabled it | Wi-Fi is re-enabled, and the state file is removed. |
| Wired Ethernet active, Wi-Fi on | Wi-Fi is disabled. The script creates `/var/tmp/gdms-wifi-disabled-by-policy` to record that it made the change. |
| Wired Ethernet active, Wi-Fi off | No change. The Mac remains wired-only. |
| Wired Ethernet disconnects after script disabled Wi-Fi | On the next network-change trigger, Wi-Fi is turned back on. |
| User manually turns Wi-Fi off while no Ethernet is active | Script leaves Wi-Fi off because the state file is absent. |
| User manually turns Wi-Fi on while Ethernet is active | On the next trigger, script disables Wi-Fi again. |
| Multiple wired Ethernet adapters active | Script detects wired activity and disables Wi-Fi, but it does not disable extra wired adapters. This script prevents Wi-Fi plus wired multi-homing, not wired plus wired multi-homing. |
| Bluetooth PAN active, Wi-Fi on | No change. Bluetooth PAN is intentionally excluded. |
| Thunderbolt Bridge active, Wi-Fi on | No change. Thunderbolt Bridge is intentionally excluded to avoid false positives. |
| USB Ethernet adapter active, Wi-Fi on | Wi-Fi should be disabled if the hardware port name includes `Ethernet`, `USB LAN`, or `USB Ethernet`. |
| No Wi-Fi hardware found | Script exits without change. This is safe for desktops or unusual hardware states. |
| Jamf fires the script multiple times quickly | Only one instance proceeds. Later overlapping instances exit because the lock directory already exists. |
| Script causes its own network-change event | The lock reduces immediate duplicate execution. A later trigger may still run, but it should see the already-correct state and make no change. |

## Operational Notes

The lock is implemented with `/var/tmp/gdms-network-single-interface.lock`. Because `mkdir` is atomic, it is suitable for preventing overlapping script instances in shell scripts.

The state file is the main safety control. Without it, the script could re-enable Wi-Fi after someone intentionally disabled it. With it, the script only restores Wi-Fi when the prior disable action was policy-driven.

The script uses `/usr/sbin/networksetup` to identify and control Wi-Fi power. That is the supported macOS command-line utility for network service configuration, including `-getairportpower`, `-setairportpower`, and hardware port listing (`networksetup(8)`). It uses `/sbin/ifconfig` to check whether wired interfaces report `status: active`.

## Known Limitation

The policy really is that "only one active network interface of any type," but this script is narrower than that. It handles the most common violation: Wi-Fi active while wired Ethernet is active. It does not remediate multiple active wired adapters, VPN interfaces, cellular/iPhone USB, or other network paths.

Because it prefers Ethernet to WiFi, it will disable WiFi any time Ethernet is plugged in, _even if there is no Internet on the Ethernet connection._ If that interface is active, it will turn off WiFi. This might be an important troubleshooting consideration down the road.

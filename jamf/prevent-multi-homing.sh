#!/usr/bin/env sh

# Genericization variables:
#   No private deployment variables are required. Network interface names are discovered at runtime.

# Grab the names of the adapters. We assume here that any ethernet connection is any connection that isn't explicitly called "WiFi"
ethernet=`networksetup -listnetworkserviceorder | sed -n '/Hardware Port: Wi-Fi/!{/Hardware Port:/s/.*Device: \(en[0-9]*\))/\1/p;}'`
wifi=`networksetup -listnetworkserviceorder | sed -En 's/^\(Hardware Port: (Wi-Fi|AirPort), Device: (en.)\)$/\2/p'`

# Start with the assumption that both Ethernet and WiFi are off:
eth_status="Off"
wifi_status="Off"

# Check actual current ethernet status; we will set it to On if it is active to match AirPort status
for ethernet in ${ethernet}; do
  if ([ "$ethernet" != "" ] && [ "`ifconfig $ethernet | grep "status: active"`" != "" ]); then
    eth_status="On"
  fi
done

# And actual current AirPort status - this will be On or Off
wifi_status=`/usr/sbin/networksetup -getairportpower $wifi | awk '{ print $4 }'`

# Now, to do the toggling - here, we just turn WiFi OFF if there is an Ethernet connection and turn it back ON if there is
# no Ethernet connection.

if [ "$eth_status" == "On" ] && [ "$wifi_status" == "On" ]; then
  echo "disabling wifi"
  networksetup -setairportpower "$wifi" off
  echo "Wi-Fi Disabled"
elif [ "$eth_status" == "Off" ] && [ "$wifi_status" == "Off" ]; then
  echo "enabling wifi"
  networksetup -setairportpower "$wifi" on
  echo "Wi-Fi Enabled"
else
  echo "not toggling wifi status"
fi

# Wait 5 seconds to prevent this from running too frequently
# since it sees its own toggle as a network state change!
/bin/sleep 10

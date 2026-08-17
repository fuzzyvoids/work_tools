# Written By: Rob Fischer, EDR Security Engineer
# Last Edit: 5/6/26, 7:05 PM
#

# No Parameterization 
#

#!/bin/bash

# The ComputerName is usually the friendly name that is always set
# The HostName and NetBIOS names are the ones that aren't always set, and will cause problems 
# on the network if the aren't. This script attempts to fix that problem.

name=$(/usr/sbin/scutil --get ComputerName)
host=$(/usr/sbin/scutil --get HostName)
netbios=$(/usr/bin/defaults read /Library/Preferences/SystemConfiguration/com.apple.smb.server.plist NetBIOSName)


echo "ComputerName is $name"
echo "HostName is $host"
echo "NetBIOS Name is $netbios"

if [[ "$host" == "$name" ]]; then
  echo "no change to HostName needed."  
else 
  echo "changing HostName to $name" && sudo /usr/local/bin/jamf setComputername -name $name
fi

if [[ "$host" == "$netbios" ]]; then
  echo "no change to NetBIOS needed"
else 
  echo "changing NetBIOS to $name" && sudo /usr/bin/defaults write /Library/Preferences/SystemConfiguration/com.apple.smb.server.plist NetBIOSName $name
fi

exit 0

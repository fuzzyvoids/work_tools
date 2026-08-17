# ZScaler Uninstallation Script
# Written by Rob Fischer, EDR Security Engineer
# Last Edits:
# 6/15/26
# Changed launchctl unload to launchctl bootout system/ to reflect newer API
# 6/12/26 
# Changes: added a "safety check" to ensure that cached installer was 
# present before preceeding with uninstall of old ZScaler
###

###
# Parameterization:
# Parameter 4 - Un-installation Password (provided by SOE)
# Parameter 5 - Filename of the new ZScaler package; e.g. Zscaler-osx-4.8.0.191-installer.pkg
###

password="$4"
file="$5"

installer="/Library/Application Support/JAMF/Waiting Room/$file"

if [ -f "$installer" ]; then
	sudo /Applications/Zscaler/.Uninstaller.sh "$password"
    # Unload any residual running processes and then delete any residual files to ensure a clean un-install
    sudo launchctl bootout system/ /Library/LaunchDaemons/com.zscaler.service.plist || true
    sudo launchctl bootout system/ /Library/LaunchDaemons/com.zscaler.tunnel.plist || true
    # Remove any residual configuration files to ensure a clean un-install
    sudo rm -rf /Library/Application\ Support/Zscaler || true
    sudo rm -rf /Library/LaunchDaemons/com.zscaler* || true
    sudo rm -rf /Library/LaunchAgents/com.zscaler* || true
	exit 0
else 
	echo "New ZScaler installer not cached!"
    exit 1
fi

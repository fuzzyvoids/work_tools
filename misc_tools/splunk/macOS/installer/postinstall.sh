#!/bin/bash

## postinstall

# Splunk Universal Forwarder - macOS Silent Installation Script
# This script is designed to run as a postinstall script in a .pkg installer.
# Specifies the shell setting to ensure the script stops immediately if any step fails:
# Copied from https://help.splunk.com/en/splunk-cloud-platform/forward-and-process-data/universal-forwarder-manual/10.2/install-the-universal-forwarder/deploying-the-universal-forwarder-to-a-macos-fleet
# Modified by Rob Fischer with info from John White
# Last edit 6/26/26

set -euo pipefail

# Configure logging and error handling
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

die() {
	echo "[ERROR] $*" >&2
	exit 1
}

# Configures the installation paths:
SPLUNK_HOME="/opt/splunkforwarder"
STAGING_DIR="/var/tmp/splunk_install"
CONF_FILES=("deploymentclient.conf" "outputs.conf" "user-seed.conf")

# Validate Prerequisites
[ "$(id -u)" -eq 0 ] || die "This script must be run as root."
[ -d "${STAGING_DIR}" ] || die "Staging directory not found: ${STAGING_DIR}"
shopt -s nullglob
SPLUNK_PKGS=("${STAGING_DIR}"/splunkforwarder-*.tgz)
shopt -u nullglob
[ "${#SPLUNK_PKGS[@]}" -gt 0 ] || die "No Splunk forwarder package found in ${STAGING_DIR}"
SPLUNK_PKG="${SPLUNK_PKGS[0]}"

# Extracts the universal forwarder package to the /opt folder:
log "Extracting Splunk Universal Forwarder..."
cd /opt || die "Failed to change directory to /opt"
#tar xzf "${STAGING_DIR}/splunkforwarder-*.tgz"
tar xzf "${SPLUNK_PKG}" -C /opt

# Terminates any existing splunkd process:
pkill splunkd 2>/dev/null || true
sleep 2

# Deploys the configuration files into the Splunk Enterprise /local folder:
log "Deploying configuration files..."
mkdir -p "${SPLUNK_HOME}/etc/system/local"
#cp "${STAGING_DIR}/deploymentclient.conf" "${SPLUNK_HOME}/etc/system/local/" 2>/dev/null || true
#cp "${STAGING_DIR}/outputs.conf" "${SPLUNK_HOME}/etc/system/local/" 2>/dev/null || true
#cp "${STAGING_DIR}/user-seed.conf" "${SPLUNK_HOME}/etc/system/local/" 2>/dev/null || true
for conf in "${CONF_FILES[@]}"; do
	src="${STAGING_DIR}/${conf}"
	if [ -f "${src}" ]; then
		cp "${src}" "${SPLUNK_HOME}/etc/system/local/"
		log " Copied: ${conf}"
	else
		log " Warning: ${conf} not found in $STAGING_DIR, skipping"
	fi
done

# Sets ownership (runs as root by default):
chown -R root:wheel "${SPLUNK_HOME}"

# Accepts the license and starts the universal forwarder:
log "Starting Splunk Universal Forwarder..."
"${SPLUNK_HOME}/bin/splunk" start --accept-license --no-prompt --answer-yes || die "Failed to start Splunk"

# Registers boot-start with the Launch Daemon system service:
log "Enabling boot-start..."
"${SPLUNK_HOME}/bin/splunk" enable boot-start || die "Failed to enable boot-start"

# Moves the Launch Daemon to the correct system location (the/LaunchDaemons folder) if needed:
if [ -f "/Library/LaunchAgents/com.splunk.splunkd.plist" ]; then
	mv "/Library/LaunchAgents/com.splunk.splunkd.plist" "/Library/LaunchDaemons/"
fi
if [ -f "/Library/LaunchAgents/com.splunk.plist" ]; then
	mv "/Library/LaunchAgents/com.splunk.plist" "/Library/LaunchDaemons/"
fi

# Loads the Launch Daemon
# launchctl unload /Library/LaunchDaemons/com.splunk.plist 2>/dev/null || true sleep 1 launchctl load /Library/LaunchDaemons/com.splunk.plist
if [ -f "/Library/LaunchDaemons/com.splunk.plist" ]; then
	log "Loading Launch Daemon..."
	launchctl unload /Library/LaunchDaemons/com.splunk.plist 2>/dev/null || true
	sleep 1
	launchctl load /Library/LaunchDaemons/com.splunk.plist || die "Failed to load LaunchDaemon"
else
	die "LaunchDaemon Plist not found"
fi

# Remove the staging files to clean up the installation directory:
rm -rf "${STAGING_DIR}"
log "Splunk Universal Forwarder installation complete."

exit 0		## Success

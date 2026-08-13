#!/bin/bash

# This Script will correct the error that occurs when splunkd fails to launch
# Genericization variables:
#   SPLUNK_LAUNCHD_PLIST: Splunk LaunchDaemon plist path. Defaults to /Library/LaunchDaemons/com.splunk.plist.
#   SPLUNK_PLISTBUDDY: PlistBuddy path. Defaults to /usr/libexec/PlistBuddy.
#   DEFAULT_SPLUNK_HOME: Default Splunk Universal Forwarder install path.
# due to not having its SPLUNK_HOME environment variable set.
# This occurs because splunk/splunkd are run via launchd/launchctl rather than
# just as the root (or any other) user.
# It inserts SPLUNK_HOME EnvironmentVariables key into the Splunk LaunchDaemon
# plist file immediately before the <key>ProgramArguments</key> line.

set -uo pipefail

# Parameterization
# Paramter 4 = the intended SPLUNK_HOME environment variable
# (also the directory where splunk is installed)

PLIST="${SPLUNK_LAUNCHD_PLIST:-/Library/LaunchDaemons/com.splunk.plist}"
PLISTBUDDY="${SPLUNK_PLISTBUDDY:-/usr/libexec/PlistBuddy}"
DEFAULT_SPLUNK_HOME="${DEFAULT_SPLUNK_HOME:-/opt/splunkforwarder}"

# Jamf passes script parameters in $4 and later. Default to DEFAULT_SPLUNK_HOME
# when parameter 4 is not provided.
SPLUNK_HOME="${4:-$DEFAULT_SPLUNK_HOME}"
# These are the explicit installation directories if you need them:
# SPLUNK_HOME="/Applications/SplunkForwarder/" #old
# SPLUNK_HOME="/opt/splunkforwarder" #current

log_info() {
    echo "[INFO]  $*"
}

log_warn() {
    echo "[WARN]  $*"
}

die() {
    echo "[ERROR] $*" >&2
    exit 1
}

# Pre-execution safety checks:

# Ensure running as root
if [[ $EUID -ne 0 ]]; then
    die "This script must be run as root (use sudo)."
fi
# Ensure plist exists
if [[ ! -f "$PLIST" ]]; then
    die "Plist file not found: $PLIST"
fi
[[ -x "$PLISTBUDDY" ]] || die "PlistBuddy not found or not executable: $PLISTBUDDY"
[[ -x "${SPLUNK_HOME}/bin/splunk" ]] || die "Splunk binary not found or not executable: ${SPLUNK_HOME}/bin/splunk"

# Create a backup of the Plist we can recover from if things go sideways

BACKUP="/tmp/$(basename "$PLIST").bak.$(date +%Y%m%d%H%M%S)"
cp "$PLIST" "$BACKUP"
log_info "Backup created: $BACKUP"

# Add or update only the SPLUNK_HOME environment variable. This preserves all
# other LaunchDaemon keys that Splunk created during boot-start registration.

log_info "Setting SPLUNK_HOME in $PLIST..."

if ! "$PLISTBUDDY" -c "Print :EnvironmentVariables" "$PLIST" > /dev/null 2>&1; then
    "$PLISTBUDDY" -c "Add :EnvironmentVariables dict" "$PLIST" \
        || die "Failed to add EnvironmentVariables dictionary."
fi

if "$PLISTBUDDY" -c "Print :EnvironmentVariables:SPLUNK_HOME" "$PLIST" > /dev/null 2>&1; then
    "$PLISTBUDDY" -c "Set :EnvironmentVariables:SPLUNK_HOME ${SPLUNK_HOME}" "$PLIST" \
        || die "Failed to update SPLUNK_HOME."
else
    "$PLISTBUDDY" -c "Add :EnvironmentVariables:SPLUNK_HOME string ${SPLUNK_HOME}" "$PLIST" \
        || die "Failed to add SPLUNK_HOME."
fi

# Validate we inserted it AT ALL

if grep -q "EnvironmentVariables" "$PLIST"; then
    log_info "EnvironmentVariables block inserted successfully."
else
    echo "[ERROR] Insertion failed. Restoring backup..."
    cp "$BACKUP" "$PLIST"
    log_info "Original plist restored from backup."
    exit 1
fi

# Validate that we inserted it CORRECTLY

log_info "Validating plist syntax..."
if plutil -lint "$PLIST" > /dev/null 2>&1; then
    log_info "Plist syntax is valid."
else
    echo "[ERROR] Plist syntax validation failed. Restoring backup..."
    cp "$BACKUP" "$PLIST"
    log_info "Original plist restored from backup."
    exit 1
fi

# Reload the LaunchDaemon

log_info "Reloading LaunchDaemon..."
if launchctl unload "$PLIST" 2>/dev/null; then
    log_info "Existing LaunchDaemon unloaded."
else
    log_warn "LaunchDaemon was not loaded or could not be unloaded; continuing."
fi

if launchctl load "$PLIST"; then
    log_info "LaunchDaemon reloaded successfully."
else
    echo "[ERROR] Failed to reload LaunchDaemon. Check system logs:"
    echo "        log show --predicate 'process == \"launchd\"' --last 1m"
    exit 1
fi

# Checks if Splunk is running and starts it if it isn't

if pgrep -x "splunkd" > /dev/null 2>&1; then
    log_info "splunkd is already running (PID: $(pgrep -x splunkd))."
else
    log_warn "splunkd is not running. Attempting to start..."
    "${SPLUNK_HOME}/bin/splunk" start

    if pgrep -x "splunkd" > /dev/null 2>&1; then
        log_info "splunkd started successfully (PID: $(pgrep -x splunkd))."
    else
        echo "[ERROR] Failed to start splunkd. Check logs at:"
        echo "        ${SPLUNK_HOME}/var/log/splunk/splunkd.log"
        exit 1
    fi
fi

# Checking Splunk Status as a final step

log_info "Verifying Splunk status..."
sleep 2
STATUS_OUTPUT=$("${SPLUNK_HOME}/bin/splunk" status 2>&1)
echo "$STATUS_OUTPUT"

# Check for expected output lines:
#   "splunkd is running (PID: <number>)."
SPLUNKD_RUNNING=false

if echo "$STATUS_OUTPUT" | grep -qE "^splunkd is running \(PID: [0-9]+\)\."; then
    SPLUNKD_RUNNING=true
fi

if $SPLUNKD_RUNNING; then
    log_info "Splunk is running as expected."
else
    log_warn "Splunk status does not match the expected output."
    if ! $SPLUNKD_RUNNING; then
        log_warn "'splunkd is running (PID: <#>).' was not detected."
    fi
    log_warn "The plist was updated successfully, but Splunk may need"
    echo "        additional time to start or may require further investigation."
    echo "        Check logs at: ${SPLUNK_HOME}/var/log/splunk/splunkd.log"
fi

exit 0

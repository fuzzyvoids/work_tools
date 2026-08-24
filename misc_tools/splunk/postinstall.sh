#!/bin/sh

pathToScript=$0
pathToPackage=$1
targetLocation=$2
targetVolume=$3

# Splunk Universal Forwarder - macOS in-place upgrade postinstall script
# Written by Rob Fischer, EDR Security Engineer. 
# Last edit: 8/24/2026
# This script is intended to run as the postinstall script inside a macOS .pkg
# built through Jamf Composer - make sure to sign it when you're done!
# It adapts the script provided by Splunk for a remote upgrade to instead as a local
# package install: choose the correct UF archive, stop the current forwarder,
# unpack the new files into the active install path, restart Splunk, and clean
# up the staged archives from /tmp.


# Package staging location. The .pkg payload is expected to install the two
# archives directly here.
# This will be where dependent upon how you've built your image in Composer

STAGING_DIR="/tmp"

# The .pkg payload should place both architecture-specific UF archives in /tmp.
# These patterns intentionally wildcard the version/build string so the script
# can be reused when the package is rebuilt with newer Splunk UF tarballs.

ARM_SPLUNK_PATTERN="splunkforwarder-*-darwin-arm64.tgz"
INTEL_SPLUNK_PATTERN="splunkforwarder-*-darwin-intel.tgz"

# Known install locations in the target macOS environment. The script detects
# which one is currently active and upgrades that location in place.

CURRENT_OPT_HOME="/opt/splunkforwarder"
LEGACY_APP_HOME="/Applications/SplunkForwarder"

# If no existing installation is found, install to the current standard path.
# This makes the script usable for first-time installs, but the primary intent
# remains in-place upgrades.

DEFAULT_SPLUNK_HOME="$CURRENT_OPT_HOME"

set -u

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

require_root() {
    # This check is just to make a failure obvious in Jamf or Installer logs.
    if [ "$(id -u)" -ne 0 ]; then
        die "This script must be run as root."
    fi
}

require_macos() {
    # Again, just making errors obvious in the logs; we only want this on macOS
    if [ "$(uname -s)" != "Darwin" ]; then
        die "This script is intended for macOS only."
    fi
}

select_architecture_archive() {
    # The package is intended for both archives. Selects the one matching the local CPU.
    case "$(uname -m)" in
        arm64)
            SPLUNK_ARCHIVE_PATTERN="$ARM_SPLUNK_PATTERN"
            ;;
        x86_64)
            SPLUNK_ARCHIVE_PATTERN="$INTEL_SPLUNK_PATTERN"
            ;;
        *)
            die "Unsupported macOS architecture: $(uname -m)"
            ;;
    esac

    # Expand the selected glob. If no file matches, POSIX sh leaves the pattern
    # unchanged, so verify that the first expanded value is really a file.
    set -- "$STAGING_DIR"/$SPLUNK_ARCHIVE_PATTERN

    if [ "$#" -eq 0 ] || [ ! -f "$1" ]; then
        die "Selected Splunk archive not found. Expected one match for: $STAGING_DIR/$SPLUNK_ARCHIVE_PATTERN"
    fi

    if [ "$#" -gt 1 ]; then
        die "Multiple Splunk archives matched $STAGING_DIR/$SPLUNK_ARCHIVE_PATTERN. Remove stale archives from $STAGING_DIR before installing."
    fi

    SPLUNK_ARCHIVE="$1"
    log_info "Selected archive: $SPLUNK_ARCHIVE"
}

detect_splunk_home() {
    # Prefer the active install location. Some target hosts use the documented/preferred
    # /opt path, while older hosts may still use /Applications/SplunkForwarder from the old installer.
    if [ -x "$CURRENT_OPT_HOME/bin/splunk" ]; then
        SPLUNK_HOME="$CURRENT_OPT_HOME"
        log_info "Detected existing Splunk UF install: $SPLUNK_HOME"
    elif [ -x "$LEGACY_APP_HOME/bin/splunk" ]; then
        SPLUNK_HOME="$LEGACY_APP_HOME"
        log_info "Detected existing Splunk UF install: $SPLUNK_HOME"
    elif [ -d "$LEGACY_APP_HOME/bin/Splunk.app" ]; then
        # Splunk should still live under /Applications/SplunkForwarder, even if the Jamf thinks the app lives here.
        SPLUNK_HOME="$LEGACY_APP_HOME"
        log_info "Detected legacy Splunk app bundle under: $LEGACY_APP_HOME/bin/Splunk.app"
    else
        SPLUNK_HOME="$DEFAULT_SPLUNK_HOME"
        log_warn "No existing Splunk UF install detected; defaulting to: $SPLUNK_HOME"
    fi

    SPLUNK_PARENT=$(dirname "$SPLUNK_HOME")
    SPLUNK_BASENAME=$(basename "$SPLUNK_HOME")
}

stop_splunk() {
    # Use the Splunk CLI when available so the forwarder can stop cleanly. Fall
    # back to pkill only when the CLI is unavailable or the stop command fails.
    if [ -x "$SPLUNK_HOME/bin/splunk" ]; then
        log_info "Stopping Splunk UF at $SPLUNK_HOME"
        if "$SPLUNK_HOME/bin/splunk" stop --answer-yes --no-prompt; then
            return 0
        fi
        log_warn "Splunk CLI stop failed; attempting to stop splunkd by process name."
    else
        log_warn "Splunk CLI not found at $SPLUNK_HOME/bin/splunk; attempting process stop only."
    fi

    pkill -x splunkd 2>/dev/null || true
    sleep 2
}

get_archive_top_dir() {
    # Splunk UF tarballs normally contain one top-level directory. Detect it so
    # the script can merge into either /opt/splunkforwarder or the legacy
    # /Applications/SplunkForwarder path without assuming archive structure.
    # In other words, avoid screwing up the existing file structure!
    ARCHIVE_TOP_DIR=$(tar -tzf "$SPLUNK_ARCHIVE" 2>/dev/null | awk -F/ 'NF {print $1; exit}')
    [ -n "$ARCHIVE_TOP_DIR" ] || die "Could not determine top-level directory in $SPLUNK_ARCHIVE"
}

extract_upgrade() {
    mkdir -p "$SPLUNK_PARENT" || die "Could not create install parent: $SPLUNK_PARENT"
    get_archive_top_dir

    if [ "$ARCHIVE_TOP_DIR" = "$SPLUNK_BASENAME" ]; then
        # Best case: the tarball directory name matches the active install path.
        # This mirrors Splunk's remote_upgrade.sh behavior exactly
        # and sticks the files right where the documentation says they ought to go.
        log_info "Extracting archive directly into $SPLUNK_PARENT"
        (cd "$SPLUNK_PARENT" && tar -zxf "$SPLUNK_ARCHIVE") \
            || die "Could not extract $SPLUNK_ARCHIVE into $SPLUNK_PARENT"
    else
        # Legacy /Applications/SplunkForwarder installs may not match the UF
        # tarball's top-level directory name. Extract to a temp directory, then
        # merge contents into the detected SPLUNK_HOME while preserving local
        # configuration files already present under etc/system/local.
        TMP_EXTRACT_DIR="$STAGING_DIR/splunk_uf_upgrade.$$"
        rm -rf "$TMP_EXTRACT_DIR"
        mkdir -p "$TMP_EXTRACT_DIR" || die "Could not create temp extraction directory: $TMP_EXTRACT_DIR"

        log_info "Extracting archive to temporary directory: $TMP_EXTRACT_DIR"
        (cd "$TMP_EXTRACT_DIR" && tar -zxf "$SPLUNK_ARCHIVE") \
            || die "Could not extract $SPLUNK_ARCHIVE into $TMP_EXTRACT_DIR"

        EXTRACTED_HOME="$TMP_EXTRACT_DIR/$ARCHIVE_TOP_DIR"
        [ -d "$EXTRACTED_HOME" ] || die "Expected extracted directory not found: $EXTRACTED_HOME"

        mkdir -p "$SPLUNK_HOME" || die "Could not create install path: $SPLUNK_HOME"
        log_info "Merging extracted files into detected install path: $SPLUNK_HOME"
        /usr/bin/ditto "$EXTRACTED_HOME" "$SPLUNK_HOME" \
            || die "Could not merge extracted files into $SPLUNK_HOME"

        rm -rf "$TMP_EXTRACT_DIR"
    fi
}

set_permissions() {
    # The existing local package uses root:wheel ownership. Preserve that model
    # after the upgrade so launchd and Splunk CLI behavior remain predictable.
    log_info "Setting ownership on $SPLUNK_HOME"
    chown -R root:wheel "$SPLUNK_HOME" || die "Could not set ownership on $SPLUNK_HOME"
}

start_splunk() {
    [ -x "$SPLUNK_HOME/bin/splunk" ] || die "Splunk CLI not found after upgrade: $SPLUNK_HOME/bin/splunk"

    log_info "Starting Splunk UF"
    "$SPLUNK_HOME/bin/splunk" start --accept-license --answer-yes --auto-ports --no-prompt \
        || die "Could not start Splunk UF after upgrade. Check $SPLUNK_HOME/var/log/splunk/splunkd.log"
}

cleanup_archives() {
    # We want to clean up our mess when we're done by removing the files from /tmp but we only want to
    # remove them after Splunk has successfully started from the upgraded files.
    log_info "Removing staged Splunk UF archives from $STAGING_DIR"
    rm -f "$STAGING_DIR"/$ARM_SPLUNK_PATTERN "$STAGING_DIR"/$INTEL_SPLUNK_PATTERN \
        || die "Could not remove staged Splunk UF archive files from $STAGING_DIR"
}

verify_splunk_status() {
    log_info "Verifying Splunk UF status"
    STATUS_OUTPUT=$("$SPLUNK_HOME/bin/splunk" status 2>&1 || true)
    echo "$STATUS_OUTPUT"

    echo "$STATUS_OUTPUT" | grep -q "splunkd is running" \
        || die "Splunk status did not report splunkd running."
}

# Now that we've defined all of our functions, we'll call them in order:

main() {
    require_root
    require_macos
    select_architecture_archive
    detect_splunk_home
    stop_splunk
    extract_upgrade
    set_permissions
    start_splunk
    verify_splunk_status
    cleanup_archives

    log_info "Splunk UF in-place upgrade completed successfully."
}

main "$@"

exit 0      ## Success
exit 1      ## Failure

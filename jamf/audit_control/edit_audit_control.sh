#!/bin/bash

# Genericization variables:
#   AUDIT_CONTROL_FILE: Target macOS audit_control path. Defaults to /etc/security/audit_control.
#   BACKUP_DIR: Directory for timestamped backups. Defaults to /var/backups/audit_control.
# Purpose: Configure macOS /etc/security/audit_control for Jamf deployment.
#
# This script preserves comments and unrelated settings in the existing
# audit_control file, replaces the required audit keys, appends any missing
# keys, and creates a timestamped backup before writing changes.

set -u

AUDIT_CONTROL_FILE="${AUDIT_CONTROL_FILE:-/etc/security/audit_control}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/audit_control}"

AWK="/usr/bin/awk"
CAT="/bin/cat"
CHMOD="/bin/chmod"
CHOWN="/usr/sbin/chown"
CMP="/usr/bin/cmp"
CP="/bin/cp"
DATE="/bin/date"
ID="/usr/bin/id"
MKDIR="/bin/mkdir"
MKTEMP="/usr/bin/mktemp"
MV="/bin/mv"
RM="/bin/rm"

# Required /etc/security/audit_control settings.
DESIRED_DIR="dir:/var/audit/"
DESIRED_FLAGS="flags:lo,aa,ad,ex,pc,fc,fd,+fm,-fr,-fw,nt"
DESIRED_MINFREE="minfree:5"
DESIRED_NAFLAGS="naflags:lo,aa"
DESIRED_POLICY="policy:cnt,argv,arge"
DESIRED_FILESZ="filesz:10M"
DESIRED_EXPIRE_AFTER="expire-after:60d OR 10G"

log() {
  echo "audit_control: $*"
}

fail() {
  echo "audit_control: ERROR: $*" >&2
  exit 1
}

cleanup() {
  if [ -n "${TEMP_FILE:-}" ] && [ -f "$TEMP_FILE" ]; then
    "$RM" -f "$TEMP_FILE"
  fi
}
trap cleanup EXIT

if [ "$("$ID" -u)" -ne 0 ]; then
  fail "This script must run as root. Jamf policies normally run scripts as root."
fi

if [ ! -f "$AUDIT_CONTROL_FILE" ]; then
  fail "Audit control file not found: $AUDIT_CONTROL_FILE"
fi

if [ ! -r "$AUDIT_CONTROL_FILE" ]; then
  fail "Audit control file is not readable: $AUDIT_CONTROL_FILE"
fi

AUDIT_CONTROL_DIR="${AUDIT_CONTROL_FILE%/*}"
TIMESTAMP="$("$DATE" +%Y%m%d%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/audit_control.$TIMESTAMP.bak"
TEMP_FILE="$("$MKTEMP" "$AUDIT_CONTROL_DIR/audit_control.XXXXXX")" || fail "Unable to create temporary file."

"$MKDIR" -p "$BACKUP_DIR" || fail "Unable to create backup directory: $BACKUP_DIR"
"$CHMOD" 700 "$BACKUP_DIR" || fail "Unable to set backup directory permissions: $BACKUP_DIR"
"$CP" -p "$AUDIT_CONTROL_FILE" "$BACKUP_FILE" || fail "Unable to back up $AUDIT_CONTROL_FILE"

log "Created backup: $BACKUP_FILE"

# Replace required keys when present and append missing keys at end of file.
# Matching is anchored to the key name and colon, so commented examples are left untouched.
"$AWK" \
  -v desired_dir="$DESIRED_DIR" \
  -v desired_flags="$DESIRED_FLAGS" \
  -v desired_minfree="$DESIRED_MINFREE" \
  -v desired_naflags="$DESIRED_NAFLAGS" \
  -v desired_policy="$DESIRED_POLICY" \
  -v desired_filesz="$DESIRED_FILESZ" \
  -v desired_expire_after="$DESIRED_EXPIRE_AFTER" \
  '
    BEGIN {
      desired["dir"] = desired_dir
      desired["flags"] = desired_flags
      desired["minfree"] = desired_minfree
      desired["naflags"] = desired_naflags
      desired["policy"] = desired_policy
      desired["filesz"] = desired_filesz
      desired["expire-after"] = desired_expire_after

      order[1] = "dir"
      order[2] = "flags"
      order[3] = "minfree"
      order[4] = "naflags"
      order[5] = "policy"
      order[6] = "filesz"
      order[7] = "expire-after"
    }

    /^[[:space:]]*[A-Za-z0-9_-]+[[:space:]]*:/ {
      key = $0
      sub(/^[[:space:]]*/, "", key)
      sub(/[[:space:]]*:.*/, "", key)

      if (key in desired) {
        print desired[key]
        seen[key] = 1
        next
      }
    }

    { print }

    END {
      for (i = 1; i <= 7; i++) {
        key = order[i]
        if (!(key in seen)) {
          print desired[key]
        }
      }
    }
  ' "$AUDIT_CONTROL_FILE" > "$TEMP_FILE" || fail "Unable to generate updated audit_control file."

"$CHOWN" root:wheel "$TEMP_FILE" || fail "Unable to set owner on temporary file."
"$CHMOD" 644 "$TEMP_FILE" || fail "Unable to set permissions on temporary file."

if "$CMP" -s "$AUDIT_CONTROL_FILE" "$TEMP_FILE"; then
  log "No changes required. Current audit_control already matches desired settings."
  exit 0
fi

"$MV" "$TEMP_FILE" "$AUDIT_CONTROL_FILE" || fail "Unable to replace $AUDIT_CONTROL_FILE"
TEMP_FILE=""

log "Updated $AUDIT_CONTROL_FILE"

# Validate the required values after the file has been written.
for required_line in \
  "$DESIRED_DIR" \
  "$DESIRED_FLAGS" \
  "$DESIRED_MINFREE" \
  "$DESIRED_NAFLAGS" \
  "$DESIRED_POLICY" \
  "$DESIRED_FILESZ" \
  "$DESIRED_EXPIRE_AFTER"; do
  if ! "$AWK" -v line="$required_line" '$0 == line { found = 1 } END { exit found ? 0 : 1 }' "$AUDIT_CONTROL_FILE"; then
    fail "Validation failed. Missing expected line: $required_line"
  fi
done

log "Validation passed. Required audit_control settings are present."

# Ask auditd to reload configuration when the audit command exists.
# The command can return non-zero on systems where audit is disabled or restricted,
# so this is logged as a warning instead of failing the whole Jamf policy.
if [ -x /usr/sbin/audit ]; then
  if /usr/sbin/audit -s; then
    log "Requested audit subsystem configuration reload with /usr/sbin/audit -s."
  else
    log "Warning: /usr/sbin/audit -s returned non-zero. Changes remain written to disk."
  fi
else
  log "Warning: /usr/sbin/audit not found. Changes remain written to disk."
fi

exit 0

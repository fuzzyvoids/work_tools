# Audit Control Jamf Script

## Purpose

`edit_audit_control.sh` configures the macOS audit subsystem control file at `/etc/security/audit_control` for Jamf deployment.

The script preserves comments and unrelated settings in the existing file, updates the required audit keys, appends missing required keys, and creates a timestamped backup before replacing the file.

## Required Settings

After the script runs, `/etc/security/audit_control` will contain these exact settings:

```text
dir:/var/audit/
flags:lo,aa,ad,ex,pc,fc,fd,+fm,-fr,-fw,nt
minfree:5
naflags:lo,aa
policy:cnt,argv,arge
filesz:10M
expire-after:60d OR 10G
```

## Files

- `edit_audit_control.sh`: Jamf deployment script.
- `README.md`: Operational notes and validation guidance.

## Behavior

The script performs the following steps:

1. Verifies it is running as root.
2. Verifies `/etc/security/audit_control` exists and is readable.
3. Creates a backup in `/var/backups/audit_control/`.
4. Replaces these keys if they already exist: `dir`, `flags`, `minfree`, `naflags`, `policy`, `filesz`, and `expire-after`.
5. Appends any required key that is missing.
6. Preserves comments and unrelated settings.
7. Validates that the required settings are present after writing.
8. Runs `/usr/sbin/audit -s` when available to request an audit subsystem configuration reload.

## Jamf Deployment

Upload `edit_audit_control.sh` to Jamf Pro as a script and run it from a policy scoped to the intended macOS computers.

Jamf policies normally execute scripts as root. If the script is run manually, use `sudo`.

```bash
sudo ./edit_audit_control.sh
```

## Backup Location

Backups are written to:

```text
/var/backups/audit_control/audit_control.YYYYMMDDHHMMSS.bak
```

The backup directory is created with `700` permissions.

## Testing Without Modifying System Audit Configuration

The script supports environment variables for safe local testing:

```bash
mkdir -p /tmp/audit-control-test
cp /etc/security/audit_control /tmp/audit-control-test/audit_control

sudo AUDIT_CONTROL_FILE=/tmp/audit-control-test/audit_control \
  BACKUP_DIR=/tmp/audit-control-test/backups \
  ./edit_audit_control.sh

cat /tmp/audit-control-test/audit_control
```

This test path validates the file modification logic without writing to `/etc/security/audit_control`.

## Expected Jamf Result

A successful run exits with status `0` and logs messages similar to:

```text
audit_control: Created backup: /var/backups/audit_control/audit_control.20260806120000.bak
audit_control: Updated /etc/security/audit_control
audit_control: Validation passed. Required audit_control settings are present.
audit_control: Requested audit subsystem configuration reload with /usr/sbin/audit -s.
```

If `/usr/sbin/audit -s` returns non-zero, the script logs a warning but does not fail the Jamf policy after the file has been written and validated. This avoids reporting a failed deployment when the target file was updated successfully but the audit reload command was restricted or unavailable.

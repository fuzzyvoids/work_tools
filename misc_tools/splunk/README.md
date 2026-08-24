# Splunk Universal Forwarder macOS Upgrade Package

This directory contains files used to build a macOS `.pkg` that performs an in-place upgrade of an existing Splunk Universal Forwarder (UF) installation.

The package flow is based on Splunk's documented remote upgrade pattern, but adapted for local execution as a macOS package `postinstall` script instead of an SSH-based remote script (Splunk Universal Forwarder upgrade documentation, 10.4).

## Files

| File | Purpose |
| --- | --- |
| `remote_upgrade.sh` | Splunk-provided remote upgrade template. This is reference material only. |
| `postinstall.sh` | macOS package postinstall script used by the upgrade `.pkg`. |

## Intended Use

Use `postinstall.sh` as the package script for a macOS `.pkg` that stages two Splunk UF tarballs in `/tmp`:

- One Apple Silicon archive matching `splunkforwarder-*-darwin-arm64.tgz`
- One Intel archive matching `splunkforwarder-*-darwin-intel.tgz`

The script detects the local CPU architecture with `uname -m`, selects the correct staged archive, upgrades the existing UF installation in place, starts the forwarder, verifies that `splunkd` is running, and then removes both staged tarballs from `/tmp`.

## Package Payload Requirements

The `.pkg` payload must install both Splunk UF archives under `/tmp`. In macOS package payload paths, this usually appears as `/private/tmp`, which resolves to the same location as `/tmp`.

Example payload paths:

```text
/private/tmp/splunkforwarder-10.4.2-33c3bf42cd73-darwin-arm64.tgz
/private/tmp/splunkforwarder-10.2.7-c0bff5b0fac3-darwin-intel.tgz
```

Avoid staging multiple matching versions for the same architecture. The script intentionally fails if more than one matching archive is present because choosing arbitrarily could install the wrong version.

## Archive Matching

The matching patterns are defined near the top of `postinstall.sh`:

```sh
ARM_SPLUNK_PATTERN="splunkforwarder-*-darwin-arm64.tgz"
INTEL_SPLUNK_PATTERN="splunkforwarder-*-darwin-intel.tgz"
```

These patterns are version-agnostic. When the package is rebuilt for a newer Splunk UF release, the script should not require edits as long as Splunk keeps the same naming structure.

## Install Path Detection

The script checks for existing UF installations in this order:

1. `/opt/splunkforwarder`
2. `/Applications/SplunkForwarder`
3. `/Applications/SplunkForwarder/bin/Splunk.app`

If none of those paths exist, the script defaults to `/opt/splunkforwarder`. This supports first-time installation, but the primary use case is in-place upgrade.

The path detection matters because some target Macs use the current `/opt/splunkforwarder` path while older installations may still live under `/Applications/SplunkForwarder`.

## What the Script Does

At a high level, `postinstall.sh` performs these actions:

1. Confirms it is running as root.
2. Confirms the operating system is macOS.
3. Selects the correct Splunk UF tarball for the local architecture.
4. Detects the active Splunk UF install path.
5. Stops the currently running forwarder using the Splunk CLI when possible.
6. Extracts or merges the selected archive into the active install path.
7. Sets ownership to `root:wheel` on the UF installation directory.
8. Starts Splunk with unattended license acceptance flags.
9. Runs `splunk status` and requires `splunkd is running` in the output.
10. Removes both staged UF tarballs from `/tmp`.

The script does not set or overwrite deployment-client configuration. This is intentional so existing client-side configuration is preserved.

## Build Notes for Jamf Composer

When building the package in Jamf Composer:

1. Add both architecture-specific UF tarballs to `/tmp` in the package payload.
2. Add `postinstall.sh` as the package `postinstall` script.
3. Confirm the script remains executable, typically mode `755`.
4. Build the package with install location `/`.
5. Sign the package before production deployment.

Before building, check the payload for AppleDouble metadata files such as `._splunkforwarder-...tgz`. They are not used by this script and should generally be removed from the package payload if Composer captured them.

## Local Validation

Run these checks before embedding the script in a package:

```sh
sh -n postinstall.sh
shellcheck postinstall.sh
ls -l postinstall.sh
```

Expected result:

- `sh -n` produces no output.
- `shellcheck` produces no findings, or only documented intentional findings.
- File mode is executable, such as `-rwxr-xr-x`.

To inspect a finished package payload before installing it:

```sh
pkgutil --payload-files /path/to/package.pkg | grep -i splunk
```

The output should show exactly one `darwin-arm64.tgz` archive and exactly one `darwin-intel.tgz` archive under `/private/tmp`.

## Installer Log Review

macOS package install logs are written to:

```text
/var/log/install.log
```

Useful searches:

```sh
grep -i splunk /var/log/install.log
grep -i postinstall /var/log/install.log
grep -i "PKInstallErrorDomain" /var/log/install.log
```

Common failure examples:

| Log message | Likely cause | Corrective action |
| --- | --- | --- |
| `Selected Splunk archive not found` | The expected architecture tarball was not staged in `/tmp`, or the filename does not match the configured pattern. | Check the package payload with `pkgutil --payload-files` and confirm the archive name matches `splunkforwarder-*-darwin-arm64.tgz` or `splunkforwarder-*-darwin-intel.tgz`. |
| `Multiple Splunk archives matched` | More than one matching archive exists in `/tmp` for the selected architecture. | Remove stale tarballs from the package payload or from `/tmp` before retrying. |
| `Could not determine top-level directory` | The selected tarball is missing, corrupt, or not a gzip tar archive. | Validate the archive with `tar -tzf /tmp/<archive>.tgz`. |
| `Splunk CLI not found after upgrade` | Extraction did not produce a valid UF directory at the detected install path. | Check the tarball structure and the detected install path in the installer log. |
| `Splunk status did not report splunkd running` | Splunk failed to start after extraction. | Review `${SPLUNK_HOME}/var/log/splunk/splunkd.log` and the local LaunchDaemon configuration. |

Package trust warnings, missing background images, missing readme resources, or missing license resources may appear in `install.log`. Those are package presentation or signing issues unless they prevent the install from reaching `postinstall`.

## Operational Notes

- Deploy the Full Disk Access PPPC profile before or alongside the package so `splunkd` can read protected macOS paths.
- If `splunkd` fails under `launchd` because `SPLUNK_HOME` is missing from the LaunchDaemon environment, use the existing repair helper from the installer directory: `../installer/start_splunkd_after_install_and_fix_launch_daemon.sh`.
- Test on both Apple Silicon and Intel Macs before production deployment.
- Confirm the final forwarder version after installation with `${SPLUNK_HOME}/bin/splunk version`.
- Confirm the forwarder reports to the expected deployment server after restart.

## Reference

- Splunk Universal Forwarder upgrade documentation: <https://help.splunk.com/en/splunk-enterprise/forward-and-process-data/universal-forwarder-manual/10.4/upgrade-or-uninstall-the-universal-forwarder/upgrade-the-universal-forwarder>

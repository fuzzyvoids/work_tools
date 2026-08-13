# Splunk Universal Forwarder — macOS Deployment

This documentation describes the details needed to deploy the Splunk Universal Forwarder (UF) version **10.4.0** to macOS endpoints (Apple Silicon / `arm64`), along with supporting configuration for TCC/Full Disk Access and a repair helper for the LaunchDaemon.

The work relied upon information provided by [Splunk](https://help.splunk.com/en/splunk-cloud-platform/forward-and-process-data/universal-forwarder-manual/10.2/install-the-universal-forwarder/deploying-the-universal-forwarder-to-a-macos-fleet)

## Contents

| File | Purpose |
| --- | --- |
| `splunk_uf_10.4.0_gdms.pkg` | Installer package that silently installs and configures the UF. |
| `start_splunkd_after_install_and_fix_launch_daemon.sh` | Repair script that fixes a `splunkd` startup failure caused by a missing `SPLUNK_HOME` in the LaunchDaemon. |
| `Splunk-PPPC.plist` | PPPC (Privacy Preferences Policy Control) profile granting `splunkd` Full Disk Access via TCC. |

---

## `splunk_uf_10.4.0_gdms.pkg`

A macOS flat installer package (built with Jamf Composer) that performs a silent, unattended install of the Splunk Universal Forwarder.

**Package metadata**
- Identifier: `com.splunk.universalforwarder`, version `10.4.0`
- Install location: `/` (target), runs with root authorization
- Architectures: `x86_64, arm64`
- Signature: **none** (unsigned)

**What it stages**

The payload drops files into `/var/tmp/splunk_install/`:
- `splunkforwarder-10.4.0-...-darwin-arm64.tgz` — the actual UF tarball (~79 MB)
- `deploymentclient.conf` — points the forwarder at the deployment server `10.144.27.32:8089`, with `clientName = $HOSTNAME`
- `user-seed.conf` — seeds the local `admin` account with a pre-hashed password
- `post-install-script.sh` — a standalone copy of the install logic (see note below)

**What its `postinstall` does** (runs as root)
1. Validates it is root and that the staging dir + UF tarball exist.
2. Extracts the UF tarball into `/opt` (installs to `/opt/splunkforwarder`).
3. Kills any running `splunkd`.
4. Copies the staged `.conf` files into `${SPLUNK_HOME}/etc/system/local/`.
5. `chown -R root:wheel` on the install dir.
6. Starts the forwarder with `--accept-license --no-prompt --answer-yes`.
7. Runs `splunk enable boot-start`, then relocates the generated `com.splunk*.plist` from `/Library/LaunchAgents` to `/Library/LaunchDaemons` if needed and (re)loads it via `launchctl`.
8. Removes the staging directory to clean up.

> **Note on the two scripts inside the pkg:** The *authoritative* logic is the embedded `postinstall` (in the pkg's Scripts archive), which is a hardened rewrite using a `CONF_FILES` loop and safe `tar`/`cp` handling. The staged `post-install-script.sh` is an earlier reference copy of the same steps provided by Splunk and contains several run-together lines (missing newlines/`fi`). It just gets expanded into the temp dir and then nothing happens to it, so it is effectively documentation, not what actually executes.

---

## `start_splunkd_after_install_and_fix_launch_daemon.sh`

A post-install repair script that is deployed via Jam (e.g. **not** part of the package!) that corrects a `splunkd` launch failure which occurs when the LaunchDaemon starts `splunk` without a `SPLUNK_HOME` environment variable set (because it runs under `launchd` rather than an interactive shell).

**Usage**

Designed to be run as a Jamf policy script, so `SPLUNK_HOME` is passed as **parameter 4**:

```bash
sudo ./start_splunkd_after_install_and_fix_launch_daemon.sh "" "" "" /opt/splunkforwarder
```

(Params 1–3 are the Jamf-reserved mount/computer/user args; `$4` is the intended `SPLUNK_HOME`.)

**What it does**
1. Requires root; requires `/Library/LaunchDaemons/com.splunk.plist` to exist.
2. If an `EnvironmentVariables` key is already present, it exits without changes (idempotent guard).
3. Backs up the existing plist to `/tmp/...bak.<timestamp>`.
4. Rewrites `com.splunk.plist` to include an `EnvironmentVariables` dict with `SPLUNK_HOME`, plus `ProgramArguments` (`splunk start --no-prompt --answer-yes`) and `RunAtLoad`.
5. Validates the result with `plutil -lint`; restores the backup on any failure.
6. Reloads the LaunchDaemon via `launchctl unload`/`load`.
7. Ensures `splunkd` is running (starts it if not) and verifies with `splunk status`.

---

## `Splunk-PPPC.plist`

An Apple PPPC configuration profile that pre-grants the forwarder the TCC permissions it needs so macOS does not block or prompt for protected file access.

- Service: `SystemPolicyAllFiles` (Full Disk Access), `Allowed = true`
- Target: `/opt/splunkforwarder/bin/splunkd` (matched by path)
- Code requirement: `identifier "splunkd" and anchor apple generic`
- Payload identifier: `com.company.splunk.pppc` (placeholder org prefix — update before deployment)

Deploy this via Jamf so it is delivered before or alongside the pkg.

---

## Typical Deployment Flow

1. Push `Splunk-PPPC.plist` via MDM to grant Full Disk Access.
2. Install `splunk_uf_10.4.0_gdms.pkg` (silent, configures deployment client + admin seed + boot-start).
3. If `splunkd` fails to start due to a missing `SPLUNK_HOME`, run `start_splunkd_after_install_and_fix_launch_daemon.sh` (Jamf param 4 = `/opt/splunkforwarder`).

## Security Notes

<!-- - The pkg is **unsigned**; MDM/allowlisting accounts for that but manual installation will trigger Gatekeeper -->
- It was discovered during testing that even deployment with an MDM triggered Gatekeeper. Therefore, the latest version of this package has been signed by a certificate issued by the GDMS JamfPro built-in CA
  - Cert info: `C=US,CN=RF_PackageSigningCert,E=rob.fischer@gd-ms.com` S/N `3371416570` Exp: 08/04/27
- `user-seed.conf` contains a hashed `admin` credential, and `deploymentclient.conf` hardcodes the deployment-server IP; Splunk will not need these credentials after configuration, but treat the contents of these files as sensitive to be distributed within GDMS only

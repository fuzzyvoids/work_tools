# Work Tools

## Purpose
The purpose of this repo is to collect all of the tools and scripts that I have built to carry out my work as a systems administrator and as a security engineer, and to keep them available for re-use as needed.  
No proprietary company data or sensitive information is included.
## Contents

### Ansible

- **Playbooks and inventory template** (`ansible/playbooks/`): Example entry points for applying roles to common host classes, including workstation setup, virtualization hosts, podman hosts, disk usage checks, CUI remediation, Elastic Agent deployment, and OpenSCAP collection. The included `inventory.yml` is a template only and uses placeholder hosts and documentation IP addresses.

- **Repository and package source roles** (`ansible/rocky-8-repos/`, `ansible/rocky-9-repos/`, `ansible/rhel-8-repos/`, `ansible/zabbix-repos/`, `ansible/zfs-on-linux/`, `ansible/repo-teradici/`): Roles for configuring OS and third-party package repositories from parameterized mirror locations. These are useful when systems need controlled package sources rather than direct internet repositories.

- **Workstation build roles** (`ansible/workstation/`, `ansible/rocky-workstation/`, `ansible/rhel8-workstation/`, `ansible/rocky-8-minimal-plus/`, `ansible/rocky-9-minimal-plus/`): Workstation baseline configuration, package installation, desktop policy files, Kerberos browser policy templates, printer setup placeholders, and supporting handlers. Environment-specific values are exposed as variables or placeholders.

- **Security and compliance roles** (`ansible/CUI-rl-rhel9/`, `ansible/oscap/`, `ansible/clear-old-certs/`, `ansible/gdms-ca-subscriber/`, `ansible/darknet-ca-subscriber/`): Compliance-focused automation, OpenSCAP tailoring content, certificate trust-store management, and cleanup tasks. CA material is not included and must be supplied from the target environment.

- **Endpoint and monitoring roles** (`ansible/deploy_elastic_agent/`, `ansible/zabbix-agent-install/`, `ansible/clamd-users/`): Deployment and configuration helpers for Elastic Agent, Zabbix Agent, and ClamAV user scanning support. Tokens, enrollment URLs, mirror paths, and service endpoints are parameterized.

- **Infrastructure service roles** (`ansible/nfs-server/`, `ansible/tang-server/`, `ansible/auto-unlock-disk/`, `ansible/nbde_client_for_rocky/`, `ansible/sanoid/`, `ansible/gitlab_runner/`, `ansible/podman_common/`): Roles for common Linux infrastructure services, including NFS, Tang/NBDE disk unlock, snapshot scheduling, GitLab Runner, and Podman registry configuration.

- **Virtualization, PCoIP, and engineering-tool roles** (`ansible/virt-servers/`, `ansible/pcoip-agent/`, `ansible/pcoip-check/`, `ansible/rocky-pcoipag-common/`, `ansible/rocky-pcoipag-standard/`, `ansible/teradici-license-server/`, `ansible/xilinx_fips/`, `ansible/xilinx-jtagger/`, `ansible/olimex-jtagger/`, `ansible/vh0101-mount-tools/`): Automation for virtualization hosts, PCoIP agents and license checks, engineering-tool path handling, and JTAG-related setup. License servers, shared tool paths, and site-specific paths are variables.

### CrowdStrike

- **Falcon API Python tools** (`crowdstrike/python/`): Scripts for host lookup, host tagging, new-host reporting, USB Device Control policy inspection, recent block analysis, and policy exception workflows. API credentials, tenant URLs, local API profile files, tag names, site mappings, and NGSIEM repositories are supplied through CLI flags, environment variables, or local configuration files.

- **RTR and removal scripts** (`crowdstrike/shell/`): Shell, PowerShell, and zsh scripts intended for CrowdStrike Real Time Response or local administrative use. These focus on removing specific developer tooling footprints from macOS, Linux, and WSL contexts.

### Jamf And macOS Management

- **Jamf extension attributes** (`jamf/extension-attributes/`): macOS inventory scripts for reporting application versions, security settings, account state, system extensions, Homebrew state, Wi-Fi details, Time Machine status, and similar Jamf Pro inventory data.

- **Jamf policy scripts** (`jamf/scripts/`): Reusable macOS administration scripts for account type conversion, domain unbind, software update controls, APFS volume management, printer cleanup, SSH key deployment, application permission correction, browser and mail defaults, and related Jamf policy tasks.

- **Script templates** (`jamf/scripts/script-templates/`): Generic uninstaller template scripts and examples for common application removal workflows. These are designed to be adapted with Jamf script parameters rather than hard-coded deployment data.

- **Configuration profiles and plists** (`jamf/plists/`): Parameterized Jamf Connect and macOS configuration profile examples. Identity provider hostnames, help URLs, password-change URLs, admin groups, and related tenant values are placeholders.

- **Network and audit helpers** (`jamf/prevent-multi-homing*`, `jamf/audit_control/`): Scripts for managing Wi-Fi/Ethernet multi-homing behavior and macOS audit configuration. Local state paths and target files are configurable.

### Miscellaneous Tools

- **Splunk Universal Forwarder macOS support** (`misc_tools/splunk/macOS/`): Auditd input examples, a package postinstall script, PPPC profile example, and a launch daemon repair helper for Splunk Universal Forwarder deployment. Deployment server addresses, staged configuration files, and package contents are expected to be supplied externally.

- **Zscaler install parameters** (`misc_tools/zscaler/`): XML, plist, and mobileconfig examples for Zscaler client installation parameters. Cloud name, device token, and policy token values are placeholders intended for templating before deployment.

### References

- Various text files (markdown, rich-text, html) that I have found useful to keep handy for quick-and-handy reference

### Repository Notes

- These files contain many parameters and placeholders, to avoid the inclusion of private or proprietary information.
- Accordingly, be **very** deliberate about reading these files and their surrounding and included documentation and *replacing or setting all variables* as appropriate.
- These files may not all be in a finished, production-ready state. This is a working repository, so always review and test before putting any of this into production

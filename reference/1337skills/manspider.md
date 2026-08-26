# ManSpider intermediate

ManSpider is a powerful SMB share enumeration and content-searching tool that crawls network shares in Active Directory environments to locate sensitive data, credentials, and misconfigurations. It combines aggressive file discovery with regex-based content analysis to extract passwords, API keys, connection strings, and other secrets from accessible shares.

## Installation

### Pip Install

```bash
pip install man-spider
```

### From GitHub

```bash
git clone https://github.com/blacklanternsecurity/MANSPIDER
cd MANSPIDER
pip install -r requirements.txt
python -m manspider --help
```

### Docker

```bash
docker pull blacklanternsecurity/manspider
docker run -it blacklanternsecurity/manspider manspider --help
docker run -it -v /tmp/loot:/tmp/loot blacklanternsecurity/manspider manspider TARGET -u user -p pass -o /tmp/loot
```

## Quick Start

### Basic Share Enumeration and Search

```bash
# Search for files containing "password" across all accessible shares
manspider 192.168.1.100 -u administrator -p 'P@ssw0rd!' -c "password"

# Search multiple targets with regex pattern
manspider 192.168.1.0/24 -u domain\\user -p pass -c "API_KEY|api_key|apikey"

# Search by file extension
manspider 192.168.1.50 -u user -p pass -e docx xlsx pdf

# Combine content search with extension filtering
manspider 10.0.0.0/24 -u user -p pass -c "username.*password" -e conf txt ini
```

## Authentication

### Username and Password

```bash
manspider TARGET -u username -p 'password'
```

### Domain Authentication

```bash
# Format: domain\username
manspider TARGET -u 'COMPANY\Administrator' -p 'P@ss123!'

# Explicit domain flag
manspider TARGET -d COMPANY -u Administrator -p 'P@ss123!'
```

### NTLM Hash Authentication

```bash
# Pass-the-hash style authentication (LM:NT format)
manspider TARGET -u Administrator -H 'aad3b435b51404eeaad3b435b51404ee:5f4dcc3b5aa765d61d8327deb882cf99'

# Null hash
manspider TARGET -u Administrator -H 'aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee'
```

### Anonymous Access

```bash
# Attempt to list shares without authentication
manspider TARGET -u '' -p ''
```

## Target Specification

### Single Host

```bash
manspider 192.168.1.100 -u user -p pass
manspider hostname.domain.local -u user -p pass
```

### CIDR Range

```bash
# Scan entire subnet
manspider 192.168.1.0/24 -u user -p pass

# Scan larger ranges (use with caution)
manspider 10.0.0.0/16 -u user -p pass -t 50
```

### Multiple Targets from File

```bash
# Create targets.txt with one target per line
manspider -l targets.txt -u user -p pass

# Targets file format:
# 192.168.1.100
# 192.168.1.101
# server.domain.local
```

## Content Search

### Basic Regex Content Search

```bash
# Search within file contents for patterns
manspider TARGET -u user -p pass -c "password"

# Case-insensitive search
manspider TARGET -u user -p pass -c "(?i)password"

# Search for multiple patterns (OR logic)
manspider TARGET -u user -p pass -c "password|passwd|pwd|secret"
```

### Complex Regex Patterns

```bash
# Search for connection strings
manspider TARGET -u user -p pass -c "Server=.*User ID=.*Password"

# Find database credentials
manspider TARGET -u user -p pass -c "(user|username|uid|login)\s*[:=]\s*\w+"

# Search for AWS keys
manspider TARGET -u user -p pass -c "AKIA[0-9A-Z]{16}"

# Find private keys
manspider TARGET -u user -p pass -c "BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY"
```

### Extension Filtering with Content Search

```bash
# Search only in configuration files
manspider TARGET -u user -p pass -c "password" -e conf ini xml

# Search in documents and configs
manspider TARGET -u user -p pass -c "api_key|secret" -e docx xlsx pdf conf ini

# Search in scripts
manspider TARGET -u user -p pass -c "password|token" -e ps1 sh bat vbs
```

## File Type Support

ManSpider can parse and search inside the following file types:

| File Type | Extensions | Searchable |
| --- | --- | --- |
| Microsoft Word | .docx | Yes |
| Microsoft Excel | .xlsx | Yes |
| PDF Documents | .pdf | Yes |
| Text Files | .txt | Yes |
| Configuration Files | .conf, .config | Yes |
| XML Files | .xml | Yes |
| INI Files | .ini | Yes |
| PowerShell Scripts | .ps1 | Yes |
| Shell Scripts | .sh, .bash | Yes |
| Batch Scripts | .bat, .cmd | Yes |
| VBScript | .vbs | Yes |
| Python Scripts | .py | Yes |
| Java | .jar, .java | Yes |

## Extension Filtering

### Target Specific Extensions

```bash
# Single extension
manspider TARGET -u user -p pass -e docx

# Multiple extensions
manspider TARGET -u user -p pass -e docx xlsx pdf

# Common credential-containing extensions
manspider TARGET -u user -p pass -e conf ini xml txt ps1 bat

# Development files
manspider TARGET -u user -p pass -e py java js yml yaml json
```

### Exclude Extensions

```bash
# Skip certain file types to speed up enumeration
manspider TARGET -u user -p pass --exclude-extensions exe dll sys msi iso
```

## Share Filtering

### Target Specific Shares

```bash
# Search only in specified shares
manspider TARGET -u user -p pass --shares "C$" "ADMIN$"

# Include common data shares
manspider TARGET -u user -p pass --shares "Documents" "Data" "Shared"

# Search only SYSVOL (domain policy scripts)
manspider TARGET -d DOMAIN -u user -p pass --shares "SYSVOL"
```

### Exclude Shares

```bash
# Skip noisy or irrelevant shares
manspider TARGET -u user -p pass --exclude-shares "PRINT$" "IPC$" "ADMIN$"

# Exclude multiple shares
manspider TARGET -u user -p pass --exclude-shares "Backup" "Archive" "Old"
```

## Size and Depth

### Maximum File Size

```bash
# Limit to files under 10MB
manspider TARGET -u user -p pass -s 10

# Smaller limit for faster scanning
manspider TARGET -u user -p pass -s 5

# Large limit for comprehensive search
manspider TARGET -u user -p pass -s 100
```

### Directory Depth

```bash
# Limit recursion depth (reduce runtime)
manspider TARGET -u user -p pass --maxdepth 5

# Search only top-level directories
manspider TARGET -u user -p pass --maxdepth 2

# Deep recursive search
manspider TARGET -u user -p pass --maxdepth 20
```

## Output

### Save Loot to Directory

```bash
# Specify output directory for found files
manspider TARGET -u user -p pass -c "password" -o /tmp/loot

# Organize by target
manspider 192.168.1.0/24 -u user -p pass -c "credential" -o ./domain_loot
```

### Output Organization

```bash
# Default structure
/tmp/loot/
  192.168.1.100/
    share_name/
      folder/
        file.txt
  192.168.1.101/
    Documents/
      sensitive.docx
```

### Quiet Mode

```bash
# Suppress verbose output
manspider TARGET -u user -p pass -c "password" -q

# Quiet with file output only
manspider TARGET -u user -p pass -c "secret" -q -o results/
```

## Threading

### Parallel Share Scanning

```bash
# Single-threaded (slower, less resource usage)
manspider TARGET -u user -p pass -t 1

# Default threading
manspider TARGET -u user -p pass -t 10

# Aggressive scanning (use carefully on networks)
manspider TARGET -u user -p pass -t 50

# Multiple targets with high thread count
manspider 192.168.1.0/24 -u user -p pass -t 20
```

## Common Search Patterns

### Passwords and Credentials

```bash
# Generic password search
manspider TARGET -u user -p pass -c "password|passwd|pwd"

# Username and password patterns
manspider TARGET -u user -p pass -c "(user|username|login)\s*[:=]\s*\w+.*password"

# Default credentials
manspider TARGET -u user -p pass -c "admin|root|test.*password"
```

### API Keys and Tokens

```bash
# AWS API Keys
manspider TARGET -u user -p pass -c "AKIA[0-9A-Z]{16}|aws_secret_access_key"

# Generic API key patterns
manspider TARGET -u user -p pass -c "api_key|apikey|api-key|secret_token"

# Authentication tokens
manspider TARGET -u user -p pass -c "Authorization.*Bearer|token.*Bearer"
```

### Connection Strings

```bash
# SQL Server connections
manspider TARGET -u user -p pass -c "Server=.*User ID=.*Password=|Data Source=.*Integrated Security"

# Database URIs
manspider TARGET -u user -p pass -c "mongodb://|mysql://|postgresql://"

# Connection strings
manspider TARGET -u user -p pass -c "connection.*string|ConnectionString"
```

### Sensitive Data Patterns

```bash
# Social Security Numbers
manspider TARGET -u user -p pass -c "\d{3}-\d{2}-\d{4}"

# Credit card numbers
manspider TARGET -u user -p pass -c "\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"

# Private keys
manspider TARGET -u user -p pass -c "BEGIN.*PRIVATE KEY|BEGIN.*RSA KEY"
```

## Troubleshooting

### Authentication Failures

```bash
# Verify credentials are correct
manspider TARGET -u user -p pass --list-shares

# Test with explicit domain
manspider TARGET -d COMPANY.LOCAL -u Administrator -p 'Pass123!'

# Check SMB port connectivity
nc -zv TARGET 445
```

### No Shares Found

```bash
# Ensure SMB is enabled and accessible
smbclient -L TARGET -U user%pass

# Try with explicit anonymous
manspider TARGET -u '' -p ''

# Check firewall blocking port 445
```

### Timeout Issues

```bash
# Reduce thread count for unstable networks
manspider TARGET -u user -p pass -t 5

# Increase timeout (if supported)
manspider TARGET -u user -p pass --timeout 30

# Limit directory depth to speed up
manspider TARGET -u user -p pass --maxdepth 3
```

### Performance Optimization

```bash
# Exclude large file types
manspider TARGET -u user -p pass --exclude-extensions exe dll iso bin

# Use smaller file size limit
manspider TARGET -u user -p pass -s 5

# Target specific shares only
manspider TARGET -u user -p pass --shares "Documents" "Data"
```

## Best Practices

### Operational Security

- Always obtain proper authorization before running ManSpider

- Run scans during approved testing windows to minimize detection

- Use VPN or trusted network paths for authentication traffic

- Clear output directories and logs after engagement completion

- Use sleep/jitter if available to avoid triggering rate limits

### Efficient Enumeration

- Start with targeted shares (Documents, Data, Shared) before full scan

- Use specific regex patterns rather than broad searches

- Combine extension and content filters to reduce results

- Test patterns on single targets before full subnet scans

- Review noise in results and refine regex patterns

### Pattern Selection

- Start simple (password, credentials) before complex patterns

- Test regex locally before deploying at scale

- Use case-insensitive matching for flexibility

- Validate patterns don't return excessive false positives

- Document custom patterns for team use

### Post-Exploitation

- Prioritize files containing plaintext credentials

- Cross-reference credentials across multiple shares

- Check for hardcoded domain admin accounts

- Review configuration files for service account usage

- Document all findings with source share path

## Related Tools

| Tool | Purpose |
| --- | --- |
| Snaffler | .NET share enumeration with advanced filtering |
| CrackMapExec | Credential validation and lateral movement |
| spider_plus | CrackMapExec module for share spidering |
| smbmap | SMB enumeration and share mapping |
| ShareFinder | Find writable shares across networks |
| BloodHound | AD relationship and attack path analysis |

Source: https://1337skills.com/cheatsheets/manspider/

# DNSRecon intermediate

## Installation

```bash
# Clone the repository
git clone https://github.com/darkoperator/dnsrecon.git
cd dnsrecon

# Install Python dependencies
pip install -r requirements.txt

# Make executable
chmod +x dnsrecon.py

# Run directly
python3 dnsrecon.py -h
```

## Basic Enumeration

### Standard DNS Enumeration

```bash
# Basic domain enumeration (A, AAAA, MX, NS, SOA records)
dnsrecon -d example.com -t std

# Verbose output
dnsrecon -d example.com -t std -v

# Save results to file
dnsrecon -d example.com -t std -o results.txt

# JSON output
dnsrecon -d example.com -t std -o results.json -f json
```

### Quick Reconnaissance

```bash
# All DNS records for a domain
dnsrecon -d example.com

# Target specific nameserver
dnsrecon -d example.com -n 8.8.8.8

# Use TOR
dnsrecon -d example.com --proxies 127.0.0.1:9050
```

## Enumeration Types

### Standard Records (std)

```bash
# Enumerate A, AAAA, MX, NS, SOA, TXT records
dnsrecon -d example.com -t std

# Shows DNS infrastructure details
# Output: IP addresses, mail servers, name servers, SOA info
```

### Brute Force Subdomains (brt)

```bash
# Brute force common subdomains (default wordlist)
dnsrecon -d example.com -t brt

# Custom wordlist
dnsrecon -d example.com -t brt -D /path/to/wordlist.txt

# Large wordlist for aggressive scanning
dnsrecon -d example.com -t brt -D /usr/share/wordlists/subdomains-top1million-5000.txt

# Multi-threaded brute force (faster)
dnsrecon -d example.com -t brt --threads 100
```

### Reverse Lookup (rvl)

```bash
# Reverse DNS lookup on IP range
dnsrecon -d example.com -t rvl -r 192.168.1.0/24

# Single IP reverse lookup
dnsrecon -d example.com -t rvl -r 192.168.1.5

# Larger range
dnsrecon -d example.com -t rvl -r 10.0.0.0/16
```

### Zone Transfer (axfr)

```bash
# Attempt zone transfer (very informative if successful)
dnsrecon -d example.com -t axfr

# Target specific nameserver for zone transfer
dnsrecon -d example.com -t axfr -n ns1.example.com

# Zone transfer attempt via nsupdate
dnsrecon -d example.com -t axfr --ns-server 1.1.1.1
```

### SRV Records (srv)

```bash
# Enumerate SRV records
dnsrecon -d example.com -t srv

# SRV records reveal internal services
# Common: _kerberos, _ldap, _smtp, _http, _xmpp
```

### Cache Snooping (snoop)

```bash
# Test for DNS cache snooping vulnerability
dnsrecon -d example.com -t snoop

# Snoop specific nameserver
dnsrecon -d example.com -t snoop -n 192.168.1.1

# Reveal cached queries on resolver
```

### DNSSEC Zone Walk (zonewalk)

```bash
# Walk DNSSEC-signed zones
dnsrecon -d example.com -t zonewalk

# Extract all DNS records via NSEC traversal
# Only works on DNSSEC-enabled domains
```

### TLD Enumeration (tld)

```bash
# Find TLDs where domain exists
dnsrecon -d example -t tld

# Searches .com, .net, .org, etc. for variations
# Useful for typosquatting reconnaissance
```

## Zone Transfer Attempts

```bash
# Standard zone transfer
dnsrecon -d example.com -t axfr

# Against all nameservers
dnsrecon -d example.com -t axfr -a

# Verbose zone transfer results
dnsrecon -d example.com -t axfr -v

# Using custom nameserver
dnsrecon -d example.com -t axfr -n 10.0.0.1

# Check if zone transfer is allowed (common misconfiguration)
dig @ns1.example.com example.com axfr
```

## Subdomain Brute Forcing

### Basic Brute Force

```bash
# Default wordlist
dnsrecon -d example.com -t brt

# Show only found subdomains
dnsrecon -d example.com -t brt | grep -i 'found'
```

### Custom Wordlists

```bash
# Use specific wordlist
dnsrecon -d example.com -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Combine multiple wordlists
cat wordlist1.txt wordlist2.txt > combined.txt
dnsrecon -d example.com -t brt -D combined.txt

# Generate custom wordlist from online sources
dnsrecon -d example.com -t brt -D /path/to/common-subdomains.txt
```

### Performance Tuning

```bash
# Increase thread count
dnsrecon -d example.com -t brt --threads 150

# Reduce thread count for stability
dnsrecon -d example.com -t brt --threads 10

# Add delays between requests (stealth)
dnsrecon -d example.com -t brt --delay 1
```

### Filter Results

```bash
# Save all results
dnsrecon -d example.com -t brt -o brute_force.txt

# Filter for only resolved subdomains
dnsrecon -d example.com -t brt | grep -E '^\[.*\]' | grep -v 'NXDOMAIN'
```

## Reverse Lookup Ranges

```bash
# Single IP reverse lookup
dnsrecon -d example.com -t rvl -r 192.168.1.100

# Subnet range (/24)
dnsrecon -d example.com -t rvl -r 192.168.1.0/24

# Larger range (/16)
dnsrecon -d example.com -t rvl -r 10.0.0.0/16

# Classless range
dnsrecon -d example.com -t rvl -r 203.0.113.0-203.0.113.255

# Against specific nameserver
dnsrecon -d example.com -t rvl -r 10.0.0.0/24 -n 192.168.1.1
```

## SRV Record Enumeration

```bash
# Enumerate all SRV records
dnsrecon -d example.com -t srv

# SRV record lookup reveals internal services
# Common SRV records:
# _kerberos._tcp.example.com (Kerberos authentication)
# _ldap._tcp.example.com (LDAP directory)
# _xmpp._tcp.example.com (XMPP messaging)
# _sip._tcp.example.com (VoIP)
# _smtp._tcp.example.com (Mail submission)
```

## DNS Cache Snooping

```bash
# Test cache snooping
dnsrecon -d example.com -t snoop

# Against specific resolver
dnsrecon -d example.com -t snoop -n 8.8.8.8

# Reveals what queries have been cached
# Indicates interest in specific domains/records

# Manual cache snooping with dig
dig @resolver.example.com example.com +norecurse

# Non-recursive query reveals cache status
```

## Google Dorks Integration

```bash
# Google dorks can supplement DNSRecon findings
# site:example.com (find indexed subdomains)
# site:example.com inurl:admin (find admin panels)
# site:example.com filetype:pdf (find documents)

# Combine with dnsrecon results
dnsrecon -d example.com -t brt > dnsrecon_results.txt
# Then manually verify with Google dorks
```

## Output Formats

### Text Output

```bash
# Plain text (default)
dnsrecon -d example.com -t std -o results.txt

# View results
cat results.txt
```

### JSON Output

```bash
# JSON format (structured data)
dnsrecon -d example.com -t std -o results.json -f json

# Parse with jq
cat results.json | jq '.[] | .records'
```

### XML Output

```bash
# XML format (compatible with other tools)
dnsrecon -d example.com -t std -o results.xml -f xml

# Parse XML
xmllint --format results.xml
```

### CSV Output

```bash
# CSV format (spreadsheet-compatible)
dnsrecon -d example.com -t std -o results.csv -f csv

# Import into Excel/Sheets
```

### SQLite Output

```bash
# SQLite database
dnsrecon -d example.com -t std -o results.db -f sqlite

# Query the database
sqlite3 results.db "SELECT * FROM records;"

# Export specific records
sqlite3 results.db ".mode csv" ".output subdomains.csv" "SELECT * FROM records WHERE type='A';"
```

## Common Flags Reference

| Flag | Description | Example |
| --- | --- | --- |
| `-d` | Target domain | `-d example.com` |
| `-t` | Enumeration type | `-t std, brt, rvl, axfr, srv, snoop, zonewalk, tld` |
| `-r` | Reverse lookup range | `-r 192.168.1.0/24` |
| `-n` | Nameserver to use | `-n 8.8.8.8` |
| `-D` | Wordlist for brute force | `-D /path/to/wordlist.txt` |
| `-o` | Output file | `-o results.txt` |
| `-f` | Output format | `-f json, xml, csv, sqlite` |
| `-v` | Verbose output | `-v` |
| `--threads` | Thread count for brute force | `--threads 100` |
| `--delay` | Delay between requests (seconds) | `--delay 1` |
| `-a` | Perform zone transfer on all NS | `-a` |
| `--proxies` | Use proxy/TOR | `--proxies 127.0.0.1:9050` |

## Complete Enumeration Chain

```bash
# 1. Standard enumeration
dnsrecon -d example.com -t std -o example_std.txt

# 2. Attempt zone transfer
dnsrecon -d example.com -t axfr -o example_axfr.txt

# 3. Brute force subdomains
dnsrecon -d example.com -t brt -D subdomains.txt -o example_brt.json -f json

# 4. SRV records
dnsrecon -d example.com -t srv -o example_srv.txt

# 5. Reverse lookups (if you know IP range)
dnsrecon -d example.com -t rvl -r 10.0.0.0/24 -o example_rvl.txt

# 6. Export all to single file
cat example_*.txt > complete_recon.txt
```

## Tips & Tricks

- **Zone transfers** are rare but extremely valuable; always attempt

- **Brute force with large wordlists** can take time; use `--threads` for speed

- **SRV records** reveal internal infrastructure (Kerberos, LDAP, etc.)

- **Reverse lookups** identify additional hosts on same network

- **Cache snooping** shows DNS interest patterns (reconnaissance indicator)

- **Save output in multiple formats** for different analysis tools

- **Combine with other tools**: Nmap, Shodan, WHOIS, certificate transparency logs

- **Use custom wordlists** for better subdomain discovery accuracy

- **Check DNSSEC** zones with zonewalk for complete record enumeration

- **TLD enumeration** useful for finding domain variations and typosquatting

Source: https://1337skills.com/cheatsheets/dnsrecon/

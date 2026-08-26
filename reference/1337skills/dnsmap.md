# dnsmap beginner

## Overview

dnsmap is a subdomain brute-forcing tool that systematically discovers subdomains by testing common names against a target domain. It comes with a built-in wordlist and supports custom wordlists, making it useful for reconnaissance and initial network mapping. dnsmap is particularly effective for identifying infrastructure, testing naming conventions, and discovering hidden services.

The tool is simple to use and doesn't require external dependencies like DNS resolvers, making it ideal for quick initial enumeration.

## Installation

### Debian/Ubuntu

```bash
sudo apt-get update
sudo apt-get install dnsmap
```

### Kali Linux (pre-installed)

```bash
which dnsmap
dnsmap -h
```

### From source

```bash
git clone https://github.com/makefu/dnsmap.git
cd dnsmap
# Read README for specific build instructions
```

### macOS via Homebrew

```bash
brew install dnsmap
```

## Basic Usage

| Command | Description |
| --- | --- |
| `dnsmap example.com` | Brute-force subdomains on example.com |
| `dnsmap example.com -w wordlist.txt` | Use custom wordlist |
| `dnsmap example.com -r results.txt` | Save results to file |
| `dnsmap example.com -d` | Display results as you find them |

## Common Workflows

### Simple subdomain enumeration

```bash
# Quick brute-force with default wordlist
dnsmap example.com

# Brute-force with output to file
dnsmap example.com -r results.txt

# Display findings in real-time
dnsmap example.com -d
```

### Using custom wordlists

```bash
# Use SecLists subdomain wordlist
dnsmap example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Use your own wordlist
dnsmap example.com -w my_wordlist.txt

# Create wordlist from common prefixes
echo -e "www\nmail\nftp\napi\nadmin\ndev\nstaging\napi-prod\napi-staging" > custom.txt
dnsmap example.com -w custom.txt
```

### Save and filter results

```bash
# Save to file and display
dnsmap example.com -r results.txt

# Extract only valid subdomains
grep "IP address" results.txt | awk '{print $1}' > valid_subs.txt

# Count findings
grep "IP address" results.txt | wc -l
```

## Output Formats

### Standard output

```plaintext
dnsmap 0.35 - DNS Network Mapper

[+] Using built-in wordlist
[+] Brute-forcing example.com
[-] Resolving: www.example.com
[+] example.com (127.0.0.1)
[+] www.example.com (10.0.0.1)
[+] mail.example.com (10.0.0.2)
[+] api.example.com (10.0.0.3)
[+] ftp.example.com (10.0.0.4)

[+] 5 subdomains found
```

### File output format

```bash
# View saved results
cat results.txt

# Extract IP addresses
grep "IP address" results.txt
```

## Advanced Options

| Option | Usage | Description |
| --- | --- | --- |
| `-w` | `dnsmap -d example.com -w list.txt` | Specify custom wordlist file |
| `-r` | `dnsmap example.com -r output.txt` | Write results to file |
| `-d` | `dnsmap -d example.com` | Delay between requests (in milliseconds) |
| `-t` | `dnsmap example.com -t` | Ignore CNAME records |

## Wordlist Management

### Built-in wordlist

```bash
# The default wordlist is embedded in the tool
# It includes common subdomain patterns like:
# www, mail, ftp, localhost, webmail, smtp, pop, ns1, webdisk,
# admin, test, dev, staging, api, and many more

dnsmap example.com  # Uses built-in automatically
```

### Creating custom wordlists

```bash
# Common subdomain patterns
cat > subdomains.txt << EOF
www
mail
ftp
admin
api
dev
staging
test
prod
backup
database
cdn
images
static
blog
shop
checkout
payment
support
help
docs
api-prod
api-staging
api-dev
EOF

dnsmap example.com -w subdomains.txt
```

### Using SecLists

```bash
# Install SecLists if not already installed
git clone https://github.com/danielmiessler/SecLists /opt/SecLists

# Use common subdomains list
dnsmap example.com -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt

# Use all-subdomains list (slower but more comprehensive)
dnsmap example.com -w /opt/SecLists/Discovery/DNS/subdomains-top1million-110000.txt
```

## Integration with Other Tools

### Combining with nmap

```bash
# Get subdomains with dnsmap, then scan with nmap
dnsmap example.com -r subs.txt
cat subs.txt | grep "IP address" | awk '{print $NF}' > ips.txt
nmap -sV -p 80,443 -iL ips.txt
```

### Piping to other tools

```bash
# Extract subdomains and pass to httpprobe
dnsmap example.com -r results.txt
grep "IP address" results.txt | awk '{print $1}' | httpprobe

# Chain to massdns for additional validation
dnsmap example.com -r results.txt | grep "IP address" | awk '{print $1}' > candidates.txt
massdns -r resolvers.txt candidates.txt
```

### Combining with other reconnaissance tools

```bash
# Multi-tool enumeration
dnsmap example.com -r dnsmap_results.txt
assetfinder example.com > assetfinder_results.txt
amass enum -d example.com > amass_results.txt

# Combine all results
cat dnsmap_results.txt assetfinder_results.txt amass_results.txt | \
  grep -oE '[a-zA-Z0-9.-]+\.example\.com' | sort -u > all_subdomains.txt
```

## Performance Tuning

### Adjust timing for network conditions

```bash
# Default behavior
dnsmap example.com

# With custom delay (adjust as needed)
dnsmap example.com -d 100
```

### Large-scale enumeration

```bash
# Process multiple domains
for domain in example.com example.org example.net; do
  echo "[*] Enumerating $domain"
  dnsmap "$domain" -r "${domain}_results.txt"
done

# Combine all results
cat *_results.txt > combined_results.txt
```

### Parallel processing

```bash
# Using GNU Parallel (install with apt-get install parallel)
cat domains.txt | parallel dnsmap {} -r {}.txt

# Using xargs
cat domains.txt | xargs -I {} dnsmap {} -r {}.txt
```

## Real-World Scenarios

### Bug bounty reconnaissance

```bash
# Initial subdomain discovery
dnsmap target.com -r initial_subs.txt

# Use findings for further enumeration
dnsmap target.com -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -r comprehensive_subs.txt

# Extract IPs for scanning
grep "IP address" comprehensive_subs.txt | awk '{print $NF}' | sort -u > target_ips.txt
```

### Internal network mapping

```bash
# Enumerate internal domain
dnsmap internal.corp -r internal_map.txt

# Find servers by function
grep "mail\|smtp\|exchange" internal_map.txt
grep "ldap\|dc\|ad" internal_map.txt
grep "database\|db\|sql" internal_map.txt
```

### Pre-engagement reconnaissance

```bash
# Quick enumeration before engagement
dnsmap example.com -d

# Save for analysis
dnsmap example.com -r pre_engagement.txt

# Create report
echo "Subdomain Enumeration Report - $(date)" > report.txt
echo "Target: example.com" >> report.txt
echo "Tool: dnsmap" >> report.txt
echo "Findings:" >> report.txt
grep "IP address" pre_engagement.txt >> report.txt
```

## Troubleshooting

### No results found

```bash
# Verify domain is resolvable
nslookup example.com

# Try with verbose output
dnsmap -d example.com

# Check if firewall is blocking DNS queries
# Try with different DNS server (if tool supports)
```

### Slow performance

```bash
# Check network connectivity
ping -c 1 example.com

# Reduce wordlist size for faster scanning
head -100 large_wordlist.txt > small_wordlist.txt
dnsmap example.com -w small_wordlist.txt

# Consider using lightweight tool for quick scan
# Then use comprehensive wordlist later
```

### High false positive rate

```bash
# Verify results manually
nslookup mail.example.com
nslookup ftp.example.com

# Some domains may have wildcard DNS records
# Validate actual IP addresses
grep "IP address" results.txt | cut -d' ' -f5 | sort | uniq -c
```

## Comparison with Other Tools

| Tool | Speed | Accuracy | Wordlists | Features |
| --- | --- | --- | --- | --- |
| dnsmap | Fast | Good | Built-in, custom | Simple, reliable |
| Sublist3r | Medium | Good | Multiple sources | Queries multiple services |
| Amass | Slow | Excellent | Extensive | Passive reconnaissance |
| massdns | Very Fast | Good | Custom | Requires external resolver |
| Subfinder | Medium | Excellent | Passive sources | Many integrations |

## Best Practices

- Start with built-in wordlist for speed, then use comprehensive lists

- Validate findings with nslookup or dig before acting on them

- Use custom wordlists tailored to target organization

- Combine with passive reconnaissance tools for complete picture

- Document all discovered subdomains for future reference

- Be aware of wildcard DNS records that may create false positives

- Respect rate limits and target policies during enumeration

## Resources

- GitHub: [https://github.com/makefu/dnsmap](https://github.com/makefu/dnsmap)

- SecLists Subdomains: [https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS](https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS)

- DNS Tools Guide: [https://www.kali.org/tools/dnsmap/](https://www.kali.org/tools/dnsmap/)

- Subdomain Enumeration: [https://github.com/OWASP/Amass/wiki/Tutorial](https://github.com/OWASP/Amass/wiki/Tutorial)

Source: https://1337skills.com/cheatsheets/dnsmap/

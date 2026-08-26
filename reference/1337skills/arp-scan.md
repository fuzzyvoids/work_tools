# Arp-Scan intermediate

Arp-scan discovers IPv4 hosts using ARP requests on the local network. More reliable than ICMP ping as it works even with ICMP filtering.

## Installation

```bash
# Debian/Ubuntu
sudo apt install arp-scan

# Kali Linux (pre-installed)
which arp-scan

# macOS
brew install arp-scan

# Build from source
git clone https://github.com/royhills/arp-scan
cd arp-scan && autoreconf -i && ./configure && make && sudo make install
```

## Basic Scanning

| Command | Description |
| --- | --- |
| `sudo arp-scan -l` | Scan local network |
| `sudo arp-scan 192.168.1.0/24` | Scan specific subnet |
| `sudo arp-scan -r 192.168.1.1 192.168.1.254` | Scan IP range |
| `arp-scan --help` | Show help |

## Network Enumeration

```bash
# Local network scan
sudo arp-scan -l

# Specific subnet
sudo arp-scan 192.168.1.0/24

# Multiple subnets
sudo arp-scan 192.168.1.0/24 192.168.2.0/24

# IP range
sudo arp-scan -r 10.0.0.1 10.0.0.254

# Class A network
sudo arp-scan 10.0.0.0/8

# All hosts on network (can take time)
sudo arp-scan 0.0.0.0/0
```

## Output and Formatting

```bash
# Numeric output (IP and MAC)
sudo arp-scan -l

# Add vendor info (default)
sudo arp-scan -l

# Show duplicate responses
sudo arp-scan -l --duplicates

# Verbose output
sudo arp-scan -l -v

# Quiet mode (one line per host)
sudo arp-scan -l -q

# Show failed hosts
sudo arp-scan -l --show-failed

# Newline output format
sudo arp-scan -l -f
```

## Interface Selection

```bash
# Specify interface
sudo arp-scan -l -i eth0

# Scan on specific interface
sudo arp-scan 192.168.1.0/24 -i wlan0

# List available interfaces
arp-scan --interface ?

# Get interface details
ifconfig
```

## Advanced Scanning Options

```bash
# Timeout (ms)
sudo arp-scan -l -t 1000

# Maximum retries
sudo arp-scan -l -c 3

# Wait between requests (ms)
sudo arp-scan -l -o 0

# VLAN ID tagging
sudo arp-scan -l --vlan 100

# Bandwidth limiting
sudo arp-scan -l -b 100

# Number of packets
sudo arp-scan -l -N 100

# Source MAC address
sudo arp-scan -l --srcaddr 00:11:22:33:44:55

# Source IP address
sudo arp-scan -l --srcip 192.168.1.100

# Padding
sudo arp-scan -l --padding
```

## Output Processing

```bash
# Save to file
sudo arp-scan -l > arp_results.txt

# Extract IP addresses
sudo arp-scan -l | awk '{print $1}' | grep -v "^$"

# Extract MAC addresses
sudo arp-scan -l | awk '{print $2}' | grep -v "^$"

# Extract vendor info
sudo arp-scan -l | awk '{print $3}' | sort | uniq

# Count hosts
sudo arp-scan -l | grep -c "bytes"

# Find specific vendor
sudo arp-scan -l | grep Intel

# Find specific IP range
sudo arp-scan -l | grep "192.168.1"
```

## Scripting and Automation

```bash
# Scan and parse results
sudo arp-scan -l -q -f | while read ip mac vendor; do
  echo "IP: $ip - MAC: $mac - Vendor: $vendor"
done

# Feed to nmap for port scan
sudo arp-scan -l -q | awk '{print $1}' | xargs -I {} nmap {}

# Feed to other tools
sudo arp-scan -l | grep -v "^Using\|bytes" | awk '{print $1}' > live_hosts.txt
```

## Filtering and Analysis

```bash
# Remove header lines
sudo arp-scan -l | grep -v "^Using\|bytes"

# Find duplicate responses
sudo arp-scan -l --duplicates

# Extract unique vendors
sudo arp-scan -l | awk '{print $3}' | sort -u

# Count by vendor
sudo arp-scan -l | awk '{print $3}' | sort | uniq -c | sort -rn

# Identify Apple devices
sudo arp-scan -l | grep -i apple

# Identify Windows devices
sudo arp-scan -l | grep -i microsoft

# Identify Cisco devices
sudo arp-scan -l | grep -i cisco
```

## Specific Host Queries

```bash
# Scan single host
sudo arp-scan 192.168.1.100

# Check if host is alive
sudo arp-scan 192.168.1.1 -q

# Get MAC of specific IP
sudo arp-scan 192.168.1.1 | grep "192.168.1.1"

# Verify host presence
sudo arp-scan 192.168.1.1 | grep -q "192.168.1.1" && echo "Alive" || echo "Dead"
```

## Bandwidth and Performance

```bash
# Maximum bandwidth (bits/sec)
sudo arp-scan -l -b 0

# Slow scan (less network load)
sudo arp-scan -l -t 2000 -o 100

# Fast scan (more network load)
sudo arp-scan -l -t 100 -o 0

# Limited retransmissions
sudo arp-scan -l -c 1

# Single attempt only
sudo arp-scan -l -c 0
```

## Network Reconnaissance Workflow

```bash
# Step 1: Scan local network
sudo arp-scan -l > network_scan.txt

# Step 2: Extract live IPs
grep -v "^Using\|bytes" network_scan.txt | awk '{print $1}' > live_ips.txt

# Step 3: Identify by vendor
grep -i "linux\|apple\|windows\|cisco" network_scan.txt

# Step 4: Port scanning
cat live_ips.txt | xargs -I {} nmap -sV {}

# Step 5: OS detection
sudo arp-scan -l | sort
```

## Troubleshooting

```bash
# Must run as root
sudo arp-scan -l

# Check network interface
ip addr show

# Verify default gateway
route -n

# Check MTU
ip link show

# Debug mode (very verbose)
arp-scan -l -vv

# Test basic connectivity
ping -c 1 192.168.1.1
```

## Common Issues and Solutions

```bash
# "No ARP replies received" - check interface
sudo arp-scan -l -i eth0

# Timeout - increase wait time
sudo arp-scan -l -t 2000

# Too slow - reduce timeout/retries
sudo arp-scan -l -t 100 -c 1

# Network not detected - specify IP range
sudo arp-scan -r 192.168.1.1 192.168.1.254
```

---

_Last updated: March 2026_

Source: https://1337skills.com/cheatsheets/arp-scan/

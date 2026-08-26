# arping beginner

## Overview

arping is a lightweight command-line utility that sends Address Resolution Protocol (ARP) requests to discover active hosts on local networks without relying on ICMP ping. It operates at Layer 2 (data link layer) and is ideal for finding hosts that block ICMP, detecting duplicate IP addresses, and building ARP tables. Unlike traditional ping, arping doesn't require IP connectivity and can discover hosts across network segments where ICMP is blocked.

## Installation

### Linux (Debian/Ubuntu)

```bash
# Install via package manager
sudo apt-get update
sudo apt-get install -y arping

# Verify installation
arping --version
which arping
```

### Linux (RHEL/CentOS/Fedora)

```bash
# Install from repositories
sudo yum install -y iputils

# Or compile from source
sudo dnf install -y arping
```

### macOS

```bash
# Install via Homebrew
brew install arping

# Or via MacPorts
sudo port install arping

# Verify
arping --version
```

### FreeBSD/OpenBSD

```bash
# Install from ports
sudo pkg install arping

# Or from ports collection
cd /usr/ports/net-mgmt/arping
sudo make install clean
```

### Windows

```bash
# Download from official repository or:
# Use Windows Subsystem for Linux (WSL)
wsl sudo apt-get install arping

# Or use alternative tools like arp-scan on Windows
# (Note: traditional arping is Unix/Linux native)
```

### Compile from Source

```bash
# Download source
wget https://github.com/ThomasHabets/arping/releases/download/arping-2.20/arping-2.20.tar.gz

# Extract and build
tar xzf arping-2.20.tar.gz
cd arping-2.20
./configure
make
sudo make install

# Verify
arping --version
```

## Basic Syntax

```bash
# Standard arping command
arping [OPTIONS] [TARGET]

# Minimal usage (requires root)
sudo arping 192.168.1.100

# With interface specification
sudo arping -i eth0 192.168.1.100

# Help and version
arping --help
arping --version
```

## Common ARP Ping Operations

### Basic Host Discovery

```bash
# Simple ARP ping to single host
sudo arping 192.168.1.1

# Expected output:
# ARPING 192.168.1.1
# 60 bytes from 00:11:22:33:44:55 (192.168.1.1): index=0 time=2.105 msec
# Sent 1 probes (1 broadcast(s))
# Received 1 response(s)
```

### Finding MAC Addresses

| Task | Command | Purpose |
| --- | --- | --- |
| Resolve single IP | `sudo arping 192.168.1.100` | Get MAC of specific host |
| Resolve multiple IPs | `for ip in {1..10}; do sudo arping -c 1 192.168.1.$ip; done` | Scan range |
| Quiet output (MAC only) | `sudo arping -c 1 -q 192.168.1.100` | Parse-friendly format |
| Get first response | `sudo arping -f 192.168.1.100` | Stop after first reply |

### Single Host Lookup

```bash
# Simple ARP request
sudo arping 192.168.1.100

# With count limit (1 request)
sudo arping -c 1 192.168.1.100

# Get first response and exit
sudo arping -f 192.168.1.100

# Verbose output
sudo arping -v 192.168.1.100

# Quiet mode (only show MAC)
sudo arping -q 192.168.1.100
```

## Interface Selection

### Specifying Network Interfaces

```bash
# List available interfaces
ip link show
ifconfig
iwconfig

# ARP ping on specific interface
sudo arping -i eth0 192.168.1.100

# Use wireless interface
sudo arping -i wlan0 192.168.1.100

# Use specific source IP
sudo arping -i eth0 -s 192.168.1.50 192.168.1.100
```

### Interface-Based Options

| Option | Syntax | Description |
| --- | --- | --- |
| Specify interface | `-i IFACE` | `sudo arping -i eth0 TARGET` |
| Source IP | `-s IP` | `sudo arping -s 192.168.1.50 TARGET` |
| Source MAC | `-S MAC` | `sudo arping -S aa:bb:cc:dd:ee:ff TARGET` |
| Target MAC | `-t MAC` | Send to specific MAC address |

## Timeout & Count Options

### Request Count & Intervals

```bash
# Send 3 ARP requests (default = 1)
sudo arping -c 3 192.168.1.100

# Send unlimited requests until Ctrl+C
sudo arping -c 0 192.168.1.100

# Wait specific timeout
sudo arping -w 2000 192.168.1.100  # 2000 ms = 2 seconds

# Interval between packets (milliseconds)
sudo arping -p 500 192.168.1.100   # 500 ms between packets
```

### Advanced Timing

| Option | Syntax | Behavior |
| --- | --- | --- |
| Count | `-c NUM` | Send NUM requests (0 = continuous) |
| Timeout | `-w TIME` | Timeout in milliseconds |
| Interval | `-p TIME` | Wait TIME ms between requests |
| Wait for response | `-f` | Stop after first reply |

## Duplicate IP Detection

### Finding Duplicate IP Addresses

```bash
# Send ARP request and check for multiple responses
sudo arping -v 192.168.1.50

# Example output with duplicate:
# ARPING 192.168.1.50
# 60 bytes from aa:bb:cc:dd:ee:01: index=0 time=1.045 msec
# 60 bytes from aa:bb:cc:dd:ee:02: index=0 time=2.105 msec  <-- Duplicate!
# Sent 1 probes (1 broadcast(s))
# Received 2 response(s)
```

### Detecting Duplicate Detection Script

```bash
#!/bin/bash
# Check IP for duplicates
TARGET=$1
echo "Checking for duplicate IP: $TARGET"

sudo arping -c 1 -v $TARGET | grep "bytes from" | wc -l | \
  awk '{
    if ($1 > 1) print "DUPLICATE DETECTED: " $1 " hosts claim IP"
    else print "No duplicates found"
  }'
```

### Duplicate IP Troubleshooting

| Symptom | Cause | Solution |
| --- | --- | --- |
| Multiple MAC responses | Duplicate IP | Identify and reconfigure device |
| Network slowness | Duplicate IPs on LAN | Run arping scan to find conflicts |
| Intermittent connectivity | IP conflict | Use `arping -c 5` for reliability |
| DHCP errors | Duplicate prevents assignment | Check active hosts with arping |

## Gratuitous ARP

### Sending Gratuitous ARP Requests

Gratuitous ARP (unsolicited ARP reply) announces the sender's IP-MAC mapping to all hosts on network.

```bash
# Send gratuitous ARP from current host
sudo arping -U 192.168.1.100

# Gratuitous ARP with source MAC
sudo arping -U -i eth0 192.168.1.100

# Declare source IP
sudo arping -U -s 192.168.1.100 192.168.1.100
```

### Gratuitous ARP Use Cases

| Use Case | Command | Purpose |
| --- | --- | --- |
| Announce IP takeover | `sudo arping -U 192.168.1.100` | Notify network of new MAC |
| Failover notification | `sudo arping -U -i eth0 VIP_IP` | Update ARP caches after failover |
| Refresh ARP tables | `sudo arping -U TARGET` | Force update of ARP entry |
| Detect ARP spoofing | `sudo arping -U IP; arping -c 1 IP` | Verify MAC after gratuitous |

## Network Scanning & Discovery

### Scanning Local Network Ranges

```bash
# Scan entire /24 subnet
for ip in $(seq 1 254); do
  sudo arping -c 1 -q 192.168.1.$ip 2>/dev/null | \
    grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}" && echo "192.168.1.$ip found"
done

# Faster scanning with background jobs
for ip in $(seq 1 254); do
  (sudo arping -c 1 -q 192.168.1.$ip 2>/dev/null) &
done
wait
```

### Building ARP Tables

```bash
# Discover all hosts on network
sudo arping -c 1 192.168.1.255

# Export results to file
sudo arping -c 1 -q 192.168.1.0/24 > arp_discovery.txt 2>&1

# Show ARP table after discovery
arp -a
ip neigh show
```

### Subnet Scanning Script

```bash
#!/bin/bash
# Efficient ARP subnet scanner

SUBNET=${1:-192.168.1}
OUTFILE="${SUBNET//\./_}_arp_scan.txt"

echo "Scanning $SUBNET.0/24..."
echo "IP Address,MAC Address" > $OUTFILE

for i in {1..254}; do
  IP="$SUBNET.$i"
  (
    RESULT=$(sudo arping -c 1 -q $IP 2>&1 | grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}")
    if [ ! -z "$RESULT" ]; then
      echo "$IP,$RESULT" >> $OUTFILE
      echo "Found: $IP -> $RESULT"
    fi
  ) &

  # Limit concurrent jobs
  if [ $((i % 10)) -eq 0 ]; then
    wait
  fi
done
wait
echo "Scan complete: $OUTFILE"
```

## Output Modes & Parsing

### Output Format Options

```bash
# Verbose output (default)
sudo arping -v 192.168.1.100

# Quiet mode (MAC only)
sudo arping -q 192.168.1.100

# Numeric output only
sudo arping -n 192.168.1.100

# Timestamp each response
sudo arping -v -D 192.168.1.100
```

### Parsing Output

| Option | Output Style | Use Case |
| --- | --- | --- |
| Default verbose | Full details with index/time | Human readable |
| `-q` (quiet) | MAC address only | Shell scripting |
| `-n` (numeric) | Numeric only | Automated parsing |
| `-D` (timestamp) | Delta timestamps | Performance monitoring |

### Example Parsing

```bash
# Extract MAC address only
sudo arping -c 1 -q 192.168.1.100 | grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}"

# Check if host is alive (0 = found, 1 = not found)
sudo arping -c 1 -f 192.168.1.100 > /dev/null && echo "UP" || echo "DOWN"

# Parse response time
sudo arping -c 1 192.168.1.100 | grep "time=" | grep -oE "[0-9]+\.[0-9]+ msec"

# Build CSV of scan results
sudo arping -c 1 -q 192.168.1.100 | sed "s/^/192.168.1.100,/"
```

## Advanced Scripting

### ARP-Based Host Discovery

```bash
#!/bin/bash
# Find all active hosts via ARP

discover_hosts() {
  local subnet=$1
  local timeout=${2:-1000}

  echo "Host Discovery Results for $subnet.0/24:"
  echo "IP,MAC,Hostname" > hosts_found.csv

  for i in {1..254}; do
    ip="$subnet.$i"
    result=$(timeout 1 sudo arping -c 1 -q "$ip" 2>/dev/null | \
      grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}")

    if [ ! -z "$result" ]; then
      hostname=$(nslookup "$ip" 2>/dev/null | grep "name =" | awk '{print $NF}' | sed 's/.$//')
      echo "$ip,$result,$hostname" >> hosts_found.csv
      echo "OK $ip -> $result"
    fi
  done
}

discover_hosts "192.168.1"
```

### MAC Address Lookup

```bash
#!/bin/bash
# Resolve IPs to MAC and vendor

resolve_mac_vendor() {
  local ip=$1
  local mac=$(sudo arping -c 1 -q "$ip" 2>/dev/null | grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}")

  if [ ! -z "$mac" ]; then
    # Look up vendor (requires macchanger or similar)
    vendor=$(macchanger -l | grep "$(echo $mac | cut -d: -f1-3)" | cut -d' ' -f3-)
    echo "IP: $ip"
    echo "MAC: $mac"
    echo "Vendor: ${vendor:-Unknown}"
  else
    echo "Host $ip not reachable"
  fi
}

resolve_mac_vendor "192.168.1.1"
```

### Network Monitoring

```bash
#!/bin/bash
# Monitor ARP activity on network

monitor_arp() {
  echo "Monitoring ARP changes every 10 seconds..."
  PREV_FILE="/tmp/arp_prev.txt"
  CURR_FILE="/tmp/arp_curr.txt"

  cp /dev/null $PREV_FILE

  while true; do
    arp -a | sort > $CURR_FILE

    echo "=== New hosts ==="
    comm -13 $PREV_FILE $CURR_FILE

    echo "=== Removed hosts ==="
    comm -23 $PREV_FILE $CURR_FILE

    cp $CURR_FILE $PREV_FILE
    sleep 10
  done
}

monitor_arp
```

## Integration with Other Tools

### Combining with arp-scan

```bash
# arp-scan gives similar results but with vendor info
sudo arp-scan -l 192.168.1.0/24

# Use arping for specific host after arp-scan discovery
sudo arp-scan -l | grep "192.168.1.100" -A1
sudo arping 192.168.1.100
```

### Using with nmap

```bash
# ARP discovery via nmap
sudo nmap -PR 192.168.1.0/24 --open

# Combine nmap with arping for verification
sudo nmap -p- 192.168.1.100  # nmap for open ports
sudo arping 192.168.1.100    # arping to verify MAC

# Parse nmap results and arping for each
nmap -sn 192.168.1.0/24 | grep "Nmap scan" | awk '{print $NF}' | \
  while read ip; do
    mac=$(sudo arping -c 1 -q $ip | grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}")
    echo "$ip,$mac"
  done
```

### Integration with tcpdump

```bash
# Monitor ARP requests/replies while arping
sudo tcpdump -i eth0 -n "arp"

# In another terminal, send arping requests
sudo arping -v -c 5 192.168.1.100

# Capture and analyze ARP traffic
sudo tcpdump -i eth0 -n "arp" -w arp_capture.pcap
```

## Common Use Cases

### Checking Gateway Availability

```bash
# Verify default gateway is reachable (no ICMP needed)
sudo arping -c 1 -f 192.168.1.1
[ $? -eq 0 ] && echo "Gateway OK" || echo "Gateway DOWN"

# Store in script
check_gateway() {
  local gw=$(ip route | grep default | awk '{print $3}')
  sudo arping -c 1 -f $gw
  return $?
}

check_gateway && echo "Network OK" || echo "Network DOWN"
```

### Building Device Inventory

```bash
#!/bin/bash
# Create device inventory from ARP discovery

create_inventory() {
  subnet=$1
  echo "Building inventory for $subnet.0/24..."

  {
    echo "IP,MAC,First_Seen,Status"
    for i in {1..254}; do
      ip="$subnet.$i"
      mac=$(sudo arping -c 1 -q "$ip" 2>/dev/null | grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}")
      [ ! -z "$mac" ] && echo "$ip,$mac,$(date),active"
    done
  } > device_inventory.csv
}

create_inventory "192.168.1"
cat device_inventory.csv
```

### Network Troubleshooting

```bash
#!/bin/bash
# Diagnose ARP-related issues

diagnose_arp() {
  echo "=== ARP Diagnostics ==="
  echo "Default Gateway:"
  GATEWAY=$(ip route | grep default | awk '{print $3}')
  echo "Gateway IP: $GATEWAY"
  sudo arping -c 1 $GATEWAY

  echo ""
  echo "Local ARP Table:"
  arp -a

  echo ""
  echo "Checking for duplicate IPs:"
  for ip in $(arp -a | awk '{print $2}' | tr -d '()'); do
    COUNT=$(sudo arping -c 1 -v $ip 2>/dev/null | grep "bytes from" | wc -l)
    [ $COUNT -gt 1 ] && echo "WARNING: Duplicate IP $ip detected!"
  done
}

diagnose_arp
```

## Performance Optimization

### Parallel Scanning

```bash
#!/bin/bash
# Fast parallel ARP scan

parallel_arp_scan() {
  local subnet=$1
  local max_jobs=${2:-20}

  echo "Parallel scanning $subnet.0/24 with $max_jobs jobs..."

  for i in {1..254}; do
    (
      ip="$subnet.$i"
      mac=$(sudo arping -c 1 -q "$ip" 2>/dev/null | grep -oE "([a-f0-9]{2}:){5}[a-f0-9]{2}")
      [ ! -z "$mac" ] && echo "$ip,$mac"
    ) &

    if [ $((i % max_jobs)) -eq 0 ]; then
      wait
    fi
  done
  wait
}

parallel_arp_scan "192.168.1" 20
```

### Timeout Optimization

```bash
# Faster scans with shorter timeout
sudo arping -c 1 -w 500 192.168.1.100  # 500ms timeout

# Balance between speed and reliability
sudo arping -c 1 -p 100 192.168.1.100  # 100ms between packets
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
| --- | --- | --- |
| "Operation not permitted" | Not running as root | Use `sudo arping` |
| No responses from hosts | Interface not specified | Use `-i IFACE` option |
| Slow scans | Default timeout too long | Use `-w TIME` to reduce timeout |
| Intermittent results | Race condition | Use `-c 3` for multiple attempts |
| Unexpected MAC addresses | Spoofing/impersonation | Monitor with tcpdump to verify |

### Permission Issues

```bash
# arping requires root/sudo
arping 192.168.1.100
# Error: ARPING: No such device

# Use sudo
sudo arping 192.168.1.100
# Success

# Alternative: setcap (advanced)
sudo setcap cap_net_raw=ep /usr/sbin/arping
arping 192.168.1.100  # Now works without sudo
```

### Interface Not Found

```bash
# List available interfaces
ip link show
ifconfig -a
iwconfig

# Try with explicit interface
sudo arping -i eth0 192.168.1.100

# Check if interface is up
ip link show eth0
ip link set eth0 up  # Bring up if down
```

## Best Practices

| Practice | Reason | Implementation |
| --- | --- | --- |
| Use `-c 1` for single host | Efficiency | `sudo arping -c 1 TARGET` |
| Specify interface | Avoid wrong network | `-i eth0` or `-i wlan0` |
| Combine with other tools | Better coverage | Use with nmap, arp-scan |
| Monitor for spoofing | Security | Use tcpdump alongside arping |
| Automate discovery | Inventory | Create scripts for regular scans |
| Log results | Audit trail | Redirect output to files |

## Resources

| Resource | Link | Purpose |
| --- | --- | --- |
| GitHub Repository | github.com/ThomasHabets/arping | Source code & releases |
| Manual Page | `man arping` | Full documentation |
| ARP Protocol | RFC 826 | Understanding ARP mechanics |
| Network Tools | inetutils suite | Related network utilities |

Source: https://1337skills.com/cheatsheets/arping/

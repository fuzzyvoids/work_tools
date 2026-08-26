# Burp intermediate

Comprehensive burp commands and usage patterns for efficient workflow management.

## Overview

Burp is a powerful tool for various operations and system management. This cheat sheet covers essential commands, configuration options, and best practices.

## Installation

### Linux/Ubuntu

```bash
# Package manager installation
sudo apt update
sudo apt install burp

# Alternative installation
chmod +x burp
sudo mv burp /usr/local/bin/
```

### macOS

```bash
# Homebrew installation
brew install burp

# Manual installation
chmod +x burp
sudo mv burp /usr/local/bin/
```

### Windows

```powershell
# Chocolatey installation
choco install burp

# Scoop installation
scoop install burp

# Manual installation
# Download from official website and add to PATH
```

## Basic Commands

| Command | Description |
| --- | --- |
| `burp --help` | Display help information |
| `burp --version` | Show version information |
| `burp init` | Initialize burp in current directory |
| `burp status` | Check current status |
| `burp list` | List available options |
| `burp info` | Display system information |
| `burp config` | Show configuration |
| `burp update` | Update to latest version |

## Essential Operations

### Getting Started

```bash
# Initialize burp
burp init

# Basic usage
burp run

# With verbose output
burp --verbose run

# With configuration file
burp --config config.yaml run
```

### Configuration

```bash
# View configuration
burp config show

# Set configuration option
burp config set key value

# Get configuration value
burp config get key

# Reset configuration
burp config reset
```

### Advanced Operations

```bash
# Debug mode
burp --debug run

# Dry run (preview changes)
burp --dry-run run

# Force operation
burp --force run

# Parallel execution
burp --parallel run
```

## File Operations

| Command | Description |
| --- | --- |
| `burp create <file>` | Create new file |
| `burp read <file>` | Read file contents |
| `burp update <file>` | Update existing file |
| `burp delete <file>` | Delete file |
| `burp copy <src> <dst>` | Copy file |
| `burp move <src> <dst>` | Move file |

## Network Operations

```bash
# Connect to remote host
burp connect host:port

# Listen on port
burp listen --port 8080

# Send data
burp send --data "message" --target host

# Receive data
burp receive --port 8080
```

## Security Features

### Authentication

```bash
# Login with credentials
burp login --user username

# Logout
burp logout

# Change password
burp passwd

# Generate API key
burp generate-key
```

### Encryption

```bash
# Encrypt file
burp encrypt file.txt

# Decrypt file
burp decrypt file.txt.enc

# Generate certificate
burp cert generate

# Verify signature
burp verify file.sig
```

## Troubleshooting

### Common Issues

**Issue: Command not found**

```bash
# Check if installed
which burp

# Reinstall if necessary
sudo apt reinstall burp
```

**Issue: Permission denied**

```bash
# Run with sudo
sudo burp command

# Fix permissions
chmod +x /usr/local/bin/burp
```

**Issue: Configuration errors**

```bash
# Reset configuration
burp config reset

# Validate configuration
burp config validate
```

### Debug Commands

| Command | Description |
| --- | --- |
| `burp --debug` | Enable debug output |
| `burp --verbose` | Verbose logging |
| `burp test` | Run self-tests |
| `burp doctor` | Check system health |

## Best Practices

### Security

- Always verify checksums when downloading

- Use strong authentication methods

- Regularly update to latest version

- Follow principle of least privilege

### Performance

- Use appropriate buffer sizes

- Monitor resource usage

- Optimize configuration for your use case

- Regular maintenance and cleanup

### Maintenance

```bash
# Update burp
burp update

# Clean temporary files
burp clean

# Backup configuration
burp backup --config

# Restore from backup
burp restore --config backup.yaml
```

## Integration

### Scripting

```bash
#!/bin/bash
# Example script using burp

if ! command -v burp &> /dev/null; then
    echo "burp is not installed"
    exit 1
fi

if burp run; then
    echo "Success"
else
    echo "Failed"
    exit 1
fi
```

### API Integration

```python
import subprocess
import json

def run_burp(command):
    try:
        result = subprocess.run(['burp'] + command.split(),
                              capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error: \\\\{e\\\\}")
        return None
```

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `BURP_CONFIG` | Configuration file path | `~/.burp/config` |
| `BURP_HOME` | Home directory | `~/.burp` |
| `BURP_LOG_LEVEL` | Logging level | `INFO` |
| `BURP_TIMEOUT` | Operation timeout | `30s` |

## Configuration File

```yaml
# ~/.burp/config.yaml
version: "1.0"
settings:
  debug: false
  timeout: 30
  log_level: "INFO"

network:
  host: "localhost"
  port: 8080
  ssl: true

security:
  auth_required: true
  encryption: "AES256"
```

## Examples

### Basic Workflow

```bash
# 1. Initialize
burp init

# 2. Configure

# 3. Run operation
burp run

# 4. Check results
burp status

# 5. Cleanup
burp clean
```

### Advanced Workflow

```bash
# Comprehensive operation
burp run \
  --config production.yaml \
  --parallel \
  --verbose \
  --timeout 300

# Monitoring
burp monitor \
  --interval 60 \
  --alert-threshold 80
```

Source: https://1337skills.com/cheatsheets/burp/

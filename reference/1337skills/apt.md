# APT Package Manager intermediate

Comprehensive APT (Advanced Package Tool) commands and workflows for Debian and Ubuntu package management.

## Installation & Updates

### Basic Package Operations

| Command | Description |
| --- | --- |
| `sudo apt update` | Update package index |
| `sudo apt upgrade` | Upgrade all packages |
| `sudo apt full-upgrade` | Upgrade with dependency resolution |
| `sudo apt install package_name` | Install package |
| `sudo apt remove package_name` | Remove package |
| `sudo apt purge package_name` | Remove package and config files |
| `sudo apt autoremove` | Remove unused dependencies |

### Advanced Installation

| Command | Description |
| --- | --- |
| `sudo apt install package1 package2` | Install multiple packages |
| `sudo apt install package=version` | Install specific version |
| `sudo apt install ./package.deb` | Install local .deb file |
| `sudo apt reinstall package_name` | Reinstall package |
| `sudo apt install --no-install-recommends package` | Install without recommended packages |

## Package Information

### Search and Information

| Command | Description |
| --- | --- |
| `apt search keyword` | Search for packages |
| `apt show package_name` | Show package information |
| `apt list --installed` | List installed packages |
| `apt list --upgradable` | List upgradable packages |
| `apt list package_name` | Check if package is available |
| `dpkg -l` | List all installed packages |
| `dpkg -l | grep package` |

### Package Dependencies

| Command | Description |
| --- | --- |
| `apt depends package_name` | Show package dependencies |
| `apt rdepends package_name` | Show reverse dependencies |
| `apt-cache policy package_name` | Show package policy |

## Repository Management

### Repository Operations

| Command | Description |
| --- | --- |
| `sudo add-apt-repository ppa:user/repo` | Add PPA repository |
| `sudo add-apt-repository --remove ppa:user/repo` | Remove PPA repository |
| `sudo apt edit-sources` | Edit sources list |
| `ls /etc/apt/sources.list.d/` | List additional repositories |

### GPG Keys

| Command | Description |
| --- | --- |
| `sudo apt-key list` | List GPG keys |
| `wget -qO - https://example.com/key.gpg \|sudo apt-key add -` | Add GPG key |
| `sudo apt-key del KEYID` | Remove GPG key |

## System Maintenance

### Cleanup Operations

| Command | Description |
| --- | --- |
| `sudo apt autoclean` | Clean package cache |
| `sudo apt clean` | Remove all cached packages |
| `sudo apt autoremove --purge` | Remove unused packages and configs |
| `sudo apt-get check` | Check for broken dependencies |

### Fix Broken Packages

| Command | Description |
| --- | --- |
| `sudo apt --fix-broken install` | Fix broken dependencies |
| `sudo dpkg --configure -a` | Configure unconfigured packages |
| `sudo apt-get -f install` | Force install to fix dependencies |

## Configuration Files

### APT Configuration

| File | Description |
| --- | --- |
| `/etc/apt/sources.list` | Main repository list |
| `/etc/apt/sources.list.d/` | Additional repository files |
| `/etc/apt/apt.conf` | APT configuration |
| `/etc/apt/preferences` | Package pinning |

### Example sources.list

```bash
# Ubuntu 22.04 LTS (Jammy Jellyfish)
deb http://archive.ubuntu.com/ubuntu/ jammy main restricted
deb http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted
deb http://archive.ubuntu.com/ubuntu/ jammy universe
deb http://archive.ubuntu.com/ubuntu/ jammy-updates universe
deb http://archive.ubuntu.com/ubuntu/ jammy multiverse
deb http://archive.ubuntu.com/ubuntu/ jammy-updates multiverse
deb http://archive.ubuntu.com/ubuntu/ jammy-backports main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu/ jammy-security main restricted
deb http://security.ubuntu.com/ubuntu/ jammy-security universe
deb http://security.ubuntu.com/ubuntu/ jammy-security multiverse
```

## Package Pinning

### Pin Package Version

```bash
# /etc/apt/preferences.d/package-pin
Package: package_name
Pin: version 1.2.3*
Pin-Priority: 1001
```

### Pin Repository

```bash
# /etc/apt/preferences.d/repo-pin
Package: *
Pin: release o=Ubuntu,a=jammy-backports
Pin-Priority: 100
```

## Advanced Usage

### Simulation and Testing

| Command | Description |
| --- | --- |
| `apt list --upgradable -a` | Show all available versions |
| `sudo apt upgrade --dry-run` | Simulate upgrade |
| `sudo apt install package --dry-run` | Simulate installation |

### Logging and History

| Command | Description |
| --- | --- |
| `cat /var/log/apt/history.log` | View installation history |
| `cat /var/log/apt/term.log` | View detailed logs |
| `grep " install " /var/log/dpkg.log` | View dpkg install log |

## Troubleshooting

### Common Issues

| Problem | Solution |
| --- | --- |
| Package conflicts | `sudo apt --fix-broken install` |
| Locked database | `sudo rm /var/lib/dpkg/lock*` |
| Corrupted cache | `sudo apt clean && sudo apt update` |
| Unmet dependencies | `sudo apt -f install` |

### Emergency Recovery

| Command | Description |
| --- | --- |
| `sudo dpkg --force-depends --remove package` | Force remove problematic package |
| `sudo apt-get download package` | Download package without installing |
| `sudo dpkg -i --force-depends package.deb` | Force install .deb file |

## Best Practices

### Security

1. **Regular Updates**: Run `sudo apt update && sudo apt upgrade` regularly

1. **Verify Sources**: Only add trusted repositories

1. **GPG Verification**: Ensure packages are properly signed

1. **Security Updates**: Enable automatic security updates

1. **Backup**: Backup important data before major upgrades

### Performance

1. **Mirror Selection**: Use fastest mirror for your location

1. **Parallel Downloads**: Enable parallel downloads in apt.conf

1. **Cache Management**: Regular cleanup of package cache

1. **Dependency Resolution**: Use apt instead of apt-get for better output

1. **Network**: Use reliable network connection for updates

### Maintenance

1. **Regular Cleanup**: Remove unused packages and dependencies

1. **Log Monitoring**: Check logs for errors and warnings

1. **Disk Space**: Monitor disk space in /var/cache/apt/

1. **Repository Health**: Verify repository accessibility

1. **System Consistency**: Regular dependency checks

Source: https://1337skills.com/cheatsheets/apt/

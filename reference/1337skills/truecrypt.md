# TrueCrypt advanced

**DEPRECATED**: TrueCrypt development ceased in 2014. Use VeraCrypt instead for active development and security updates. This guide is for legacy system recovery only.

## Important Information

- **Status**: Abandoned (May 2014)

- **Successor**: VeraCrypt (fork with continued development)

- **Recommendation**: Migrate to VeraCrypt or LUKS for new implementations

- **Use Case**: Only for accessing existing TrueCrypt volumes on legacy systems

## Installation (Legacy Systems Only)

### Linux (from source)

```bash
# Download legacy version
wget https://www.archive.org/download/truecrypt-7.1a/TrueCrypt%207.1a%20Linux%20Kernel%202.4%20-%202.6.tar.gz

# Extract
tar xzf TrueCrypt*.tar.gz
cd truecrypt-7.1a

# Install dependencies
sudo apt-get install build-essential pkg-config libwxgtk2.8-dev

# Compile
./build.sh
sudo ./install
```

### macOS (Intel, legacy)

```bash
# Download disk image
curl -L -o truecrypt.dmg \
  "https://archive.org/download/TrueCrypt/TrueCrypt%207.1a.dmg"

# Mount and install
hdiutil mount truecrypt.dmg
cd /Volumes/TrueCrypt\ 7.1a
sudo installer -pkg TrueCrypt\ 7.1a.mpkg -target /

# Unmount
hdiutil unmount /Volumes/TrueCrypt\ 7.1a
```

### Windows (legacy)

```powershell
# Download installer
$url = "https://archive.org/download/TrueCrypt/TrueCrypt%20Setup%207.1a.exe"
Invoke-WebRequest -Uri $url -OutFile TrueCrypt.exe

# Run installer
.\TrueCrypt.exe

# Command-line installation
TrueCrypt.exe /S /D=C:\Program Files\TrueCrypt
```

## Basic Volume Operations

### Create Standard Volume

```bash
# GUI (recommended for safety)
truecrypt

# Command-line create
truecrypt --create volume.img --size 1000M --filesystem FAT

# Interactive mode
truecrypt --create
# (Follow prompts for password, encryption, filesystem)
```

### Create Hidden Volume

```bash
# Hidden volume in existing TrueCrypt volume
truecrypt --create outer_volume.img

# Then open and create hidden partition within
truecrypt --create

# Interactive process:
# 1. Create outer volume first
# 2. Mount outer volume
# 3. Create hidden volume inside
# 4. Use different password for hidden volume
```

### Mount Volume

```bash
# GUI mount
truecrypt

# Command-line mount
truecrypt volume.img /mnt/truecrypt

# Mount with specific slot
truecrypt --mount volume.img --slot 1 /mnt/truecrypt

# Mount read-only
truecrypt --mount-options=ro volume.img /mnt/truecrypt
```

### Dismount Volume

```bash
# Dismount specific volume
truecrypt --dismount /mnt/truecrypt

# Dismount by slot
truecrypt --dismount slot1

# Dismount all
truecrypt --dismount-all

# Force dismount
truecrypt --force --dismount /mnt/truecrypt
```

## Volume Management

### Create Volume File

```bash
# Create 500MB encrypted volume file
truecrypt --create encrypted.img --size 500M

# Create with password
echo "mypassword" | truecrypt --create vol.img --password --size 1G

# Create on USB drive
truecrypt --create /media/usb/secure.img --size 2G --filesystem FAT
```

### Encrypt USB Drive

```bash
# Create encrypted partition on USB
truecrypt --create /dev/sdX1 --size 4G

# Create hidden volume on USB
truecrypt --create /dev/sdX1 --hidden

# Mount encrypted USB
truecrypt /dev/sdX1 /mnt/usb
```

## Key and Password Management

### Change Password

```bash
# Interactive password change
truecrypt --change-password volume.img

# Specify old password
echo "oldpass" | truecrypt --change-password volume.img --password

# Non-interactive (risky, show in history)
truecrypt --change-password volume.img \
  --password "oldpass" \
  --new-password "newpass"
```

### Create Key Files

```bash
# Generate random key file
dd if=/dev/urandom of=keyfile.key bs=1024 count=4

# Use key file with volume
truecrypt --create volume.img --keyfile keyfile.key

# Mount with key file
truecrypt --mount volume.img --keyfile keyfile.key /mnt/truecrypt

# Use multiple key files
truecrypt --create volume.img \
  --keyfile keyfile1.key,keyfile2.key

# Mount with multiple key files
truecrypt --mount volume.img \
  --keyfile keyfile1.key,keyfile2.key /mnt/truecrypt
```

## Encryption Ciphers

### View Available Ciphers

```bash
# List ciphers in GUI
truecrypt -> Settings -> Encryption

# Typical ciphers available:
# - AES (128-bit key)
# - Twofish (128-bit key)
# - Serpent (128-bit key)
# - AES-Twofish
# - AES-Twofish-Serpent
# - Twofish-Serpent
```

### Create with Specific Cipher

```bash
# Note: GUI selection required at creation
# Command-line doesn't allow cipher specification

# Mount existing volume
truecrypt volume.img /mnt/truecrypt
# Cipher is stored in volume header
```

## Volume Information

### View Volume Details

```bash
# Interactive info display
truecrypt --info volume.img

# Display all mounted volumes
truecrypt --list

# Check slot contents
truecrypt --list-slot volume.img
```

## Data Recovery and Backup

### Backup Volume Header

```bash
# Manual backup (critical for recovery)
dd if=volume.img of=header.bak bs=512 count=1

# From mounted device
dd if=/dev/sdX1 of=header.bak bs=512 count=1

# Restore header
dd if=header.bak of=volume.img bs=512 count=1 seek=0
```

### Recover Forgotten Password

```bash
# TrueCrypt has no password recovery
# Options if password forgotten:
# 1. Brute force (not practical, designed to be slow)
# 2. Try common passwords
# 3. If header backup exists, could attempt recovery

# Password isn't stored, it's used to derive the header key
# Once forgotten, volume is effectively inaccessible
```

## Scripting Examples

### Automated Mount Script

```bash
#!/bin/bash
# TrueCrypt auto-mount (legacy systems)

VOLUME="$HOME/encrypted.img"
MOUNT_POINT="/mnt/secure"
PASSWORD="your_password_here"

# Create mount point
mkdir -p "$MOUNT_POINT"

# Mount with password
echo "$PASSWORD" | \
truecrypt "$VOLUME" "$MOUNT_POINT" --password --text

if [ $? -eq 0 ]; then
    echo "Volume mounted successfully"
else
    echo "Mount failed"
    exit 1
fi
```

### Batch Volume Creation

```bash
#!/bin/bash
# Create multiple legacy volumes

SIZES=(500M 1G 2G)
PASSWORDS=("pass1" "pass2" "pass3")

for i in "${!SIZES[@]}"; do
    VOL="volume_${i}.img"
    SIZE="${SIZES[$i]}"
    PASS="${PASSWORDS[$i]}"

    echo "Creating $VOL ($SIZE)..."

    echo "$PASS" | \
    truecrypt --create "$VOL" \
        --size "$SIZE" \
        --password \
        --filesystem FAT \
        --silent

    if [ $? -eq 0 ]; then
        echo "Successfully created $VOL"
    fi
done
```

## Troubleshooting

### Common Issues

**Issue: "Mount directory not empty"**

```bash
# Remove contents of mount directory
sudo rm -rf /mnt/truecrypt/*

# Or create new mount point
mkdir -p /mnt/secure
truecrypt volume.img /mnt/secure
```

**Issue: "Not a TrueCrypt volume"**

```bash
# Corrupted header or wrong password
# Verify file size
ls -lh volume.img

# Try with different password
truecrypt volume.img /mnt/truecrypt

# Check first 512 bytes (header)
hexdump -C volume.img | head
```

**Issue: "Permission denied"**

```bash
# Run with sudo
sudo truecrypt volume.img /mnt/truecrypt

# Fix mount point permissions
sudo chown $USER:$USER /mnt/truecrypt

# Add user to relevant groups
sudo usermod -a -G disk $USER
```

**Issue: Kernel module not loading**

```bash
# Install kernel module
sudo truecrypt --install

# Check module
lsmod | grep truecrypt

# Manually load if needed
sudo modprobe truecrypt
```

## Comparison with Modern Alternatives

| Feature | TrueCrypt | VeraCrypt | LUKS |
| --- | --- | --- | --- |
| Development | Stopped 2014 | Active | Active |
| Security | Good (dated) | Better | Excellent |
| Cipher Options | Limited | More options | Standard |
| Hidden Volumes | Yes | Yes | No |
| Cross-platform | Yes | Yes | Linux only |
| Performance | Good | Good | Excellent |
| Recommendation | Legacy only | Modern use | Linux standard |

## Migration Path

### From TrueCrypt to VeraCrypt

```bash
# VeraCrypt can mount TrueCrypt volumes
veracrypt volume.img /mnt/truecrypt

# Export data to new VeraCrypt volume
# 1. Mount TrueCrypt volume
# 2. Create VeraCrypt volume with same capacity
# 3. Copy data between mounted volumes
# 4. Verify data integrity
# 5. Securely delete old TrueCrypt volume
```

### From TrueCrypt to LUKS (Linux)

```bash
# For partition-based volumes
# 1. Back up all data
# 2. Create LUKS partition
# 3. Restore data to LUKS partition
# 4. Update mount scripts/fstab

# For file-based volumes, use conversion tools or manual migration
```

## Best Practices for Legacy Systems

- **Backup Regularly**: Store encrypted backups on modern systems

- **Document Setup**: Keep encrypted notes on access procedures

- **Test Recovery**: Regularly test accessing volumes

- **Plan Migration**: Develop timeline to move to modern encryption

- **Monitor Security**: Watch for new vulnerabilities in TrueCrypt

- **Keep Offline Copy**: Maintain offline backup of critical volumes

## Security Notes

- TrueCrypt was considered secure at its time

- No major vulnerabilities known as of 2014

- Modern ciphers and key derivation functions are stronger

- Considered "secure enough" for non-critical legacy data

- Not recommended for new deployments

## Related Tools

- [VeraCrypt](veracrypt.md) - Modern successor to TrueCrypt

- [LUKS](luks.md) - Linux standard encryption

- [BitLocker](bitlocker.md) - Windows disk encryption

- [FileVault](filevault.md) - macOS disk encryption

---

**Deprecation Notice**: This tool is no longer maintained. For new systems, use VeraCrypt or LUKS.

_Last updated: 2026-03-30_

Source: https://1337skills.com/cheatsheets/truecrypt/

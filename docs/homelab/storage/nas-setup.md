# Network Attached Storage (NAS) Setup

## Overview

Network Attached Storage provides centralized file storage for homelab environments. This guide covers setting up NAS solutions with OpenMediaVault, TrueNAS, and DIY configurations.

## NAS Solutions Comparison

### Popular NAS Operating Systems
```bash
# NAS OS Comparison
Solution       | Cost        | Difficulty | Features           | Hardware Req
OpenMediaVault | Free        | Easy       | Docker, Plugins     | x86_64 1GB RAM
TrueNAS Core  | Free        | Medium     | ZFS, Docker, VMs   | x86_64 8GB RAM
TrueNAS Scale | Free        | Medium     | K8s, ZFS, Docker   | x86_64 8GB RAM
Unraid         | Paid        | Easy       | Docker, VMs, Array  | x86_64 4GB RAM
Rockstor       | Freemium    | Medium     | BTRFS, Docker       | x86_64 2GB RAM
DIY (Debian)  | Free        | Hard       | Custom, Full Control | x86_64 1GB RAM
```

## Hardware Requirements

### Recommended Hardware Specifications
```bash
# Minimum Requirements
CPU: x86_64 dual-core 2.0GHz
RAM: 4GB DDR4 (8GB recommended)
Storage: 2x 4TB+ drives (for RAID)
Network: Gigabit Ethernet (10GbE recommended)
Boot: 32GB+ USB/SSD (for OS)

# Recommended Specifications
CPU: x86_64 quad-core 3.0GHz+ (Intel Celeron J4125+)
RAM: 16GB DDR4 (32GB for virtualization)
Storage: 4x 8TB+ drives (for RAID 6/10)
Network: 10GbE (with 1GbE backup)
Boot: 256GB SSD (for OS and cache)
Power: 400W+ PSU (80+ Bronze efficiency)
Case: 4+ bay NAS case with good cooling
```

### Drive Configuration Examples
```bash
# Storage Array Configurations

# Basic 2-Bay Setup (Good for beginners)
2x 4TB drives = 4TB usable (RAID 1 mirroring)
Pros: Redundancy, simple setup
Cons: 50% capacity efficiency

# 4-Bay Setup (Recommended)
4x 8TB drives = 16TB usable (RAID 5)
Pros: Good capacity, single drive redundancy
Cons: Rebuild time, single point of failure during rebuild

# Advanced 6-Bay Setup
6x 12TB drives = 48TB usable (RAID 6)
Pros: Dual drive redundancy, good capacity
Cons: Longer rebuild times, more complex

# Hybrid Setup (Performance + Capacity)
2x 512GB SSD (cache) + 4x 8TB HDD (storage)
Pros: Fast cache, large storage capacity
Cons: More complex configuration
```

## OpenMediaVault Setup

### Installation and Initial Configuration
```bash
# 1. Download and Flash OpenMediaVault
wget https://sourceforge.net/projects/openmediavault/files/\
OpenMediaVault/6.x/openmediavault_6.9.0-amd64.iso/download

# 2. Create bootable USB
sudo dd if=openmediavault_6.9.0-amd64.iso of=/dev/sdX bs=4M status=progress

# 3. Boot from USB and install
- Select language and keyboard
- Choose installation disk (USB or SSD)
- Configure network (static IP recommended)
- Set root password
- Complete installation

# 4. Initial web configuration
URL: https://NAS_IP (default: admin/openmediavault)
Change default password immediately!
```

### Storage Configuration
```bash
# Web Interface Steps

# 1. Create Storage Array
Storage -> RAID Management -> Create
- Select drives (exclude boot drive)
- Choose RAID level (RAID 5 recommended)
- Set filesystem (EXT4 or XFS)
- Name the array (e.g., "dataarray")

# 2. Create Filesystem
Storage -> File Systems -> Create
- Select RAID array
- Choose filesystem (EXT4 recommended)
- Set mount point (/data)
- Enable at boot

# 3. Create Shared Folders
Storage -> Shared Folders -> Create
- Name: media, documents, backups, etc.
- Path: /data/media, /data/documents
- Permissions: Set appropriate user/group
- Enable SMB/CIFS sharing

# 4. Configure Services
Services -> SMB/CIFS -> Enable
- Workgroup: WORKGROUP (default)
- Enable time machine (if needed)
- Configure user access
```

### Service Configuration
```bash
# SMB/CIFS Configuration
Services -> SMB/CIFS -> Settings

# Basic Settings
Workgroup: WORKGROUP
Description: Homelab NAS
Server string: %h NAS
Enable NetBIOS: Yes
Enable Time Machine: Yes

# Advanced Settings
Min protocol: SMB2
Max protocol: SMB3
Unix extensions: Yes
Wide links: Yes
Follow symlinks: Yes

# User Configuration
Services -> SMB/CIFS -> Shares
Select shared folder -> Privileges
Add users with read/write access as needed

# NFS Configuration (for Linux clients)
Services -> NFS -> Settings
Enable: Yes
Enable v4: Yes
Enable v4.2: Yes
Client access: 192.168.1.0/24
```

## TrueNAS Core Setup

### Installation Process
```bash
# 1. Download TrueNAS Core
wget https://www.truenas.com/download-truenas-core/

# 2. Create bootable USB
sudo dd if=FreeBSD-13.1-RELEASE-amd64-disc1.iso of=/dev/sdX bs=4M

# 3. Initial Setup (Console or Web)
1. Configure network interface
2. Set root password
3. Configure timezone
4. Access web interface: http://NAS_IP

# 4. Storage Pool Creation
Storage -> Pools -> Add
- Pool Name: tank
- Encryption: Yes (recommended)
- Type: RAID-Z1 (recommended)
- Select drives for the pool
- Review and create pool
```

### Dataset and Share Configuration
```bash
# Create Datasets (ZFS filesystems)
Storage -> Pools -> tank -> Add Dataset

# Media Dataset
Name: media
Compression: LZ4 (good balance)
atime: Off (performance improvement)
Case Sensitivity: Insensitive
Share Type: SMB

# Documents Dataset  
Name: documents
Compression: LZ4
atime: On (needed for some applications)
Case Sensitivity: Sensitive
Share Type: SMB

# Backups Dataset
Name: backups
Compression: GZIP (better compression)
atime: Off
Case Sensitivity: Sensitive
Share Type: NFS/SMB

# Configure SMB Shares
Sharing -> Windows (SMB) Shares -> Add
Select dataset -> Configure
Share name: media, documents, backups
Enable: Yes
Allowed hosts: 192.168.1.0/24
Enable time machine: Yes (for media)
```

### Advanced ZFS Configuration
```bash
# ZFS Pool Management Commands (via shell)

# Check pool status
zpool status
zpool list

# Check dataset properties
zfs list
zfs get all tank

# Create snapshots (for backups)
zfs snapshot tank/documents@daily-$(date +%Y%m%d)
zfs snapshot tank/media@weekly-$(date +%Y%m%d)

# List snapshots
zfs list -t snapshot

# Restore from snapshot
zfs rollback tank/documents@daily-20231201

# Replicate to backup pool
zfs send tank/documents@daily-20231201 | zfs receive backup/documents

# Monitor ZFS performance
zpool iostat -v 1
zfs iostat -v 1
```

## DIY NAS with Debian

### Base System Setup
```bash
#!/bin/bash
# NAS Server Setup Script

# 1. Install Debian Minimal
# Download Debian netinst and install minimal system

# 2. Update and install basic packages
apt update && apt upgrade -y
apt install -y net-tools vim htop tmux

# 3. Configure network (static IP)
cat > /etc/netplan/01-nas-config.yaml << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:
      dhcp4: no
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
EOF

netplan apply

# 4. Install storage management tools
apt install -y mdadm lvm2 samba nfs-common

# 5. Configure RAID array (example with 4 drives)
mdadm --create /dev/md0 --level=5 --raid-devices=4 \
  /dev/sda /dev/sdb /dev/sdc /dev/sdd

# Monitor RAID array
watch cat /proc/mdstat
```

### Filesystem and Services Configuration
```bash
#!/bin/bash
# Filesystem and Services Setup

# 1. Create filesystem on RAID array
mkfs.ext4 /dev/md0

# 2. Create mount points
mkdir -p /mnt/nas/{media,documents,backups,public}

# 3. Add to /etc/fstab
echo '/dev/md0 /mnt/nas ext4 defaults 0 2' >> /etc/fstab

# 4. Mount filesystem
mount -a

# 5. Create directories
mkdir -p /mnt/nas/media/{movies,tv,music,photos}
mkdir -p /mnt/nas/documents/{personal,work,shared}
mkdir -p /mnt/nas/backups/{daily,weekly,monthly}
mkdir -p /mnt/nas/public/downloads

# 6. Install and configure Samba
apt install -y samba samba-common-bin

# Backup original config
cp /etc/samba/smb.conf /etc/samba/smb.conf.backup

# Create Samba configuration
cat > /etc/samba/smb.conf << EOF
[global]
   workgroup = WORKGROUP
   server string = Homelab NAS
   security = user
   map to guest = Bad User
   dns proxy = no
   vfs objects = recycle

[media]
   path = /mnt/nas/media
   browseable = yes
   writeable = yes
   guest ok = yes
   create mask = 0664
   directory mask = 0775

[documents]
   path = /mnt/nas/documents
   browseable = yes
   writeable = yes
   valid users = @users
   create mask = 0660
   directory mask = 0770

[backups]
   path = /mnt/nas/backups
   browseable = yes
   writeable = yes
   valid users = admin
   create mask = 0600
   directory mask = 0700
EOF

# 7. Create Samba users
useradd -m nasuser
smbpasswd -a nasuser

# 8. Start and enable services
systemctl enable smbd nmbd
systemctl start smbd nmbd
```

## Backup and Monitoring

### Automated Backup Setup
```bash
#!/bin/bash
# NAS Backup Script

BACKUP_SOURCE="/mnt/nas"
BACKUP_DEST="/backup/nas-backup"
LOG_FILE="/var/log/nas-backup.log"
RETENTION_DAYS=30

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Function to perform backup
perform_backup() {
    local source=$1
    local dest=$2
    local backup_name=$(date +%Y%m%d-%H%M%S)
    
    log_message "Starting backup of $source"
    
    # Use rsync for incremental backup
    rsync -av --delete --link-dest="$BACKUP_DEST/latest" \
        "$source" "$BACKUP_DEST/$backup_name"
    
    # Update latest symlink
    ln -sfn "$BACKUP_DEST/$backup_name" "$BACKUP_DEST/latest"
    
    log_message "Backup completed: $backup_name"
}

# Function to clean old backups
cleanup_old_backups() {
    log_message "Cleaning up backups older than $RETENTION_DAYS days"
    find "$BACKUP_DEST" -maxdepth 1 -type d -mtime +$RETENTION_DAYS \
        -not -name "latest" -exec rm -rf {} \;
    log_message "Cleanup completed"
}

# Main execution
log_message "=== Starting NAS Backup ==="

# Perform backup
perform_backup "$BACKUP_SOURCE" "$BACKUP_DEST"

# Clean old backups
cleanup_old_backups

# Verify backup integrity
if [ -d "$BACKUP_DEST/latest" ]; then
    log_message "Backup verification: SUCCESS"
else
    log_message "Backup verification: FAILED"
    exit 1
fi

log_message "=== Backup completed successfully ==="

# Setup cron job (run daily at 2 AM)
# 0 2 * * * /path/to/nas-backup.sh
```

### Monitoring and Alerts
```bash
#!/bin/bash
# NAS Monitoring Script

EMAIL_ALERT="admin@example.com"
LOG_FILE="/var/log/nas-monitor.log"
DISK_THRESHOLD=80
MEMORY_THRESHOLD=80
TEMP_THRESHOLD=60

# Function to send email alert
send_alert() {
    local subject=$1
    local message=$2
    echo "$message" | mail -s "$subject" "$EMAIL_ALERT"
}

# Function to check disk space
check_disk_space() {
    local usage=$(df /mnt/nas | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $usage -gt $DISK_THRESHOLD ]; then
        local message="WARNING: NAS disk usage at ${usage}%"
        log_message "$message"
        send_alert "NAS Disk Space Alert" "$message"
    fi
}

# Function to check memory usage
check_memory() {
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ $usage -gt $MEMORY_THRESHOLD ]; then
        local message="WARNING: NAS memory usage at ${usage}%"
        log_message "$message"
        send_alert "NAS Memory Alert" "$message"
    fi
}

# Function to check RAID status
check_raid() {
    local status=$(cat /proc/mdstat | grep -o "blocks.*\[" | head -1)
    
    if [[ $status != *"blocks"* ]]; then
        local message="WARNING: RAID array may be degraded"
        log_message "$message"
        send_alert "NAS RAID Alert" "$message"
    fi
}

# Function to check system temperature
check_temperature() {
    local temp=$(sensors | grep "Core 0" | awk '{print $3}' | sed 's/+//;s/°C//')
    
    if [ ! -z "$temp" ] && [ $temp -gt $TEMP_THRESHOLD ]; then
        local message="WARNING: System temperature at ${temp}°C"
        log_message "$message"
        send_alert "NAS Temperature Alert" "$message"
    fi
}

# Function to log message
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Main monitoring loop
log_message "=== Starting NAS Monitoring ==="

check_disk_space
check_memory
check_raid
check_temperature

log_message "=== Monitoring check completed ==="

# Setup cron job (run every 15 minutes)
# */15 * * * * /path/to/nas-monitor.sh
```

## Security Configuration

### User and Access Management
```bash
# Create user groups for different access levels
groupadd media_users
groupadd document_users  
groupadd admin_users

# Create users with appropriate groups
useradd -m -G media_users,users john
useradd -m -G document_users,users jane
useradd -m -G admin_users,users admin

# Set passwords
echo "john:password123" | chpasswd
echo "jane:password456" | chpasswd
echo "admin:admin789" | chpasswd

# Configure directory permissions
chmod 775 /mnt/nas/media
chown :media_users /mnt/nas/media

chmod 770 /mnt/nas/documents
chown :document_users /mnt/nas/documents

chmod 700 /mnt/nas/backups
chown :admin_users /mnt/nas/backups
```

### Network Security
```bash
# Configure UFW firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (from specific network)
ufw allow from 192.168.1.0/24 to any port 22

# Allow NAS services (LAN only)
ufw allow from 192.168.1.0/24 to any port 139
ufw allow from 192.168.1.0/24 to any port 445
ufw allow from 192.168.1.0/24 to any port 2049

# Enable firewall
ufw enable

# Configure fail2ban for SSH protection
apt install -y fail2ban

cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
EOF

systemctl enable fail2ban
systemctl start fail2ban
```

## Performance Optimization

### Network Optimization
```bash
# TCP/IP tuning for NAS performance
cat >> /etc/sysctl.conf << EOF

# Network performance tuning
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
EOF

# Apply sysctl changes
sysctl -p

# Enable jumbo frames (if supported by network)
# Set MTU to 9000 on network interface
ip link set dev enp0s3 mtu 9000

# Samba performance tuning
cat >> /etc/samba/smb.conf << EOF

# Performance optimizations
socket options = TCP_NODELAY SO_RCVBUF=131072 SO_SNDBUF=131072
use sendfile = true
aio read size = 16384
aio write size = 16384
EOF
```

## Troubleshooting

### Common Issues and Solutions
```bash
# Issue: RAID array degraded
# Solution: Check which drive failed
cat /proc/mdstat
mdadm --detail /dev/md0

# Replace failed drive
mdadm --manage /dev/md0 --add /dev/sdX

# Issue: Samba shares not accessible
# Solution: Check Samba status and logs
systemctl status smbd nmbd
tail -f /var/log/samba/log.smbd

# Test Samba configuration
testparm -s

# Issue: Slow performance
# Solution: Check disk I/O and network
iotop -o
iftop -i enp0s3
hdparm -Tt /dev/sda

# Issue: Out of memory errors
# Solution: Monitor memory usage
free -h
ps aux --sort=-%mem | head -10

# Add swap if needed
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

## Summary

A well-configured NAS provides reliable, centralized storage for homelab environments:

- **Solution Choice**: Select based on needs and expertise
- **Hardware Planning**: Invest in quality components
- **Data Protection**: Implement RAID and backups
- **Security**: Configure proper access controls
- **Monitoring**: Set up automated monitoring and alerts
- **Performance**: Optimize for your workload

Regular maintenance and monitoring ensure long-term reliability and data safety.

## Further Reading

- [OpenMediaVault Documentation](https://documentation.openmediavault.org/)
- [TrueNAS Documentation](https://www.truenas.com/docs/)
- [ZFS Administration Guide](https://openzfs.github.io/openzfs-docs/)
- [Samba Official Documentation](https://www.samba.org/samba/docs/)

---

*This guide provides comprehensive NAS setup instructions for homelab storage needs.*

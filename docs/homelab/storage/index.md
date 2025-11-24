---
title: Storage Systems
description: Comprehensive storage solutions for homelab environments
---

# Storage Systems

Effective storage management is crucial for any homelab. This section covers everything from basic NAS setup to advanced storage technologies like ZFS, RAID, and backup strategies.

## 💾 Storage Architecture

### Storage Hierarchy
```
Tier 1: SSD Cache      # Fast access, frequently used data
Tier 2: HDD Array      # Main storage, bulk data
Tier 3: Cloud/Offsite  # Backup, archives
Tier 4: Cold Storage    # Rarely accessed data
```

### Common Storage Solutions

| Technology | Use Case | Pros | Cons |
|------------|----------|------|------|
| **Docker Volumes** | Container data | Simple, portable | Limited performance |
| **ZFS** | File server, backup | Data integrity, snapshots | RAM intensive |
| **RAID** | Performance/Redundancy | Speed, reliability | Complex recovery |
| **NAS** | Network storage | Easy access, sharing | Cost, single point of failure |
| **Cloud Storage** | Backup, sync | Offsite, accessible | Costs, privacy concerns |

## 📚 Storage Documentation

### [NAS Configuration](nas.md)
- TrueNAS/Unraid setup
- Network file sharing (SMB, NFS)
- User permissions
- Media server integration

### [Backup Strategies](backup.md)
- 3-2-1 backup strategy
- Automated backup scripts
- Cloud backup solutions
- Disaster recovery planning

### [Data Recovery](recovery.md)
- File system recovery
- RAID rebuild procedures
- Data forensics tools
- Preventive measures

## 🗂️ Storage Planning

### Capacity Planning

#### Calculate Your Needs
```bash
# Example storage requirements calculation
Base Usage: 500GB
Growth Rate: 100GB/year
Planning Horizon: 5 years
Total Required: 500 + (100 × 5) = 1TB
Recommended: 3TB (3x for redundancy)
```

#### Storage Categories
```bash
Documents:           50GB   # Text, PDFs, spreadsheets
Photos:             200GB   # Family photos, images
Videos:             500GB   # Home videos, movies
Music:              50GB   # Audio files, playlists
Backups:            300GB   # System backups, archives
VMs/Containers:     200GB   # Virtual machines, containers
Development:        100GB   # Code, projects
Media Server:       1TB+    # Plex, Jellyfin libraries
```

### Performance Requirements

#### IOPS Calculator
```bash
# Basic IOPS requirements per workload
Web Hosting:        50-100 IOPS
Database:           200-500 IOPS
Media Streaming:    100-200 IOPS
File Server:         150-300 IOPS
Virtualization:      500-1000+ IOPS
```

#### Bandwidth Planning
```bash
# Network bandwidth requirements
1Gbps LAN = 125 MB/s theoretical
Real-world: ~100-110 MB/s

SSD Array: 500+ MB/s
HDD Array: 200-300 MB/s (RAID 10)
Mixed Storage: 100-200 MB/s
```

## 🔧 Storage Technologies

### File Systems

#### ZFS Features
```bash
# Advantages of ZFS
- Data integrity with checksums
- Self-healing capabilities
- Snapshots and clones
- Compression (LZ4, ZSTD)
- Deduplication
- RAID-Z (RAID 5/6 equivalent)
```

#### Btrfs Features
```bash
# Advantages of Btrfs
- Copy-on-write (CoW)
- Snapshots
- Compression
- Built-in RAID
- Subvolumes
- Checksums
```

#### ext4 Features
```bash# Advantages of ext4
- Mature and stable
- Good performance
- Journaling
- Large file support
- Widely compatible
- Low resource usage
```

### RAID Configurations

#### RAID Levels Comparison
| RAID | Min Disks | Capacity | Fault Tolerance | Performance |
|------|-----------|----------|-----------------|-------------|
| RAID 0 | 2 | 100% | None | Excellent |
| RAID 1 | 2 | 50% | 1 disk | Good read |
| RAID 5 | 3 | 67% | 1 disk | Good |
| RAID 6 | 4 | 50% | 2 disks | Fair |
| RAID 10 | 4 | 50% | 1 disk per pair | Excellent |

#### Recommended RAID for Homelab
```bash
# Performance focused: RAID 10
# Capacity focused: RAID 6
# Mixed approach: RAID 10 for OS/apps, RAID 6 for data
# Budget: RAID 1 for OS, RAID 5 for data
```

## 🏗️ Storage Setup Examples

### Basic NAS Setup
```bash
# Hardware requirements
CPU: 4+ cores
RAM: 8GB+ (16GB for ZFS)
Storage: 2x 4TB+ drives
Network: Gigabit ethernet

# Software options
TrueNAS (FreeNAS)     # ZFS focused
Unraid               # Easy setup, mixed drives
OpenMediaVault       # Debian-based
DIY (Linux)          # Full control
```

### ZFS Pool Configuration
```bash
# Create mirror pool (RAID 1 equivalent)
zpool create tank mirror /dev/sda /dev/sdb

# Create RAID-Z pool (RAID 5 equivalent)
zpool create tank raidz1 /dev/sda /dev/sdb /dev/sdc

# Create RAID-Z2 pool (RAID 6 equivalent)
zpool create tank raidz2 /dev/sda /dev/sdb /dev/sdc /dev/sdd

# Add cache device
zpool add tank cache /dev/nvme0n1

# Add log device (ZIL)
zpool add tank log /dev/nvme0n1p1
```

### Docker Storage Setup
```bash
# Create Docker volumes
docker volume create app_data
docker volume create database_data

# Use bind mounts for better performance
docker run -d \
  -v /homelab/data/app:/data \
  -v /homelab/config/app:/config \
  app-image

# Volume for persistent data
docker run -d \
  -v database_data:/var/lib/postgresql \
  postgres:latest
```

## 📊 Storage Monitoring

### Capacity Monitoring
```bash
# Check disk usage
df -h
du -sh /path/to/directory

# ZFS specific monitoring
zpool list
zfs list

# Monitor Docker volumes
docker system df
```

### Performance Monitoring
```bash
# Disk performance
iotop -o
iostat -x 1

# Network storage performance
iperf3 -c nas-ip -t 30

# File system performance
bonnie++ -d /test/path -s 2G -r 512M
```

### Health Monitoring
```bash
# S.M.A.R.T. status
smartctl -a /dev/sda

# ZFS health
zpool status

# Array health (mdadm)
cat /proc/mdstat

# File system check
fsck -n /dev/sda1  # Dry run
```

## 🔍 Common Storage Issues

### Running Out of Space
```bash
# Find large files
find / -type f -size +1G 2>/dev/null | head -10

# Check Docker space usage
docker system df
docker system prune -a

# Clean old logs
journalctl --vacuum-time=7d

# Clear package cache
apt-get clean
```

### Performance Issues
```bash
# Check for I/O bottlenecks
iotop
vmstat 1
iostat -x 5

# Check for disk errors
dmesg | grep -i error
smartctl -l error /dev/sda

# Check for fragmentation (btrfs)
btrfs filesystem df /path
```

### Data Corruption
```bash
# ZFS scrub
zpool scrub tank

# Check for errors
zpool status

# Recover from snapshots
zfs rollback tank@snapshot-name

# File system check (if needed)
zpool scrub tank
```

## 📋 Storage Best Practices

### General Guidelines
- [ ] Use UPS for storage equipment
- [ ] Monitor drive health regularly
- [ ] Implement backup strategy
- [ ] Document configuration
- [ ] Test recovery procedures

### Performance Optimization
- [ ] Use SSD for caching
- [ ] Configure appropriate RAID level
- [ ] Monitor I/O patterns
- [ ] Optimize file system settings
- [ ] Network optimization

### Data Protection
- [ ] Regular backups
- [ ] Offsite copy
- [ ] Encryption for sensitive data
- [ ] Access controls
- [ ] Audit logs

## 🛠️ Troubleshooting Tools

### Diagnostic Commands
```bash
# System information
lsblk                     # Block devices
lscpu                      # CPU info
free -h                   # Memory info

# Storage specific
fdisk -l                   # Disk partitions
df -h                      # File systems
mount                      # Mounted filesystems

# Performance
top                        # System processes
iotop                      # I/O monitoring
nethogs                    # Network usage
```

### Recovery Tools
```bash
# File recovery
photorec                   # Photo/file recovery
testdisk                   # Partition recovery
ddrescue                   # Data recovery

# File system tools
fsck                       # File system check
xfs_repair                 # XFS repair
btrfs restore              # Btrfs recovery
```

---

**Ready to set up your storage?** Start with our [NAS Configuration](nas.md) guide for a complete storage solution!

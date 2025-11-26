---
title: Linux System Administration
description: Comprehensive guide for Linux system administration in homelab environments
---

# Linux System Administration

Linux is the foundation of most homelab environments, serving as the primary operating system for servers, containers, and network infrastructure. This comprehensive guide covers Linux administration from basic concepts to advanced system management.

## 🐧 Linux Fundamentals

### Linux Architecture Overview
```bash
# Linux System Components

Kernel:
  Role: Core operating system
  Functions: Hardware abstraction, process management
  Versioning: Semantic versioning (5.x.x, 6.x)
  Modules: Loadable kernel modules
  Syscalls: System call interface

System Libraries:
  glibc: GNU C library
  systemd: System and service manager
  Coreutils: Essential system utilities
  Shell: Command-line interface (bash, zsh, fish)

Filesystem:
  Hierarchy: FHS (Filesystem Hierarchy Standard)
  Types: ext4, xfs, btrfs, zfs
  Mounting: Mount points and filesystem table
  Permissions: Unix permissions and ACLs

Process Management:
  Init System: systemd (modern), SysVinit (legacy)
  Process IDs: Unique process identification
  Signals: Inter-process communication
  Resource limits: CPU, memory, file descriptors
```

### Linux Distributions
```bash
# Distribution Categories

Debian-based:
  Debian: Stable, universal, package management
  Ubuntu: User-friendly, LTS releases
  Linux Mint: Desktop-focused, Ubuntu-based
  Kali Linux: Security testing, penetration testing

Red Hat-based:
  RHEL: Enterprise, commercial support
  CentOS/Rocky: Community RHEL clones
  Fedora: Cutting-edge, RHEL upstream
  openSUSE: Enterprise, community-driven

Arch-based:
  Arch Linux: Rolling release, DIY philosophy
  Manjaro: User-friendly Arch
  EndeavourOS: Arch-based, out-of-box

Specialized:
  Alpine: Lightweight, security-focused
  Gentoo: Source-based, highly customizable
  Slackware: Traditional, BSD-like
  LFS: Linux From Scratch, educational
```

## 🔧 System Installation and Setup

### System Requirements
```bash
# Minimum Requirements
CPU: x86_64 or ARM64
RAM: 1GB+ (2GB+ recommended)
Storage: 10GB+ (20GB+ recommended)
Network: Ethernet or WiFi

# Recommended Homelab Setup
CPU: 4+ cores with virtualization support
RAM: 8GB+ (16GB+ for virtualization)
Storage: 100GB+ SSD
Network: Gigabit Ethernet
Virtualization: VT-x/AMD-V support

# Server vs Desktop
Server: Minimal install, CLI-focused
Desktop: GUI applications, development tools
Container: Lightweight, security-hardened
Virtualization: Host OS, virtualization tools
```

### Ubuntu Server Installation
```bash
# Download Ubuntu Server
wget https://releases.ubuntu.com/22.04.3/ubuntu-22.04.3-live-server-amd64.iso

# Create Bootable USB
# On Linux
sudo dd if=ubuntu-22.04.3-live-server-amd64.iso of=/dev/sdX bs=4M status=progress

# On Windows
# Use Rufus or balenaEtcher
# Select ISO and USB drive
# Choose GPT partition scheme
# Start writing

# Installation Steps
1. Boot from USB/ISO
2. Select "Install Ubuntu Server"
3. Choose language and keyboard
4. Configure network (DHCP or static)
5. Configure proxy (if needed)
6. Configure mirror archive
7. Configure disk partitioning:
   - Use entire disk
   - Set up LVM (recommended)
   - Create separate /home partition
8. Create user account
9. Install SSH server
10. Select additional software
11. Install GRUB bootloader
12. Reboot and complete setup
```

### Post-Installation Configuration
```bash
# System Update
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

# Essential Packages
sudo apt install -y \
  curl \
  wget \
  git \
  vim \
  htop \
  tree \
  unzip \
  build-essential \
  software-properties-common

# Configure SSH
sudo nano /etc/ssh/sshd_config

# SSH Security Settings
Port 2222                    # Change from default 22
PermitRootLogin no          # Disable root login
PasswordAuthentication no     # Use key-based auth
PubkeyAuthentication yes     # Enable key auth
UsePAM no                  # Disable PAM
X11Forwarding no           # Disable X11 forwarding

# Restart SSH Service
sudo systemctl restart sshd
sudo systemctl enable sshd

# Configure Firewall
sudo ufw enable
sudo ufw allow 2222/tcp    # Custom SSH port
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow from 192.168.1.0/24  # Internal network
```

## 📁 Filesystem Management

### Linux Filesystem Hierarchy
```bash
# Standard Directory Structure
/                # Root directory
/bin             # Essential user binaries
/sbin            # System binaries
/lib             # Essential libraries
/lib64           # 64-bit libraries
/usr              # User programs
  /bin           # User binaries
  /sbin          # User system binaries
  /lib           # User libraries
  /local         # Local software
/etc              # Configuration files
/home             # User home directories
/root             # Root user home
/tmp              # Temporary files
/var              # Variable data
  /log           # System logs
  /cache         # Application cache
  /www           # Web server files
/boot             # Boot loader files
/opt              # Optional software
/mnt              # Mount points
/media             # Removable media
/proc             # Process information
/sys              # Kernel information
/dev              # Device files
/run              # Runtime data
/srv              # Service data
```

### Disk Partitioning and Mounting
```bash
# Partition Types
MBR (Master Boot Record):
  Max Partitions: 4 primary
  Max Disk Size: 2TB
  Legacy Support: BIOS systems
  Compatibility: Older systems

GPT (GUID Partition Table):
  Max Partitions: 128+
  Max Disk Size: 9.4ZB
  Modern Support: UEFI systems
  Recommended: Modern systems

# Filesystem Types
ext4: Standard Linux filesystem
  Features: Journaling, extents, delayed allocation
  Max File Size: 16TB
  Max Volume Size: 1EB
  Recommended: General use

xfs: High-performance filesystem
  Features: Journaling, allocation groups, extents
  Max File Size: 8EB
  Max Volume Size: 8EB
  Recommended: Large files, high performance

btrfs: Modern copy-on-write filesystem
  Features: Snapshots, compression, checksums
  Max File Size: 16EB
  Max Volume Size: 16EB
  Recommended: Advanced features, snapshots

zfs: Advanced filesystem with volume management
  Features: Snapshots, compression, deduplication, RAID
  Max File Size: 16EB
  Max Volume Size: 256ZB
  Recommended: Enterprise, data integrity
```

### Storage Management Commands
```bash
# Disk Information
lsblk                    # List block devices
fdisk -l                  # Partition table
gdisk -l                  # GPT partition table
df -h                      # Disk usage
du -sh /path/to/dir         # Directory size

# Partitioning
sudo fdisk /dev/sda        # MBR partitioning
sudo gdisk /dev/sda        # GPT partitioning
sudo parted /dev/sda        # Advanced partitioning

# Filesystem Creation
sudo mkfs.ext4 /dev/sda1   # Create ext4
sudo mkfs.xfs /dev/sda2     # Create xfs
sudo mkfs.btrfs /dev/sda3  # Create btrfs

# Mounting
sudo mount /dev/sda1 /mnt/data  # Mount filesystem
sudo umount /mnt/data             # Unmount filesystem

# fstab Configuration
sudo nano /etc/fstab

# fstab Entry Format
UUID=device-uuid /mount-point filesystem options dump pass
UUID=1234-abcd-5678-efgh-9012-ijklmnop /data ext4 defaults 0 2

# LVM Setup
sudo pvcreate /dev/sda2        # Create physical volume
sudo vgcreate vg0 /dev/sda2      # Create volume group
sudo lvcreate -n data -l 100%FREE vg0  # Create logical volume
sudo mkfs.ext4 /dev/vg0/data    # Create filesystem
sudo mount /dev/vg0/data /mnt/data  # Mount logical volume
```

## 🔐 User and Security Management

### User Management
```bash
# User Creation and Management
sudo useradd -m -s /bin/bash username    # Create user
sudo useradd -m -s /bin/zsh -G sudo,adm username  # User with groups

# User Modification
sudo usermod -aG sudo username               # Add to group
sudo usermod -s /bin/zsh username          # Change shell
sudo usermod -l newname username           # Change username

# Password Management
sudo passwd username                         # Change password
sudo chage -l username                       # Password info
sudo chage -M 90 username                     # Set max age
sudo chage -W 7 username                      # Warning days

# Group Management
sudo groupadd developers                    # Create group
sudo groupmod -n newname oldname            # Rename group
sudo groupdel developers                     # Delete group

# User Information
id username                              # User ID and groups
groups username                        # Group membership
finger username                          # User information
last username                           # Login history
```

### File Permissions
```bash
# Permission Basics
# File permissions: rwxrwxrwx
# User | Group | Others
# Read (4), Write (2), Execute (1)

# Permission Commands
chmod 755 script.sh                   # rwxr-xr-x
chmod +x script.sh                     # Add execute
chmod 644 config.txt                  # rw-r--r--
chmod -R 755 /var/www                 # Recursive

# Permission Examples
chmod 750 private_dir                  # rwxr-x---
chmod 644 public_file                   # rw-r--r--
chmod 600 private_file                  # rw-------
chmod 777 shared_dir                   # rwxrwxrwx

# Ownership
chown user:group file.txt            # Change owner and group
chown -R user:group /var/www        # Recursive ownership

# Special Permissions
chmod u+s executable                 # Setuid bit
chmod g+s directory                  # Setgid bit
chmod +t sticky_dir                   # Sticky bit

# Access Control Lists (ACL)
sudo apt install acl
getfacl file.txt                     # View ACL
setfacl -m u:user:rw file.txt    # Set ACL
setfacl -x u:user file.txt         # Remove ACL
```

### SSH Key Management
```bash
# Generate SSH Key Pair
ssh-keygen -t ed25519 -C "user@hostname"
ssh-keygen -t rsa -b 4096 -C "user@hostname"

# Key Types
ed25519: Elliptic curve, modern, secure
rsa: Traditional, widely supported
ecdsa: Elliptic curve, deprecated
dsa: Digital Signature Algorithm, deprecated

# Copy Public Key to Server
ssh-copy-id user@server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server

# Manual Key Installation
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1..." >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# SSH Agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l                              # List loaded keys
ssh-add -D                                # Remove all keys

# SSH Config File
nano ~/.ssh/config

# SSH Config Example
Host server1
    HostName 192.168.1.100
    User admin
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

Host server2
    HostName server2.homelab.local
    User deploy
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

## 🔄 Process and Service Management

### Process Management
```bash
# Process Information
ps aux                    # All processes
ps -ef                   # Full format
ps aux --forest          # Process tree
pstree                   # Process tree view

# Process Control
kill PID                   # Terminate process
kill -9 PID               # Force kill
killall process_name      # Kill by name
pkill pattern              # Kill by pattern

# Resource Monitoring
top                        # Interactive process viewer
htop                       # Enhanced top
atop                        # Process accounting
iotop                       # I/O monitoring

# Background Processes
command &                   # Run in background
jobs                        # List background jobs
fg %1                       # Bring to foreground
bg %1                        # Send to background
kill %1                      # Kill background job
```

### Systemd Service Management
```bash
# Service Status and Control
systemctl status service-name           # Service status
systemctl start service-name            # Start service
systemctl stop service-name             # Stop service
systemctl restart service-name          # Restart service
systemctl reload service-name          # Reload configuration

# Service Enablement
systemctl enable service-name           # Enable at boot
systemctl disable service-name          # Disable at boot
systemctl is-enabled service-name      # Check if enabled

# Service Information
systemctl list-units --type=service   # List all services
systemctl list-units --failed         # List failed services
systemctl list-unit-files              # Available unit files

# Service Logs
journalctl -u service-name               # Service logs
journalctl -f -u service-name          # Follow logs
journalctl --since "1 hour ago"        # Recent logs

# Custom Service Creation
sudo nano /etc/systemd/system/myservice.service

# Service File Example
[Unit]
Description=My Custom Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/myservice
Restart=always
User=myuser
Group=myuser

[Install]
WantedBy=multi-user.target

# Enable Custom Service
sudo systemctl daemon-reload
sudo systemctl enable myservice
sudo systemctl start myservice
```

## 📊 System Monitoring

### Resource Monitoring
```bash
# System Resource Commands
free -h                    # Memory usage
free -h -s 1              # Memory usage every second
df -h                      # Disk usage
du -sh /var/*              # Directory sizes
lscpu                      # CPU information
lsblk                       # Block devices
lsusb                       # USB devices
lspci                       # PCI devices

# Performance Monitoring
vmstat 1                   # Virtual memory statistics
iostat 1                   # I/O statistics
mpstat 1                   # Multiprocessor statistics
sar                         # System activity reporter

# Temperature Monitoring
sensors                     # Hardware sensors
watch sensors               # Continuous monitoring

# Network Monitoring
ip addr show                # Network interfaces
ip route show              # Routing table
ss -tulpn                  # Network connections
netstat -tulpn              # Legacy network stats
```

### Log Management
```bash
# System Logs
journalctl                     # All systemd logs
journalctl -f                  # Follow logs
journalctl --since "1 hour ago"  # Recent logs
journalctl -u service-name     # Service logs
journalctl -p err              # Error logs only

# Traditional Logs
tail -f /var/log/syslog          # System log
tail -f /var/log/auth.log         # Authentication log
tail -f /var/log/kern.log         # Kernel log
tail -f /var/log/dmesg             # Boot messages

# Log Rotation Configuration
sudo nano /etc/logrotate.conf

# Log Rotation Example
/var/log/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root adm
    postrotate
        systemctl reload rsyslog
    endscript
}

# Manual Log Rotation
sudo logrotate -f /etc/logrotate.conf
```

## 🌐 Network Configuration

### Network Interface Management
```bash
# Network Information
ip addr show                 # IP addresses
ip link show                  # Interface status
ip route show                # Routing table
ip neigh show                 # ARP table

# Interface Configuration
sudo ip link set eth0 up          # Enable interface
sudo ip link set eth0 down        # Disable interface
sudo ip addr add 192.168.1.100/24 dev eth0  # Add IP
sudo ip addr del 192.168.1.100/24 dev eth0  # Remove IP

# Network Configuration Files
sudo nano /etc/netplan/01-netcfg.yaml

# Netplan Configuration Example
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
    eth1:
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

# Apply Netplan Configuration
sudo netplan apply
```

### Network Troubleshooting
```bash
# Network Diagnostic Commands
ping -c 4 8.8.8.8           # Test connectivity
traceroute google.com           # Trace route
nslookup google.com             # DNS lookup
dig google.com                 # Advanced DNS lookup

# Port Scanning
nmap -sS -O target-host      # SYN scan with OS detection
nmap -p 1-1000 target-host   # Port range scan
nmap -sU target-host          # UDP scan

# Network Performance
iperf3 -c server-host        # Bandwidth test
iperf3 -s                    # Server mode
wget -O /dev/null http://example.com/large-file  # Download speed test

# Network Debugging
tcpdump -i eth0                # Packet capture
ss -tulpn                     # Network connections
ethtool eth0                    # Ethernet interface info
```

## 📦 Package Management

### APT (Debian/Ubuntu)
```bash
# Package Commands
sudo apt update                  # Update package lists
sudo apt upgrade                 # Upgrade packages
sudo apt full-upgrade            # Full system upgrade
sudo apt install package-name    # Install package
sudo apt remove package-name     # Remove package
sudo apt purge package-name      # Remove with config

# Package Information
apt search keyword              # Search packages
apt show package-name           # Package details
apt list --installed           # List installed
apt policy package-name        # Version and source

# Package Management
sudo apt autoremove            # Remove unused packages
sudo apt autoclean              # Clean cache
sudo apt clean                 # Full cache clean
dpkg -l                      # List all packages
dpkg -L package-name          # Package files
```

### YUM/DNF (Red Hat/Fedora)
```bash
# YUM Commands (Legacy)
sudo yum update                 # Update packages
sudo yum install package-name    # Install package
sudo yum remove package-name     # Remove package
sudo yum search keyword         # Search packages
yum info package-name          # Package information

# DNF Commands (Modern)
sudo dnf update                 # Update packages
sudo dnf install package-name    # Install package
sudo dnf remove package-name     # Remove package
sudo dnf search keyword         # Search packages
dnf info package-name          # Package information

# Repository Management
sudo dnf config-manager --add-repo repo-url
sudo dnf repolist                 # List repositories
sudo dnf makecache                # Rebuild cache
```

### Pacman (Arch Linux)
```bash
# Pacman Commands
sudo pacman -Sy                 # Update database
sudo pacman -Syu                # Update system
sudo pacman -S package-name       # Install package
sudo pacman -R package-name       # Remove package
sudo pacman -Ss keyword          # Search packages
pacman -Si package-name         # Package information

# Package Management
sudo pacman -Q                 # Query installed
sudo pacman -Qe                # Explicitly installed
sudo pacman -Qdt               # Dependencies as targets
sudo pacman -Sc                 # Clean cache
sudo pacman -Rns package-name   # Remove with deps
```

## 🔧 System Optimization

### Performance Tuning
```bash
# Kernel Parameters
sudo sysctl -a                  # Show all parameters
sudo sysctl -w parameter=value    # Change parameter
sudo nano /etc/sysctl.conf         # Permanent changes

# Performance Tuning
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.rmem_max=16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max=16777216' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p                 # Apply changes

# CPU Frequency Scaling
sudo apt install cpufrequtils
cpufreq-info                   # CPU frequency info
cpufreq-set -g performance    # Set governor

# I/O Scheduler
echo 'deadline' | sudo tee /sys/block/sda/queue/scheduler
echo 'noop' | sudo tee /sys/block/sdb/queue/scheduler

# Filesystem Mount Options
# Add to /etc/fstab
UUID=device-uuid /data ext4 defaults,noatime,discard 0 2
```

### Resource Limits
```bash
# Ulimits Configuration
ulimit -a                       # Show all limits
ulimit -n 65536                 # Increase file descriptors

# Permanent Ulimits
sudo nano /etc/security/limits.conf

# Limits Configuration Example
username soft nofile 65536
username hard nofile 65536
username soft nproc 32768
username hard nproc 32768

# Systemd Resource Limits
sudo systemctl set-property service-name.service MemoryLimit=1G
sudo systemctl set-property service-name.service CPUQuota=50%
```

## 🛡️ Security Hardening

### System Security
```bash
# Security Updates
sudo apt update && sudo apt upgrade -y
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Remove Unused Services
sudo systemctl stop telnet.socket
sudo systemctl disable telnet.socket
sudo apt remove telnetd -y

# File Permissions
sudo chmod 600 /etc/ssh/sshd_config
sudo chmod 644 /etc/passwd
sudo chmod 600 /etc/shadow
sudo chmod 644 /etc/group
sudo chmod 600 /etc/gshadow

# Immutable Files
sudo chattr +i /etc/resolv.conf
sudo chattr +i /etc/hosts
sudo lsattr /etc/resolv.conf          # Check attributes
sudo chattr -i /etc/resolv.conf          # Remove attribute
```

### Firewall Configuration
```bash
# UFW (Uncomplicated Firewall)
sudo ufw enable                     # Enable firewall
sudo ufw default deny incoming       # Default deny policy
sudo ufw default allow outgoing        # Allow outgoing
sudo ufw allow 22/tcp                # Allow SSH
sudo ufw allow 80/tcp               # Allow HTTP
sudo ufw allow 443/tcp              # Allow HTTPS
sudo ufw deny from 192.168.1.100    # Block specific IP
sudo ufw status                      # Show rules

# iptables (Advanced)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -j DROP
sudo iptables-save > /etc/iptables/rules.v4

# nftables (Modern)
sudo nft add rule inet filter input tcp dport 22 accept
sudo nft add rule inet filter input tcp dport 80 accept
sudo nft add rule inet filter input drop
sudo nft list ruleset
```

### Intrusion Detection
```bash
# Install Security Tools
sudo apt install -y fail2ban rkhunter chkrootkit aide

# Fail2Ban Configuration
sudo nano /etc/fail2ban/jail.local

# Fail2Ban Example
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

# Start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Rootkit Detection
sudo rkhunter --check --sk
sudo chkrootkit

# File Integrity Check
sudo aide --init
sudo aide --check
```

## 🚨 Troubleshooting

### System Diagnostics
```bash
# Boot Issues
sudo journalctl -b -p err    # Boot errors
sudo dmesg | grep -i error  # Kernel errors
sudo fsck -y /dev/sda1       # Filesystem check

# Performance Issues
sudo iotop                     # I/O monitoring
sudo nethogs                   # Network monitoring
sudo perf top                   # Performance profiling

# Resource Issues
free -h                       # Memory usage
df -h                         # Disk usage
ps aux --sort=-%cpu          # CPU usage
ps aux --sort=-%mem          # Memory usage

# Network Issues
ping -c 4 8.8.8.8           # Connectivity test
traceroute google.com           # Route tracing
nslookup domain.com            # DNS resolution
```

### Recovery Procedures
```bash
# System Rescue
# Boot from Live USB/ISO
mount /dev/sda1 /mnt          # Mount root filesystem
mount --bind /dev /mnt/dev       # Mount devices
mount --bind /proc /mnt/proc     # Mount proc
mount --bind /sys /mnt/sys       # Mount sys

# Chroot to System
sudo chroot /mnt /bin/bash

# Reset Password
passwd root                    # Reset root password
passwd username                # Reset user password

# Bootloader Repair
sudo grub-install /dev/sda
sudo update-grub

# Backup Configuration
sudo tar czf system-backup.tar.gz /etc /home /var
sudo scp system-backup.tar.gz backup@server:/backups/
```

## 📖 Further Reading

### Documentation
- [Linux Documentation](https://www.kernel.org/doc/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs/)
- [Red Hat Documentation](https://access.redhat.com/documentation/)
- [Arch Linux Wiki](https://wiki.archlinux.org/)

### Books and Courses
- [The Linux Command Line](https://linuxcommandlibrary.com/)
- [Linux Bible](https://www.wiley.com/en-us/Linux+Bible-p-97811194972)
- [Linux Foundation Training](https://training.linuxfoundation.org/)

### Communities
- Reddit: r/linux4noobs, r/linuxadmin, r/homelab
- LinuxQuestions.org
- Stack Exchange: Unix & Linux
- Local Linux User Groups (LUGs)

### Advanced Topics
- Containerization with Docker/Podman
- Kernel compilation and tuning
- High availability clustering
- Security auditing and compliance
- Cloud infrastructure management

---

**Ready to dive deeper?** Check our [System Administration](index.md) overview for comprehensive admin planning!

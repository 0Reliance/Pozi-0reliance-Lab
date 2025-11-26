---
title: KVM Virtualization Setup
description: Complete guide for KVM hypervisor installation and management in homelab environments
---

# KVM Virtualization Setup

Kernel-based Virtual Machine (KVM) is a powerful, open-source virtualization solution for Linux homelabs. This guide covers KVM installation, VM management, network configuration, and performance optimization.

## 🖥️ KVM Fundamentals

### Virtualization Concepts
```bash
# KVM Architecture Overview

Host System (Hypervisor):
  Role: Physical server running KVM
  Requirements: Linux with virtualization support
  Components: QEMU, libvirt, virt-manager
  Management: CLI tools, web interfaces, GUI

Guest Systems (Virtual Machines):
  Role: Operating systems running on host
  Types: Linux, Windows, BSD, specialty OSes
  Resources: CPU cores, RAM, storage, network
  Isolation: Hardware-level virtualization

Storage Pool:
  Role: Centralized storage for VM disks
  Types: Local filesystem, LVM, NFS, iSCSI
  Management: libvirt storage pools
  Formats: qcow2, raw, vmdk, vdi

Virtual Network:
  Role: Network connectivity for VMs
  Types: NAT, bridged, routed, isolated
  Management: libvirt virtual networks
  Features: DHCP, DNS, port forwarding
```

### Hardware Requirements
```bash
# Minimum System Requirements
CPU: x86_64 with VT-x/AMD-V support
Cores: 2+ physical cores (4+ recommended)
RAM: 8GB+ (16GB+ recommended)
Storage: 100GB+ SSD (500GB+ recommended)
Network: Gigabit Ethernet (10GbE recommended)

# Recommended Homelab Specifications
CPU: Intel i7/i9 or AMD Ryzen 7/9
Cores: 8+ physical cores with hyperthreading
RAM: 32GB+ DDR4/DDR5
Storage: 1TB+ NVMe SSD for VMs
Network: 10GbE or multiple Gigabit interfaces
GPU: Optional for GPU passthrough
```

## 🔧 KVM Installation

### System Preparation
```bash
# Check CPU Virtualization Support
egrep -c '(vmx|svm)' /proc/cpuinfo
# Should return > 0 if virtualization is supported

# Check KVM Module Support
kvm-ok
# Should report "KVM acceleration can be used"

# Install Required Packages (Ubuntu/Debian)
sudo apt update
sudo apt install -y \
  qemu-kvm \
  libvirt-daemon-system \
  libvirt-clients \
  bridge-utils \
  virtinst \
  virt-manager \
  virt-viewer \
  ovmf \
  swtpm \
  cpu-checker

# Install Required Packages (CentOS/RHEL)
sudo dnf groupinstall -y "Virtualization Host"
sudo dnf install -y \
  virt-manager \
  libvirt-daemon-config-network \
  virt-install

# Add User to libvirt Group
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
newgrp libvirt

# Start and Enable Services
sudo systemctl enable --now libvirtd
sudo systemctl enable --now virtlogd

# Verify Installation
virsh list --all
sudo virsh net-list --all
```

### Network Configuration
```bash
# Create Bridged Network
# Edit network configuration
sudo nano /etc/netplan/01-netcfg.yaml

# Bridge Configuration Example
network:
  version: 2
  renderer: networkd
  ethernets:
    enp3s0:
      dhcp4: no
  bridges:
    br0:
      interfaces: [enp3s0]
      dhcp4: yes
      parameters:
        stp: false
        forward-delay: 0

# Apply Network Configuration
sudo netplan apply

# Verify Bridge
ip addr show br0
brctl show br0

# Create Virtual Network for VMs
sudo virsh net-define /dev/stdin <<EOF
<network>
  <name>homelab-net</name>
  <forward mode='nat'>
    <nat>
      <port start='1024' end='65535'/>
    </nat>
  </forward>
  <bridge name='virbr1' stp='on' delay='0'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.100' end='192.168.122.200'/>
    </dhcp>
  </ip>
</network>
EOF

# Start and Autostart Network
sudo virsh net-start homelab-net
sudo virsh net-autostart homelab-net
```

## 🖥️ VM Creation and Management

### Creating VMs with virt-manager (GUI)
```bash
# Launch virt-manager
virt-manager

# VM Creation Steps:
1. Click "Create new virtual machine"
2. Choose installation method:
   - Local install media (ISO)
   - Network install (PXE)
   - Import existing disk image
3. Select ISO image
4. Configure memory and CPU
5. Create disk image
6. Configure network
7. Complete installation

# VM Management in virt-manager:
- Start/Stop/Reboot VMs
- Console access
- Resource adjustment
- Snapshot management
- Clone VMs
```

### Creating VMs with virt-install (CLI)
```bash
# Create Ubuntu Server VM
virt-install \
  --name ubuntu-server \
  --memory 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/ubuntu-server.qcow2,size=50 \
  --cdrom /path/to/ubuntu-22.04.iso \
  --network network=default \
  --graphics spice \
  --noautoconsole

# Create Windows 11 VM (with UEFI)
virt-install \
  --name windows11 \
  --memory 8192 \
  --vcpus 4 \
  --disk path=/var/lib/libvirt/images/windows11.qcow2,size=100 \
  --cdrom /path/to/windows11.iso \
  --disk path=/path/to/virtio-win.iso,device=cdrom \
  --network network=default \
  --os-variant win10 \
  --features smm.state=on \
  --cpu host-passthrough \
  --graphics spice

# Create Docker Host VM
virt-install \
  --name docker-host \
  --memory 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/docker-host.qcow2,size=50 \
  --os-variant ubuntu20.04 \
  --network network=default \
  --graphics none \
  --import \
  --cloud-init /path/to/user-data \
  --cloud-init /path/to/meta-data
```

### VM Management Commands
```bash
# List VMs
virsh list --all

# Start/Stop/Reboot VMs
virsh start vm-name
virsh shutdown vm-name
virsh reboot vm-name
virsh destroy vm-name    # Force stop

# Pause/Resume VMs
virsh suspend vm-name
virsh resume vm-name

# VM Information
virsh dominfo vm-name
virsh domblklist vm-name
virsh domiflist vm-name

# Resource Management
virsh setmem vm-name 8G --live
virsh setvcpus vm-name 4 --live

# Snapshot Management
virsh snapshot-create-as vm-name snapshot-name
virsh snapshot-list vm-name
virsh snapshot-revert vm-name snapshot-name
virsh snapshot-delete vm-name snapshot-name
```

## 💾 Storage Management

### Storage Pools Configuration
```bash
# Create Directory-based Storage Pool
sudo virsh pool-define-as homelab-pool dir --target /var/lib/libvirt/homelab
sudo virsh pool-build homelab-pool
sudo virsh pool-start homelab-pool
sudo virsh pool-autostart homelab-pool

# Create LVM Storage Pool
sudo pvcreate /dev/sdb
sudo vgcreate homelab-vg /dev/sdb
sudo virsh pool-define-as homelab-lvm logical --target /dev/homelab-vg
sudo virsh pool-build homelab-lvm
sudo virsh pool-start homelab-lvm

# Create NFS Storage Pool
sudo mkdir -p /mnt/nfs-storage
sudo mount -t nfs nfs-server:/path/to/share /mnt/nfs-storage
sudo virsh pool-define-as nfs-storage netfs --target /mnt/nfs-storage --source-path /path/to/share --source-host nfs-server
sudo virsh pool-build nfs-storage
sudo virsh pool-start nfs-storage

# List Storage Pools
virsh pool-list --all
virsh pool-info homelab-pool

# Volume Management
virsh vol-create-as homelab-pool vm-disk.qcow2 50G
virsh vol-list homelab-pool
virsh vol-info homelab-pool vm-disk.qcow2
```

### Disk Formats and Optimization
```bash
# Convert Disk Formats
qemu-img convert -f raw -O qcow2 source.img destination.qcow2
qemu-img convert -f vmdk -O qcow2 source.vmdk destination.qcow2

# Resize Disk Images
qemu-img resize vm-disk.qcow2 +20G

# Disk Image Information
qemu-img info vm-disk.qcow2

# Create Sparse Disk (grow as needed)
qemu-img create -f qcow2 -o preallocation=off sparse-disk.qcow2 100G

# Create Preallocated Disk (full size allocated)
qemu-img create -f qcow2 -o preallocation=metadata full-disk.qcow2 100G

# Compact Disk Images (for qemu-img)
qemu-img convert -O qcow2 source.qcow2 compressed.qcow2 -c
```

## 🌐 Network Configuration

### Virtual Network Types
```bash
# NAT Network (Default)
# VMs access internet but not visible from host
# Easy setup, good for testing

# Bridged Network
# VMs appear as separate hosts on physical network
# Requires bridge configuration

# Routed Network
# VMs in separate subnet, host routes traffic
# Good for network segmentation

# Isolated Network
# VMs can only communicate with each other
# Good for testing clusters

# Macvtap Network
# VM directly connected to physical interface
# No bridge required, but host can't access VMs
```

### Advanced Network Setup
```bash
# Create Additional Virtual Networks
sudo virsh net-define /dev/stdin <<EOF
<network>
  <name>isolated-net</name>
  <bridge name='virbr2' stp='on' delay='0'/>
  <ip address='10.0.0.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='10.0.0.100' end='10.0.0.200'/>
    </dhcp>
  </ip>
</network>
EOF

# Configure Port Forwarding
sudo virsh net-update homelab-net add-last ip-dhcp-host \
  --xml "<host mac='52:54:00:ab:cd:ef' ip='192.168.122.150'/>" \
  --live --config

# Static IP Assignment for VM
<interface type='network'>
  <mac address='52:54:00:ab:cd:ef'/>
  <source network='homelab-net'/>
  <model type='virtio'/>
  <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
</interface>
```

## 🚀 Performance Optimization

### CPU and Memory Optimization
```bash
# CPU Pinning (Assign VMs to specific CPU cores)
virsh vcpupin vm-name 0 1 2 3

# Memory Ballooning (Dynamic memory adjustment)
virsh setmem vm-name 4G --live

# Huge Pages (Improve memory performance)
# Allocate huge pages
echo 2048 | sudo tee /proc/sys/vm/nr_hugepages

# Configure libvirt for huge pages
sudo mkdir /dev/hugepages
sudo mount -t hugetlbfs nodev /dev/hugepages
sudo chmod 755 /dev/hugepages

# VM Configuration with Huge Pages
<domain type='kvm'>
  <memory unit='KiB'>4194304</memory>
  <currentMemory unit='KiB'>4194304</currentMemory>
  <memoryBacking>
    <hugepages>
      <page size='2048' unit='KiB'/>
    </hugepages>
  </memoryBacking>
  <!-- ... rest of configuration ... -->
</domain>
```

### Storage Performance
```bash
# Storage Pool Optimization
# Use SSD for VM storage
# Configure proper caching modes
# Use LVM for better performance

# Cache Modes:
- none: No caching (safest, slowest)
- writethrough: Write cache, safe
- writeback: Write and read cache (fastest, risky)
- directsync: Direct I/O bypassing cache

# Example with cache mode
<disk type='file' device='disk'>
  <driver name='qemu' type='qcow2' cache='writeback'/>
  <source file='/var/lib/libvirt/images/vm-disk.qcow2'/>
  <target dev='vda' bus='virtio'/>
</disk>
```

### Network Performance
```bash
# Virtio Network Drivers (Best Performance)
<interface type='network'>
  <mac address='52:54:00:ab:cd:ef'/>
  <source network='homelab-net'/>
  <model type='virtio'/>
  <driver name='vhost'/>
  <tune>
    <sndbuf>0</sndbuf>
    <rcvbuf>0</rcvbuf>
  </tune>
</interface>

# Multi-Queue Networking (for high bandwidth)
<interface type='network'>
  <mac address='52:54:00:ab:cd:ef'/>
  <source network='homelab-net'/>
  <model type='virtio'/>
  <driver name='vhost' queues='4'/>
  <tune>
    <sndbuf>0</sndbuf>
    <rcvbuf>0</rcvbuf>
  </tune>
</interface>
```

## 🔧 Advanced Features

### GPU Passthrough
```bash
# Enable IOMMU in BIOS/UEFI
# Add kernel parameters
# Edit /etc/default/grub
GRUB_CMDLINE_LINUX="intel_iommu=on"  # For Intel
GRUB_CMDLINE_LINUX="amd_iommu=on"    # For AMD

# Update GRUB
sudo update-grub

# Load VFIO Modules
echo "vfio" | sudo tee -a /etc/modules
echo "vfio_iommu_type1" | sudo tee -a /etc/modules
echo "vfio_pci" | sudo tee -a /etc/modules
echo "vfio_virqfd" | sudo tee -a /etc/modules

# Blacklist GPU Driver
echo "blacklist nvidia" | sudo tee -a /etc/modprobe.d/blacklist-nvidia.conf
echo "blacklist nouveau" | sudo tee -a /etc/modprobe.d/blacklist-nvidia.conf

# VFIO Configuration
echo "options vfio-pci ids=10de:1234,10de:5678" | sudo tee -a /etc/modprobe.d/vfio.conf

# VM Configuration with GPU Passthrough
<devices>
  <hostdev mode='subsystem' type='pci' managed='yes'>
    <source>
      <address domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>
    </source>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
  </hostdev>
</devices>
```

### Live Migration
```bash
# Shared Storage Setup
# Use NFS, iSCSI, or shared LVM
# Configure same storage pool on both hosts

# Migration Setup
# Configure SSH between hosts
sudo systemctl enable libvirtd.socket
sudo systemctl enable libvirtd-ro.socket
sudo systemctl enable libvirtd-admin.socket

# Live Migration
virsh migrate --live --persistent vm-name qemu+ssh://destination-host/system

# Migration with Compression
virsh migrate --live --compressed --persistent vm-name qemu+ssh://destination-host/system

# Non-Live Migration (VM shutdown required)
virsh migrate --persistent vm-name qemu+ssh://destination-host/system
```

## 📊 Monitoring and Management

### VM Monitoring
```bash
# Resource Usage Monitoring
virsh dommemstat vm-name
virsh domblkinfo vm-name vda
virsh domifstat vm-name vnet0

# Live Monitoring
watch virsh list --all
watch virsh dominfo vm-name

# Performance Metrics
virsh domstats vm-name --cpu-total --block-total --interface-total

# XML Configuration Export
virsh dumpxml vm-name > vm-config.xml

# Import VM Configuration
virsh define vm-config.xml
```

### Web-based Management
```bash
# Install Cockpit for Web Management
sudo apt install cockpit cockpit-machines

# Enable and Start Cockpit
sudo systemctl enable --now cockpit.socket

# Access Cockpit Web Interface
https://server-ip:9090

# Features:
- VM lifecycle management
- Console access
- Resource monitoring
- Storage management
- Network configuration

# Alternative: Kimchi Web Interface
sudo apt install kimchi
sudo systemctl enable --now kimchid
```

## 🔒 Security Considerations

### VM Isolation
```bash
# SELinux for VM Security
sudo setenforce 1
sudo semanage fcontext -a -t svirt_image_t "/var/lib/libvirt/images(/.*)?"
sudo restorecon -R /var/lib/libvirt/images/

# AppArmor Configuration
sudo aa-complain /usr/libexec/qemu-kvm

# Network Filtering
<interface type='network'>
  <mac address='52:54:00:ab:cd:ef'/>
  <source network='homelab-net'/>
  <model type='virtio'/>
  <filterref filter='clean-traffic'/>
</interface>

# Disk Encryption
qemu-img create -f qcow2 -o encryption=on encrypted-disk.qcow2 50G
```

### Access Control
```bash
# Libvirt User Management
# Add users to libvirt group
sudo usermod -aG libvirt username

# Configure polkit rules
sudo nano /etc/polkit-1/localauthority/50-local.d/50-libvirt.pkla

[Allow libvirt management]
Identity=unix-group:libvirt
Action=org.libvirt.unix.manage
ResultAny=yes
ResultInactive=yes
ResultActive=yes
```

## 🚨 Troubleshooting

### Common Issues
```bash
# VM Won't Start
virsh start vm-name --verbose
sudo journalctl -u libvirtd
sudo virsh dominfo vm-name

# Network Issues
sudo virsh net-list --all
sudo virsh net-dumpxml homelab-net
brctl show
iptables -L -n

# Performance Issues
virsh vcpuinfo vm-name
virsh dommemstat vm-name
iostat -x 1
top

# Storage Issues
virsh pool-list --detail
virsh vol-list homelab-pool
df -h /var/lib/libvirt/images
```

### Debug Commands
```bash
# Libvirt Daemon Logs
sudo journalctl -u libvirtd
sudo journalctl -u virtlogd

# QEMU Process Information
ps aux | grep qemu
sudo strace -p qemu-pid

# Network Debugging
tcpdump -i virbr0
arp -n
ip neigh show
```

## 📋 Backup and Recovery

### VM Backup Strategies
```bash
# Offline Backup (VM Shutdown)
virsh shutdown vm-name
cp /var/lib/libvirt/images/vm-disk.qcow2 /backups/
virsh dumpxml vm-name > /backups/vm-name.xml

# Online Backup (Live Snapshot)
virsh snapshot-create-as vm-name backup-snap --disk-only
virsh dumpxml vm-name > /backups/vm-name.xml
cp /var/lib/libvirt/images/vm-disk.qcow2 /backups/

# Block Commit (Merge changes)
virsh blockcommit vm-name vda --active --verbose --pivot

# VM Restore
virsh define /backups/vm-name.xml
cp /backups/vm-disk.qcow2 /var/lib/libvirt/images/
virsh start vm-name
```

### Automated Backup Script
```bash
#!/bin/bash
# VM Backup Script

BACKUP_DIR="/backups/kvm"
VM_NAME="$1"
DATE=$(date +%Y%m%d-%H%M%S)

if [ -z "$VM_NAME" ]; then
    echo "Usage: $0 <vm-name>"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

# Create snapshot
virsh snapshot-create-as "$VM_NAME" "backup-$DATE" --disk-only --atomic

# Backup configuration
virsh dumpxml "$VM_NAME" > "$BACKUP_DIR/${VM_NAME}-${DATE}.xml"

# Copy disk images
virsh domblklist "$VM_NAME" | grep ^/ | while read line; do
    disk_path=$(echo "$line" | awk '{print $1}')
    disk_name=$(basename "$disk_path")
    cp "$disk_path" "$BACKUP_DIR/${disk_name}-${DATE}"
done

echo "Backup completed: ${VM_NAME}-${DATE}"
```

## 📖 Further Reading

### Documentation
- [KVM Documentation](https://www.linux-kvm.org/page/Documents)
- [libvirt Documentation](https://libvirt.org/docs.html)
- [QEMU Documentation](https://www.qemu.org/docs/master/)

### Communities
- Reddit: r/KVM, r/virtualization, r/homelab
- libvirt Mailing List
- QEMU Discourse Forums

### Advanced Topics
- High Availability (Pacemaker/Corosync)
- Container Integration (LXC, Docker)
- Cloud Management Platforms (OpenStack, Proxmox)

---

**Ready to dive deeper?** Check our [Virtualization](index.md) overview for comprehensive virtualization planning!

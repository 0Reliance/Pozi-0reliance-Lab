---
title: Getting Started
description: Complete beginner's guide to setting up your first homelab
---

# Getting Started with Homelabs

Welcome to the exciting world of homelabs! This guide will walk you through everything you need to know to set up your first homelab environment.

## 🤔 What is a Homelab?

A homelab is a personal computing environment where you can experiment, learn, and develop IT skills using real hardware and software. It's your personal data center for:

- Learning new technologies
- Testing configurations before production
- Hosting personal services
- Developing and testing applications
- Building technical skills

## 📋 Prerequisites

### Hardware Requirements

**Minimum Setup:**
- Computer with 8GB+ RAM
- 2+ CPU cores
- 100GB+ storage space
- Network connectivity

**Recommended Setup:**
- Dedicated server or desktop with 16GB+ RAM
- 4+ CPU cores
- 500GB+ storage (SSD preferred)
- Gigabit network connection
- UPS (Uninterruptible Power Supply)

### Software Requirements

- Operating System (Linux recommended: Ubuntu Server, Debian, Proxmox)
- Basic command line knowledge
- Text editor (VS Code, vim, nano)
- Network configuration knowledge

## 🏗️ Planning Your Homelab

### Define Your Goals

What do you want to accomplish with your homelab?

- **Learning**: Focus on diverse technologies and setups
- **Hosting**: Run personal services (media server, web hosting)
- **Development**: Application development and testing
- **Network Skills**: Routing, switching, security

### Network Planning

Consider these network aspects:

```bash
# Example network plan
Network: 192.168.1.0/24
Gateway: 192.168.1.1
DNS: 192.168.1.1, 8.8.8.8
Homelab subnet: 192.168.1.100-192.168.1.200
```

## 🚀 Step-by-Step Setup

### Step 1: Choose Your Platform

**Option A: Dedicated Server**
- Bare metal installation
- Best performance
- Full control

**Option B: Virtual Machine**
- Run on existing computer
- Resource sharing
- Easy to backup

**Option C: Cloud Server**
- Remote access
- Managed hardware
- Monthly costs

### Step 2: Install Operating System

For beginners, we recommend Ubuntu Server:

```bash
# Download Ubuntu Server
# Create bootable USB
# Install with these settings:
- Minimal installation
- OpenSSH server
- Standard system utilities
```

### Step 3: Basic System Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create user account (don't use root)
sudo adduser homelab
sudo usermod -aG sudo homelab

# Configure SSH
sudo nano /etc/ssh/sshd_config
# Add: PermitRootLogin no
# Add: PasswordAuthentication no

# Restart SSH
sudo systemctl restart ssh
```

### Step 4: Network Configuration

```bash
# Check current IP
ip addr show

# Set static IP (optional)
sudo nano /etc/netplan/01-netcfg.yaml

# Example configuration:
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [192.168.1.1, 8.8.8.8]

# Apply changes
sudo netplan apply
```

### Step 5: Install Essential Tools

```bash
# Basic utilities
sudo apt install -y curl wget git vim htop tree

# Docker (for containerization)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Portainer (Docker management)
docker volume create portainer_data
docker run -d -p 8000:8000 -p 9000:9000 \
    --name portainer --restart always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest
```

## 🗂️ Common Homelab Services

### File Storage
- **Nextcloud**: Personal cloud storage
- **Samba**: Windows file sharing
- **NFS**: Network file system

### Media Management
- **Plex**: Media server
- **Jellyfin**: Open-source alternative
- **Emby**: Media organization

### Development
- **GitLab**: Git repository management
- **Jenkins**: CI/CD pipeline
- **Docker Registry**: Container storage

### Monitoring
- **Grafana**: Dashboards and visualization
- **Prometheus**: Metrics collection
- **Uptime Kuma**: Uptime monitoring

## 📊 Resource Planning

### CPU Allocation
| Service | CPU Cores | Priority |
|---------|-----------|----------|
| Virtual Machines | 2-4 | High |
| Docker Containers | 1-2 | Medium |
| File Storage | 1 | Low |

### Memory Planning
| Service | RAM | Priority |
|---------|-----|----------|
| Virtual Machines | 4-8GB | High |
| Databases | 2-4GB | High |
| Media Server | 2-4GB | Medium |
| Monitoring | 1-2GB | Low |

## 🔧 Next Steps

After completing the basic setup:

1. **Read the [Best Practices](best-practices.md) guide**
2. **Set up your [Network Infrastructure](../homelab/network/)**
3. **Configure [Storage Systems](../homelab/storage/)**
4. **Implement [Security](security.md) measures**

## ❓ Common Questions

**Q: How much does a homelab cost?**
A: Entry-level setups can cost $200-500, while advanced setups may cost $1000+.

**Q: Can I use an old computer?**
A: Yes! Many homelabs start with repurposed hardware.

**Q: Do I need programming skills?**
A: Basic command line knowledge helps, but many services have web interfaces.

**Q: Is it secure?**
A: With proper security measures (covered in our Security guide), homelabs can be very secure.

## 🛠️ Troubleshooting

If you encounter issues:

1. Check network connectivity: `ping google.com`
2. Verify service status: `systemctl status service-name`
3. Check logs: `journalctl -u service-name`
4. Review our [Troubleshooting](troubleshooting.md) guide

---

**Ready to dive deeper?** Check out our [Homelab Projects](../homelab/) section for specific setup guides!

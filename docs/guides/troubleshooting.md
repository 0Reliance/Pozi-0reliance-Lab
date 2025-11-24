---
title: Troubleshooting
description: Common issues and solutions for homelab problems
---

# Homelab Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common homelab issues. Follow these systematic steps to identify and fix problems efficiently.

## 🔍 Diagnostic Workflow

### Step 1: Quick Assessment
Before diving deep, run these quick checks:

```bash
# System overview
uname -a                    # OS version
df -h                       # Disk space
free -h                     # Memory usage
uptime                      # System uptime
ps aux | head -20          # Running processes

# Network basics
ip addr show               # IP addresses
ping -c 4 8.8.8.8          # Internet connectivity
nslookup google.com        # DNS resolution
```

### Step 2: Recent Changes
Always check what changed recently:

```bash
# System updates
cat /var/log/dpkg.log | tail -20

# Docker changes
docker events --since 24h

# Git changes (if using version control)
git log --oneline --since="2 days ago"
```

## 🌐 Network Issues

### Can't Access Services

#### Symptom: Service not responding on browser
**Quick Check:**
```bash
# Is the service running?
docker ps | grep service-name
systemctl status service-name

# Is the port listening?
netstat -tlnp | grep :8080
ss -tlnp | grep :8080

# Local connection test
curl -I http://localhost:8080
```

**Common Solutions:**

1. **Service Not Running**
```bash
# Restart Docker container
docker-compose restart service-name

# Restart systemd service
sudo systemctl restart service-name
```

2. **Port Conflict**
```bash
# Find what's using the port
sudo lsof -i :8080
sudo netstat -tlnp | grep :8080

# Kill conflicting process
sudo kill -9 <PID>
```

3. **Firewall Blocking**
```bash
# Check UFW status
sudo ufw status

# Allow specific port
sudo ufw allow 8080/tcp

# Check iptables
sudo iptables -L -n | grep 8080
```

### DNS Resolution Problems

#### Symptom: Can't resolve domain names
**Diagnostic:**
```bash
# Test DNS servers
nslookup google.com 8.8.8.8
nslookup google.com 1.1.1.1

# Check current DNS
cat /etc/resolv.conf

# Test with different DNS
dig @8.8.8.8 google.com
```

**Solutions:**
```bash
# Update DNS servers
sudo nano /etc/netplan/01-netcfg.yaml
# Add:
nameservers:
  addresses: [8.8.8.8, 1.1.1.1]

# Apply changes
sudo netplan apply

# Restart networking
sudo systemctl restart systemd-resolved
```

### Slow Network Performance

#### Diagnostic:
```bash
# Test bandwidth
iperf3 -c server-ip

# Check for packet loss
ping -c 100 8.8.8.8

# Check network interface errors
cat /proc/net/dev
```

**Common Causes:**
- Bad Ethernet cable
- Switch port issues
- Driver problems
- Network congestion

## 💾 Storage Issues

### Out of Disk Space

#### Quick Check:
```bash
# Overall disk usage
df -h

# Find large files
find / -type f -size +1G 2>/dev/null | head -10

# Directory sizes
du -sh /var/log /tmp /home
du -sh /var/lib/docker
```

**Solutions:**

1. **Clean Docker:**
```bash
# Remove unused images, containers, volumes
docker system prune -a --volumes

# Clean specific
docker image prune -a
docker container prune
docker volume prune
```

2. **Clean Logs:**
```bash
# Clear system logs
sudo journalctl --vacuum-time=7d

# Clear specific logs
sudo truncate -s 0 /var/log/syslog
sudo truncate -s 0 /var/log/auth.log
```

3. **Remove Old Packages:**
```bash
# Remove old kernels
sudo apt autoremove
sudo apt autoclean

# Remove cached packages
sudo apt-get clean
```

### Permission Issues

#### Symptom: "Permission denied" errors
**Diagnostic:**
```bash
# Check file permissions
ls -la /path/to/file

# Check ownership
stat /path/to/file

# Check user groups
groups
```

**Common Solutions:**

1. **Fix Ownership:**
```bash
# Change ownership
sudo chown -R user:group /path/to/directory

# For Docker volumes
sudo chown -R 1000:1000 /path/to/volume
```

2. **Fix Permissions:**
```bash
# Standard file permissions
chmod 644 file.txt
chmod 755 directory

# Recursive fix (use carefully)
chmod -R 755 /path/to/directory
```

## 🐳 Docker Issues

### Container Won't Start

#### Diagnostic:
```bash
# Check container status
docker ps -a | grep container-name

# View logs
docker logs container-name

# Check container details
docker inspect container-name
```

**Common Issues:**

1. **Port Already in Use**
```bash
# Find conflicting container
docker ps | grep :8080

# Stop conflicting service
docker stop conflicting-container
```

2. **Volume Mount Issues**
```bash
# Check if mount points exist
ls -la /host/path

# Check permissions
ls -ld /host/path

# Fix permissions
sudo chown -R 1000:1000 /host/path
```

3. **Resource Limits**
```bash
# Check system resources
free -h
df -h

# Check Docker limits
docker system df
```

### Image Pull Failures

#### Symptom: Can't pull Docker images
**Diagnostic:**
```bash
# Test Docker Hub connectivity
curl -I https://registry-1.docker.io/v2/

# Check Docker daemon
sudo systemctl status docker

# Check Docker config
cat ~/.docker/config.json
```

**Solutions:**

1. **Restart Docker:**
```bash
sudo systemctl restart docker
sudo systemctl status docker
```

2. **Clear Docker Cache:**
```bash
# Clear build cache
docker builder prune -a

# Reset Docker completely
sudo systemctl stop docker
sudo rm -rf /var/lib/docker
sudo systemctl start docker
```

3. **Use Mirror:**
```bash
# Configure Docker registry mirror
sudo nano /etc/docker/daemon.json
{
  "registry-mirrors": ["https://mirror.gcr.io"]
}
sudo systemctl restart docker
```

## 🔧 System Performance Issues

### High CPU Usage

#### Diagnostic:
```bash
# Find CPU-intensive processes
top
htop

# Find specific process CPU usage
ps aux --sort=-%cpu | head -10

# Check CPU load average
uptime
cat /proc/loadavg
```

**Common Solutions:**

1. **Identify Process:**
```bash
# Find what's using CPU
sudo iotop
sudo atop

# Kill if necessary
sudo kill -9 <PID>
```

2. **Docker Container Issues:**
```bash
# Check container resource usage
docker stats

# Limit container resources
docker update --cpus="1.5" container-name
```

### High Memory Usage

#### Diagnostic:
```bash
# Check memory usage
free -h
cat /proc/meminfo

# Find memory-intensive processes
ps aux --sort=-%mem | head -10

# Check swap usage
swapon -s
```

**Solutions:**

1. **Clear Memory:**
```bash
# Clear page cache
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Clear swap
sudo swapoff -a
sudo swapon -a
```

2. **Optimize Services:**
```bash
# Reduce Docker memory limits
docker update --memory="2g" container-name

# Restart memory-hungry services
sudo systemctl restart service-name
```

## 🚨 Service-Specific Issues

### Web Server Problems

#### Nginx/Apache Issues:
```bash
# Check configuration syntax
sudo nginx -t
sudo apache2ctl configtest

# Check error logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/apache2/error.log

# Restart service
sudo systemctl restart nginx
sudo systemctl restart apache2
```

### Database Issues

#### MySQL/MariaDB:
```bash
# Check status
sudo systemctl status mysql

# Check logs
sudo tail -f /var/log/mysql/error.log

# Test connection
mysql -u root -p

# Check disk space
df -h /var/lib/mysql
```

#### PostgreSQL:
```bash
# Check status
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*/main.log

# Test connection
psql -U postgres
```

## 🔐 Security Issues

### Failed SSH Connections

#### Diagnostic:
```bash
# Check SSH status
sudo systemctl status ssh

# Test SSH connection locally
ssh localhost

# Check SSH configuration
sudo sshd -T

# View failed attempts
sudo tail -f /var/log/auth.log | grep sshd
```

**Solutions:**
```bash
# Restart SSH
sudo systemctl restart ssh

# Check configuration
sudo nano /etc/ssh/sshd_config

# Allow your IP if using restrictions
sudo ufw allow from YOUR_IP to any port 22
```

### Suspicious Activity

#### Detection:
```bash
# Check failed login attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# Check active connections
ss -tuln

# Check running processes
ps aux | grep -v "^\["
```

**Response:**
```bash
# Block suspicious IP
sudo ufw deny from SUSPICIOUS_IP

# Check for rootkits
sudo rkhunter --check --skip-keypress

# Update system
sudo apt update && sudo apt upgrade -y
```

## 📋 Quick Reference

### Essential Commands
```bash
# System status
systemctl status service-name
docker ps
docker logs container-name

# Network
ip addr show
ping -c 4 8.8.8.8
netstat -tlnp

# Storage
df -h
du -sh /directory
ls -la

# Processes
ps aux | grep process-name
top
htop

# Logs
journalctl -u service-name
tail -f /var/log/service.log
```

### Emergency Commands
```bash
# Emergency reboot (if frozen)
sudo echo b > /proc/sysrq-trigger

# Kill frozen process
sudo kill -9 <PID>

# Clear disk space fast
sudo apt autoremove && sudo apt autoclean
docker system prune -a --volumes
```

## 📞 Getting Help

### When to Ask for Help
- You've tried all diagnostic steps
- Issue persists after reboot
- Multiple services affected
- Hardware suspected failure

### What to Include When Asking
1. **System Info:** OS version, hardware specs
2. **Exact Error Messages:** Full error output
3. **What You've Tried:** List of attempted solutions
4. **Recent Changes:** Updates, new installations
5. **Configuration:** Relevant config files (sanitized)

### Helpful Communities
- Reddit: r/homelab, r/sysadmin
- Discord: Homelab servers
- Stack Overflow: Technical questions
- Official documentation: Service-specific docs

---

**Still stuck?** Start with the [Getting Started](getting-started.md) guide to ensure your basic setup is correct, then work through these troubleshooting steps systematically.

**Pro tip:** Document your solutions! Keep a personal log of issues you encounter and how you fixed them - it'll save you time in the future.

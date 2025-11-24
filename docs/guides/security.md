---
title: Security
description: Essential security measures to protect your homelab
---

# Homelab Security Guide

Security is crucial for any homelab environment. This guide covers essential practices to protect your data, services, and network from various threats while maintaining accessibility for legitimate use.

## 🛡️ Security Layers

### Defense in Depth Approach
```
Internet
    ↓
Firewall/Router
    ↓
Network Segmentation
    ↓
Host Security
    ↓
Application Security
    ↓
Data Protection
```

## 🔒 Network Security

### Firewall Configuration

#### Basic UFW Setup
```bash
# Reset firewall rules
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential services
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Allow homelab services (restrict to local network)
sudo ufw allow from 192.168.1.0/24 to any port 8080
sudo ufw allow from 192.168.1.0/24 to any port 8443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

#### Advanced iptables Rules
```bash
#!/bin/bash
# /usr/local/bin/firewall-setup.sh

# Flush existing rules
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X

# Default policies
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow SSH (rate limited)
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

### Network Segmentation

#### VLAN Configuration
```bash
# Create VLAN interfaces (example for Proxmox/Debian)
sudo ip link add link eth0 name eth0.10 type vlan id 10
sudo ip link set eth0.10 up
sudo ip addr add 192.168.10.1/24 dev eth0.10

# Management VLAN (10)
# Production VLAN (20)
# IoT VLAN (30)
# Guest VLAN (40)
```

#### Router ACLs
```bash
# Example router configuration
access-list 101 permit tcp 192.168.1.0 0.0.0.255 192.168.10.0 0.0.0.255 eq 22
access-list 101 permit tcp 192.168.1.0 0.0.0.255 192.168.10.0 0.0.0.255 eq 443
access-list 101 deny tcp any 192.168.20.0 0.0.0.255 eq 22
access-list 101 permit ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
```

## 🔐 Authentication & Access Control

### SSH Hardening

#### Secure SSH Configuration
```bash
# /etc/ssh/sshd_config

# Disable root login
PermitRootLogin no

# Use key-based authentication
PasswordAuthentication no
PubkeyAuthentication yes

# Change default port
Port 2222

# Limit users
AllowUsers homelab admin
AllowGroups ssh-users

# Security settings
Protocol 2
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable empty passwords
PermitEmptyPasswords no

# Use specific algorithms
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com
```

#### SSH Key Management
```bash
# Generate strong keys
ssh-keygen -t ed25519 -a 100 -C "homelab-key"

# Copy key to server
ssh-copy-id -i ~/.ssh/homelab-key.pub homelab@server-ip

# Test key-based login
ssh -i ~/.ssh/homelab-key homelab@server-ip
```

### User Management

#### Create Service Accounts
```bash
# Create system user for service
sudo adduser --system --group --home /var/lib/service service-name
sudo usermod -L service-name  # Lock password
sudo usermod -s /usr/sbin/nologin service-name

# Add to appropriate groups
sudo usermod -aG docker service-name
sudo usermod -aG audio service-name  # If needed for media services
```

#### Sudo Configuration
```bash
# /etc/sudoers.d/homelab

# Allow admin users full sudo
%admin ALL=(ALL:ALL) ALL

# Allow service-specific commands
service-name ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/systemctl restart service-name

# Limit sudo access
homelab ALL=(ALL) /usr/bin/apt update, /usr/bin/apt upgrade
```

## 🌐 SSL/TLS Configuration

### Let's Encrypt Setup

#### Install Certbot
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Configure Nginx for automatic renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### Obtain and Configure Certificates
```bash
# Get certificate for domain
sudo certbot --nginx -d homelab.example.com -d www.homelab.example.com

# Generate stronger certificate
sudo certbot --nginx --rsa-key-size 4096 -d homelab.example.com

# Test renewal
sudo certbot renew --dry-run
```

#### Nginx SSL Configuration
```nginx
# /etc/nginx/sites-available/homelab
server {
    listen 443 ssl http2;
    server_name homelab.example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/homelab.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/homelab.example.com/privkey.pem;
    
    # Modern SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Proxy to applications
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐳 Container Security

### Docker Security Best Practices

#### Container Hardening
```yaml
# docker-compose.yml with security settings
version: '3.8'
services:
  secure-service:
    image: service-name:latest
    container_name: secure-service
    restart: unless-stopped
    
    # Security options
    user: "1000:1000"  # Run as non-root
    read_only: true     # Read-only filesystem
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /var/log:noexec,nosuid,size=100m
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    
    # Network security
    networks:
      - homelab-net
    ports:
      - "127.0.0.1:8080:80"  # Bind to localhost only
    
    # Environment variables (use .env file for secrets)
    env_file:
      - .env.secure
    environment:
      - NODE_ENV=production
```

#### Docker Daemon Security
```bash
# /etc/docker/daemon.json
{
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "iptables": true,
  "ip-forward": false,
  "bridge": "none"
}
```

### Container Image Security

#### Security Scanning
```bash
# Install Docker Bench for Security
git clone https://github.com/docker/docker-bench-security.git
cd docker-bench-security
sudo sh docker-bench-security.sh

# Scan images with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image image-name:latest

# Regular security updates
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --update-db
```

## 📊 Monitoring & Detection

### Intrusion Detection

#### Fail2ban Setup
```bash
# Install fail2ban
sudo apt install fail2ban

# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
destemail = admin@example.com

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
```

#### Log Monitoring
```bash
# Monitor suspicious activity
sudo tail -f /var/log/auth.log | grep -i "failed\|invalid"

# Check for port scanning
sudo grep "port scan" /var/log/kern.log

# Monitor Docker logs
docker logs -f container-name | grep -i "error\|warning"
```

### Security Auditing

#### Automated Security Checks
```bash
#!/bin/bash
# /usr/local/bin/security-audit.sh

echo "=== Security Audit Report ===" > /var/log/security-audit.log
date >> /var/log/security-audit.log

# Check for failed logins
echo "Failed Login Attempts:" >> /var/log/security-audit.log
grep "Failed password" /var/log/auth.log | wc -l >> /var/log/security-audit.log

# Check open ports
echo "Open Ports:" >> /var/log/security-audit.log
netstat -tlnp | grep LISTEN >> /var/log/security-audit.log

# Check running Docker containers
echo "Docker Containers:" >> /var/log/security-audit.log
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}" >> /var/log/security-audit.log

# Check disk space
echo "Disk Usage:" >> /var/log/security-audit.log
df -h >> /var/log/security-audit.log

# Check for world-writable files
echo "World-Writable Files:" >> /var/log/security-audit.log
find / -type f -perm -002 2>/dev/null | head -20 >> /var/log/security-audit.log

echo "Audit Complete" >> /var/log/security-audit.log
```

## 🔒 Data Protection

### Encryption

#### Full Disk Encryption
```bash
# Setup LUKS encryption (during install or later)
sudo cryptsetup luksFormat /dev/sdb1
sudo cryptsetup open /dev/sdb1 encrypted_volume
sudo mkfs.ext4 /dev/mapper/encrypted_volume

# Add to /etc/crypttab for automatic mounting
echo "encrypted_volume /dev/sdb1 none luks" >> /etc/crypttab
```

#### Backup Encryption
```bash
#!/bin/bash
# /usr/local/bin/encrypted-backup.sh

SOURCE_DIR="/homelab/data"
BACKUP_FILE="/backup/homelab-$(date +%Y%m%d).tar.gz"
GPG_RECIPIENT="admin@example.com"

# Create encrypted backup
tar -czf - "$SOURCE_DIR" | gpg --trust-model always --encrypt -r "$GPG_RECIPIENT" > "$BACKUP_FILE.gpg"

# Verify backup
gpg --decrypt "$BACKUP_FILE.gpg" | tar -tzf - > /dev/null
if [ $? -eq 0 ]; then
    echo "Backup created and verified successfully"
else
    echo "Backup verification failed"
    rm "$BACKUP_FILE.gpg"
fi
```

### Secrets Management

#### Environment Variable Security
```bash
# .env.template (commit to git)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# .env.local (don't commit)
# Use generated secrets
openssl rand -base64 32  # For secret keys
pwgen -s 16 1            # For passwords
```

#### HashiCorp Vault Setup (Advanced)
```yaml
# docker-compose.yml for Vault
version: '3.8'
services:
  vault:
    image: vault:latest
    container_name: vault
    restart: unless-stopped
    environment:
      - VAULT_ADDR=http://localhost:8200
      - VAULT_DEV_ROOT_TOKEN_ID=dev-token
    ports:
      - "8200:8200"
    volumes:
      - vault_data:/vault/data
    command: vault server -dev

volumes:
  vault_data:
```

## 🚨 Incident Response

### Security Incident Checklist

#### Immediate Response
1. **Isolate affected systems**
   ```bash
   # Disconnect from network
   sudo ip link set eth0 down
   
   # Stop suspicious services
   sudo systemctl stop service-name
   docker stop suspicious-container
   ```

2. **Preserve evidence**
   ```bash
   # Create system snapshot
   sudo dd if=/dev/sda of=/forensic/image.dd bs=4M
   
   # Save logs
   sudo cp -r /var/log /forensic/logs-$(date +%Y%m%d)
   ```

3. **Assess damage**
   ```bash
   # Check for unauthorized access
   sudo last | head -20
   sudo grep "Accepted" /var/log/auth.log
   
   # Look for suspicious processes
   ps aux | grep -v "^\[" | sort -k10
   ```

### Recovery Procedures

#### System Restoration
```bash
# From encrypted backup
gpg --decrypt /backup/homelab-20231201.tar.gz.gpg | tar -xzf - /

# Verify integrity
find /homelab/data -type f -exec sha256sum {} \; > /tmp/checksums.txt
sha256sum -c /tmp/checksums.txt
```

#### Password Reset
```bash
# Reset all service passwords
for user in service1 service2 service3; do
    openssl rand -base64 16 | sudo passwd --stdin "$user"
done

# Rotate SSH keys
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/new_key
```

## 📋 Security Checklist

### Daily
- [ ] Review system logs for suspicious activity
- [ ] Check for failed login attempts
- [ ] Verify backup completion
- [ ] Monitor disk space and resource usage

### Weekly
- [ ] Update system packages
- [ ] Scan Docker images for vulnerabilities
- [ ] Review firewall logs
- [ ] Check SSL certificate expiry

### Monthly
- [ ] Run security audit script
- [ ] Test backup restoration
- [ ] Review user access permissions
- [ ] Update documentation

### Quarterly
- [ ] Conduct full security assessment
- [ ] Review and update security policies
- [ ] Perform penetration testing
- [ ] Update incident response procedures

---

**Remember**: Security is an ongoing process, not a one-time setup. Regular monitoring, updates, and education are essential for maintaining a secure homelab environment.

**Need help?** Check our [Troubleshooting](troubleshooting.md) guide for security-related issues!

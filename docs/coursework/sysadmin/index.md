# System Administration Fundamentals

## Overview

System administration is the practice of managing and maintaining computer systems and networks to ensure optimal performance, security, and reliability. This comprehensive curriculum covers essential skills for modern IT professionals.

## Core Competencies

### Operating Systems
```bash
# Linux Distributions and Use Cases
Distribution   | Family      | Use Case                | Package Manager
Ubuntu         | Debian      | Desktop, Cloud, DevOps   | apt, snap
CentOS/RHEL    | Red Hat    | Enterprise, Servers      | yum, dnf
Debian         | Debian      | Stable, Servers          | apt
Fedora         | Red Hat    | Cutting Edge, Development | dnf
Arch Linux     | Independent| Custom, Enthusiasts     | pacman
openSUSE       | SUSE       | Enterprise, Desktop      | zypp

# Windows Server Versions
Windows Server 2022: Latest stable release
Windows Server 2019: Previous LTS version
Windows Server Core: Minimal GUI, command-line focus
Azure Stack HCI: Hybrid cloud integration
```

### Essential System Administration Skills
```python
# Core Competency Areas
sysadmin_skills = {
    "system_management": {
        "installation": "OS installation and configuration",
        "updates": "Patch management and system updates",
        "performance": "Monitoring and optimization",
        "troubleshooting": "Problem diagnosis and resolution"
    },
    "user_management": {
        "authentication": "User account management",
        "authorization": "Permission and access control",
        "security": "Security policies and hardening",
        "auditing": "Activity logging and monitoring"
    },
    "network_management": {
        "configuration": "Network interface setup",
        "troubleshooting": "Connectivity issues",
        "services": "DNS, DHCP, routing",
        "security": "Firewalls and access control"
    },
    "storage_management": {
        "filesystems": "File system management",
        "backup": "Data protection strategies",
        "recovery": "Disaster recovery procedures",
        "monitoring": "Storage capacity planning"
    },
    "automation": {
        "scripting": "Bash, PowerShell, Python",
        "orchestration": "Ansible, Puppet, Chef",
        "monitoring": "Automated health checks",
        "documentation": "Automated documentation"
    }
}
```

## Learning Path

### Beginner Level (Foundation)
```bash
# Module 1: Basic System Administration
1. Operating System Fundamentals
   - Linux file system hierarchy
   - Windows system architecture
   - Command line basics
   - Graphical administration tools

2. User and Group Management
   - User account creation and deletion
   - Group management
   - Password policies
   - Basic permissions

3. File System Management
   - File operations and permissions
   - Directory structure
   - File system types
   - Basic disk management

4. Network Fundamentals
   - IP addressing basics
   - Network configuration
   - Basic troubleshooting
   - Network services overview
```

### Intermediate Level (Professional)
```bash
# Module 2: System Administration Professional
1. Advanced User Management
   - Security policies
   - Advanced permissions
   - Active Directory/LDAP
   - Single Sign-On

2. Service Management
   - Service configuration
   - Process management
   - Startup configuration
   - Performance tuning

3. Network Services
   - DNS configuration
   - DHCP setup
   - Web server administration
   - Database management

4. Security Administration
   - Firewall configuration
   - Intrusion detection
   - Security auditing
   - Incident response
```

### Advanced Level (Expert)
```bash
# Module 3: System Administration Expert
1. Enterprise Architecture
   - High availability design
   - Load balancing
   - Clustering solutions
   - Disaster recovery

2. Automation and Orchestration
   - Infrastructure as Code
   - Configuration management
   - Continuous integration
   - DevOps practices

3. Cloud Integration
   - Hybrid cloud management
   - Container orchestration
   - Cloud security
   - Multi-cloud strategies

4. Advanced Troubleshooting
   - Performance analysis
   - Capacity planning
   - Root cause analysis
   - Optimization techniques
```

## Operating System Fundamentals

### Linux System Administration
```bash
# Essential Linux Commands
# System Information
uname -a                    # System information
lsb_release -a             # Distribution info
hostnamectl                 # System hostname
free -h                    # Memory usage
df -h                      # Disk usage
uptime                      # System uptime

# Process Management
ps aux                     # Process list
top                         # Real-time processes
htop                        # Interactive process viewer
kill -9 PID                # Kill process
systemctl status service    # Service status

# User Management
useradd username            # Add user
userdel username            # Delete user
passwd username             # Change password
groups username             # User groups
chmod 755 file            # Change permissions
chown user:group file      # Change ownership

# Network Management
ip addr show                # IP addresses
ip route show               # Routing table
ss -tulnp                  # Network connections
ping google.com             # Network test
traceroute google.com       # Route trace
```

### Windows System Administration
```powershell
# Essential PowerShell Commands
# System Information
Get-ComputerInfo              # System information
Get-WmiObject -Class Win32_OperatingSystem  # OS info
Get-Process                  # Process list
Get-Service                  # Service list

# User Management
New-LocalUser -Name "username" -PasswordNeverExpires
Set-LocalUser -Name "username" -Password (Read-Host -AsSecureString "Password")
Add-LocalGroupMember -Group "Administrators" -Member "username"
Remove-LocalUser -Name "username"

# File System Management
Get-ChildItem -Path C:\ -Recurse     # List files
New-Item -Path "C:\temp" -ItemType Directory  # Create directory
Set-Acl -Path "file.txt" -AclObject $acl  # Set permissions

# Network Management
Get-NetIPAddress               # IP addresses
Get-NetAdapter                # Network adapters
Test-NetConnection            # Network connectivity
Get-NetTCPConnection         # TCP connections
```

## Security Fundamentals

### System Hardening
```bash
# Linux Security Hardening Checklist

# 1. Update System
apt update && apt upgrade -y
yum update -y

# 2. Configure Firewall
ufw enable                    # Ubuntu
firewall-cmd --permanent --add-service=ssh  # CentOS
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 3. Secure SSH
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# 4. Create Limited Users
useradd -m -s /bin/bash admin
usermod -aG sudo admin

# 5. Configure Logging
logrotate -f /etc/logrotate.conf
auditctl -w /etc/passwd -p wa -k passwd_changes

# 6. File System Permissions
chmod 600 /etc/ssh/sshd_config
chmod 644 /etc/passwd
chmod 600 /etc/shadow
```

### Windows Security Hardening
```powershell
# Windows Security Hardening

# 1. Update System
Install-Module -Name PSWindowsUpdate
Import-Module PSWindowsUpdate
Get-WindowsUpdate -AcceptAll -Install

# 2. Configure Windows Firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
New-NetFirewallRule -DisplayName "Allow SSH" -Direction Inbound -Protocol TCP -LocalPort 22

# 3. User Account Control
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1

# 4. Security Policies
secedit /export /cfg C:\secconfig.cfg
(Get-Content C:\secconfig.cfg).replace("PasswordComplexity = 0", "PasswordComplexity = 1") | Set-Content C:\secconfig.cfg
secedit /configure /db secedit.sdb /cfg C:\secconfig.cfg

# 5. Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false
Update-MpSignature
```

## Backup and Recovery

### Backup Strategies
```bash
# Linux Backup Strategies

# 1. File System Backup with rsync
rsync -avz --delete /home/ /backup/home/
rsync -avz --delete /etc/ /backup/etc/

# 2. System Image with tar
tar -czf system-backup-$(date +%Y%m%d).tar.gz --exclude=/proc --exclude=/sys --exclude=/dev --exclude=/backup /

# 3. Database Backup
mysqldump -u root -p --all-databases > mysql-backup-$(date +%Y%m%d).sql
pg_dumpall > postgres-backup-$(date +%Y%m%d).sql

# 4. Automated Backup Script
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup critical directories
tar -czf $BACKUP_DIR/home.tar.gz /home
tar -czf $BACKUP_DIR/etc.tar.gz /etc
mysqldump -u root -p$MYSQL_PASS --all-databases > $BACKUP_DIR/mysql.sql

# Cleanup old backups (keep 7 days)
find /backup -type d -mtime +7 -exec rm -rf {} \;
```

```powershell
# Windows Backup Strategies

# 1. Windows Server Backup
Add-WindowsFeature -Name Windows-Server-Backup
wbadmin start backup -backupTarget:D: -include:C:,E: -quiet

# 2. File System Backup with robocopy
robocopy C:\Users E:\Backup\Users /E /R:3 /W:5 /LOG+:C:\Logs\backup.log

# 3. System State Backup
wbadmin start systemstatebackup -backupTarget:D:

# 4. Scheduled Backup PowerShell Script
$BackupPath = "E:\Backup\$(Get-Date -Format 'yyyyMMdd')"
New-Item -ItemType Directory -Path $BackupPath -Force

# Backup files
Robocopy "C:\Users" "$BackupPath\Users" /E /COPYALL /R:3 /W:5

# Backup system state
wbadmin start systemstatebackup -backupTarget:$BackupPath -quiet

# Cleanup old backups
Get-ChildItem "E:\Backup" | Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Recurse -Force
```

## Monitoring and Performance

### System Monitoring
```bash
# Linux System Monitoring

# 1. Real-time Monitoring with htop
htop --sort-key=PERCENT_CPU

# 2. System Resource Monitoring
vmstat 1 5                   # System statistics
iostat -x 1 5               # I/O statistics
sar -u 1 5                  # CPU utilization
sar -r 1 5                  # Memory utilization
sar -n DEV 1 5              # Network statistics

# 3. Disk Usage Monitoring
df -h                        # Disk space
du -sh /var/log/*           # Directory sizes
inotifywait -m /var/log      # Monitor file changes

# 4. Log Monitoring
tail -f /var/log/syslog
journalctl -f -u nginx
grep "ERROR" /var/log/app.log | tail -20

# 5. Performance Monitoring Script
#!/bin/bash
while true; do
    echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% MEM: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
    sleep 60
done
```

```powershell
# Windows System Monitoring

# 1. Performance Counters
Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 5
Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 5
Get-Counter "\PhysicalDisk(_Total)\% Disk Time" -SampleInterval 1 -MaxSamples 5

# 2. Event Log Monitoring
Get-WinEvent -LogName System -MaxEvents 10 | Where-Object {$_.LevelDisplayName -eq "Error"}
Get-WinEvent -LogName Application -MaxEvents 10 | Where-Object {$_.LevelDisplayName -eq "Warning"}

# 3. Service Monitoring
Get-Service | Where-Object {$_.Status -eq "Stopped"} | Where-Object {$_.StartType -eq "Automatic"}

# 4. Performance Monitoring Script
while ($true) {
    $cpu = (Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples.CookedValue
    $mem = (Get-Counter "\Memory\Available MBytes").CounterSamples.CookedValue
    $disk = (Get-Counter "\PhysicalDisk(_Total)\% Disk Time").CounterSamples.CookedValue
    
    Write-Host "$(Get-Date): CPU: $cpu% MEM: $mem MB Disk: $disk%"
    Start-Sleep 60
}
```

## Automation and Scripting

### Shell Scripting
```bash
#!/bin/bash
# System Administration Script

# Configuration
LOG_FILE="/var/log/sysadmin.log"
BACKUP_DIR="/backup"
TEMP_DIR="/tmp"

# Functions
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

check_disk_space() {
    local threshold=90
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $usage -gt $threshold ]; then
        log_message "WARNING: Disk usage at ${usage}%"
        echo "Disk usage critical: ${usage}%"
    fi
}

backup_database() {
    local db_name=$1
    local backup_file="$BACKUP_DIR/${db_name}_$(date +%Y%m%d).sql"
    
    mysqldump -u root -p$MYSQL_PASS $db_name > $backup_file
    if [ $? -eq 0 ]; then
        log_message "SUCCESS: Database $db_name backed up"
        gzip $backup_file
    else
        log_message "ERROR: Database backup failed for $db_name"
    fi
}

system_health_check() {
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        log_message "WARNING: High CPU usage: ${cpu_usage}%"
    fi
    
    # Check memory usage
    local mem_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
    if (( $(echo "$mem_usage > 90" | bc -l) )); then
        log_message "WARNING: High memory usage: ${mem_usage}%"
    fi
    
    # Check disk space
    check_disk_space
    
    # Check services
    local services=("nginx" "mysql" "ssh")
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet $service; then
            log_message "ERROR: Service $service is not running"
            systemctl start $service
            log_message "INFO: Attempted to start $service"
        fi
    done
}

# Main execution
log_message "INFO: Starting system health check"
system_health_check
backup_database "wordpress"
log_message "INFO: System health check completed"
```

### PowerShell Scripting
```powershell
# System Administration PowerShell Script

# Configuration
$LogFile = "C:\Logs\sysadmin.log"
$BackupPath = "E:\Backup"
$TempPath = "C:\Temp"

# Functions
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "$Timestamp - $Message"
}

function Test-DiskSpace {
    $Threshold = 90
    $Disks = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3}
    
    foreach ($Disk in $Disks) {
        $Usage = [math]::Round((($Disk.Size - $Disk.FreeSpace) / $Disk.Size) * 100, 2)
        if ($Usage -gt $Threshold) {
            Write-Log "WARNING: Disk $($Disk.DeviceID) usage at ${Usage}%"
            Write-Host "Disk usage critical: $($Disk.DeviceID) - ${Usage}%"
        }
    }
}

function Backup-Database {
    param([string]$DatabaseName)
    $BackupFile = "$BackupPath\$DatabaseName\$(Get-Date -Format 'yyyyMMdd').bak"
    
    try {
        # SQL Server backup example
        Backup-SqlDatabase -ServerInstance "localhost" -Database $DatabaseName -BackupFile $BackupFile
        Write-Log "SUCCESS: Database $DatabaseName backed up"
        
        # Compress backup
        Compress-Archive -Path $BackupFile -Destination "$BackupFile.zip" -Force
        Remove-Item $BackupFile
    }
    catch {
        Write-Log "ERROR: Database backup failed for $DatabaseName"
    }
}

function Test-SystemHealth {
    # Check CPU usage
    $CPU = (Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples.CookedValue
    if ($CPU -gt 80) {
        Write-Log "WARNING: High CPU usage: $CPU%"
    }
    
    # Check memory usage
    $Memory = Get-WmiObject -Class Win32_OperatingSystem
    $MemoryUsage = [math]::Round((($Memory.TotalVisibleMemorySize - $Memory.FreePhysicalMemory) / $Memory.TotalVisibleMemorySize) * 100, 2)
    if ($MemoryUsage -gt 90) {
        Write-Log "WARNING: High memory usage: $MemoryUsage%"
    }
    
    # Check disk space
    Test-DiskSpace
    
    # Check services
    $Services = @("w3svc", "MSSQLSERVER", "Spooler")
    foreach ($Service in $Services) {
        $Svc = Get-Service -Name $Service -ErrorAction SilentlyContinue
        if ($Svc -and $Svc.Status -ne "Running") {
            Write-Log "ERROR: Service $Service is not running"
            Start-Service -Name $Service
            Write-Log "INFO: Attempted to start $Service"
        }
    }
}

# Main execution
Write-Log "INFO: Starting system health check"
Test-SystemHealth
Backup-Database "AdventureWorks"
Write-Log "INFO: System health check completed"
```

## Virtualization and Containers

### Virtual Machine Management
```bash
# KVM/QEMU Management

# List virtual machines
virsh list --all

# Create virtual machine
virt-install \
  --name webserver \
  --ram 2048 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/webserver.qcow2,size=20 \
  --cdrom /path/to/ubuntu-20.04.iso \
  --network bridge=virbr0

# Start/Stop VM
virsh start webserver
virsh shutdown webserver
virsh destroy webserver

# VM monitoring
virsh dominfo webserver
virsh dommemstat webserver
virsh domblkstat webserver

# Take snapshot
virsh snapshot-create-as webserver --name "backup-$(date +%Y%m%d)"
virsh snapshot-list webserver
virsh snapshot-revert webserver --name "backup-$(date +%Y%m%d)"
```

### Docker Container Management
```bash
# Docker Commands

# Image management
docker images
docker pull nginx:latest
docker build -t myapp:1.0 .
docker save -o myapp.tar myapp:1.0

# Container management
docker ps -a
docker run -d --name webserver -p 80:80 nginx:latest
docker stop webserver
docker start webserver
docker rm webserver

# Container monitoring
docker stats
docker logs webserver
docker inspect webserver

# Volume management
docker volume create data_volume
docker run -v data_volume:/data myapp:1.0
docker volume ls
docker volume inspect data_volume
```

## Practical Labs

### Lab 1: System Setup and Configuration
```bash
# Objectives
1. Install and configure Linux/Windows Server
2. Set up user accounts and permissions
3. Configure network services
4. Implement basic security measures
5. Create backup procedures

# Tasks
1. OS installation with minimal footprint
2. User and group creation
3. Service configuration (SSH, Web server)
4. Firewall setup
5. Backup script creation
6. Documentation of procedures
```

### Lab 2: Monitoring and Troubleshooting
```bash
# Objectives
1. Set up system monitoring
2. Analyze performance metrics
3. Troubleshoot common issues
4. Implement alerting
5. Create incident response procedures

# Tasks
1. Install monitoring tools
2. Configure performance alerts
3. Create troubleshooting checklist
4. Simulate and resolve issues
5. Document recovery procedures
```

## Certification Paths

### System Administration Certifications
```bash
# Linux Certifications
1. Linux Professional Institute (LPI)
   - LPIC-1: Junior Level Linux Administrator
   - LPIC-2: Advanced Level Linux Administrator
   - LPIC-3: Senior Level Linux Professional

2. Red Hat Certifications
   - RHCSA: Red Hat Certified System Administrator
   - RHCE: Red Hat Certified Engineer
   - RHCA: Red Hat Certified Architect

# Windows Certifications
1. Microsoft Certified: Azure Administrator Associate
2. Microsoft Certified: Windows Server Hybrid Administrator Associate
3. Microsoft Certified: Azure Security Engineer Associate

# General Certifications
1. CompTIA Server+
2. CompTIA Linux+
3. Certified System Administrator (CSA)
```

## Summary

System administration requires a broad skill set covering:

- **Operating Systems**: Linux and Windows expertise
- **Security**: System hardening and protection
- **Monitoring**: Performance and health monitoring
- **Automation**: Scripting and orchestration
- **Troubleshooting**: Problem diagnosis and resolution
- **Documentation**: Procedure documentation and knowledge management

Modern system administrators must be versatile, continuously learning new technologies, and able to manage complex heterogeneous environments.

## Further Reading

- [The Linux Documentation Project](https://tldp.org/)
- [Microsoft Docs - Windows Server](https://docs.microsoft.com/en-us/windows-server/)
- [Linux System Administration Course](https://www.linuxfoundation.org/training/sysadmin)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)

---

*This curriculum provides comprehensive coverage of system administration fundamentals for modern IT infrastructure management.*

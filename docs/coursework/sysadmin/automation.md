---
title: System Administration Automation
description: Comprehensive guide for automating system administration tasks in homelab environments
---

# System Administration Automation

Automation transforms repetitive system administration tasks into efficient, repeatable processes. This comprehensive guide covers automation strategies, tools, and best practices for homelab environments using shell scripting, configuration management, and orchestration frameworks.

## 🤖 Automation Fundamentals

### Automation Philosophy
```bash
# Automation Principles

Consistency:
  Goal: Standardized processes across systems
  Benefit: Reduced human error, predictable results
  Implementation: Configuration as code, version control
  Examples: User creation, service deployment, updates

Scalability:
  Goal: Manage multiple systems efficiently
  Benefit: Linear scaling of administrative effort
  Implementation: Orchestration, parallel execution
  Examples: Cluster management, batch operations

Reliability:
  Goal: Reduce manual intervention
  Benefit: 24/7 operation, faster recovery
  Implementation: Monitoring, automated remediation
  Examples: Self-healing systems, automated failover

Maintainability:
  Goal: Clear, documented automation
  Benefit: Easy updates, knowledge transfer
  Implementation: Modular design, comprehensive logging
  Examples: Reusable functions, template systems
```

### Automation Strategy
```bash
# Automation Maturity Levels

Level 1: Manual Automation
  Description: Manual script execution
  Tools: Shell scripts, batch files
  Use Case: One-time tasks, learning automation
  Limitations: Manual triggers, no error handling

Level 2: Scheduled Automation
  Description: Automated execution on schedule
  Tools: Cron, Task Scheduler, systemd timers
  Use Case: Regular maintenance, backups, updates
  Benefits: Consistent timing, reduced oversight

Level 3: Event-Driven Automation
  Description: Triggered by system events
  Tools: inotify, file watchers, webhooks
  Use Case: Real-time responses, immediate actions
  Examples: Auto-deployment on code change, security response

Level 4: Intelligent Automation
  Description: AI/ML-enhanced decision making
  Tools: Prometheus alerts, machine learning models
  Use Case: Predictive maintenance, auto-scaling
  Complexity: Advanced analytics, feedback loops
```

## 📜 Shell Scripting

### Bash Scripting Essentials
```bash
#!/bin/bash
# homelab-automation.sh
# Comprehensive homelab automation script

# Script metadata
set -euo pipefail  # Strict error handling
IFS=$'\n\t'       # Safe iteration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/homelab-automation.log"

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Error handling
error_handler() {
    local line_number=$1
    local error_code=$2
    log "ERROR" "Script failed at line $line_number with exit code $error_code"
    cleanup_on_exit
    exit "$error_code"
}

trap 'error_handler ${LINENO} $?' ERR
trap cleanup_on_exit EXIT

# Cleanup function
cleanup_on_exit() {
    log "INFO" "Performing cleanup tasks"
    # Remove temporary files, unlock resources, etc.
}

# Configuration validation
validate_config() {
    local config_file="$1"
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Configuration file $config_file not found"
        return 1
    fi
    
    # Validate required configuration sections
    if ! grep -q "backup_paths" "$config_file"; then
        log "ERROR" "backup_paths not specified in configuration"
        return 1
    fi
    
    log "INFO" "Configuration validation passed"
}

# System health check
check_system_health() {
    log "INFO" "Performing system health checks"
    
    # Check disk space
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if (( disk_usage > 80 )); then
        log "WARN" "Disk usage is ${disk_usage}%"
    fi
    
    # Check memory usage
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if (( mem_usage > 85 )); then
        log "WARN" "Memory usage is ${mem_usage}%"
    fi
    
    # Check critical services
    local services=("sshd" "networking" "cron")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            log "INFO" "Service $service is running"
        else
            log "ERROR" "Service $service is not running"
        fi
    done
}

# Backup automation
perform_backup() {
    local backup_source="$1"
    local backup_dest="$2"
    local backup_type="$3"
    
    log "INFO" "Starting $backup_type backup of $backup_source"
    
    # Create backup directory
    local backup_dir="$backup_dest/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    case "$backup_type" in
        "files")
            tar -czf "$backup_dir/files.tar.gz" -C "$(dirname "$backup_source")" "$(basename "$backup_source")"
            ;;
        "database")
            if command -v pg_dump >/dev/null 2>&1; then
                pg_dump "$backup_source" | gzip > "$backup_dir/database.sql.gz"
            elif command -v mysqldump >/dev/null 2>&1; then
                mysqldump "$backup_source" | gzip > "$backup_dir/database.sql.gz"
            else
                log "ERROR" "No database dump tool found"
                return 1
            fi
            ;;
        "system")
            # System configuration backup
            cp /etc/passwd "$backup_dir/"
            cp /etc/group "$backup_dir/"
            cp /etc/fstab "$backup_dir/"
            dpkg --get-selections > "$backup_dir/dpkg-selections"
            ;;
    esac
    
    log "INFO" "Backup completed: $backup_dir"
}

# User management automation
manage_users() {
    local action="$1"
    local username="$2"
    
    case "$action" in
        "create")
            if id "$username" &>/dev/null; then
                log "WARN" "User $username already exists"
                return 1
            fi
            
            useradd -m -s /bin/bash "$username"
            log "INFO" "Created user: $username"
            
            # Generate SSH key for new user
            sudo -u "$username" ssh-keygen -t ed25519 -f "/home/$username/.ssh/id_ed25519" -N ""
            log "INFO" "Generated SSH key for $username"
            ;;
        "disable")
            usermod --lock "$username"
            log "INFO" "Disabled user: $username"
            ;;
        "delete")
            userdel -r "$username"
            log "INFO" "Deleted user: $username"
            ;;
        *)
            log "ERROR" "Unknown action: $action"
            return 1
            ;;
    esac
}

# Service management
manage_services() {
    local action="$1"
    local service="$2"
    
    case "$action" in
        "start")
            systemctl start "$service"
            log "INFO" "Started service: $service"
            ;;
        "stop")
            systemctl stop "$service"
            log "INFO" "Stopped service: $service"
            ;;
        "restart")
            systemctl restart "$service"
            log "INFO" "Restarted service: $service"
            ;;
        "status")
            if systemctl is-active --quiet "$service"; then
                log "INFO" "Service $service is running"
            else
                log "WARN" "Service $service is not running"
            fi
            ;;
    esac
}

# Update management
perform_updates() {
    local update_type="$1"
    
    log "INFO" "Starting $update_type updates"
    
    case "$update_type" in
        "system")
            apt update && apt upgrade -y
            log "INFO" "System packages updated"
            ;;
        "security")
            apt update && apt unattended-upgrade -y
            log "INFO" "Security updates applied"
            ;;
        "packages")
            if [[ -f "$SCRIPT_DIR/package-list.txt" ]]; then
                while read -r package; do
                    apt install -y "$package"
                    log "INFO" "Installed package: $package"
                done < "$SCRIPT_DIR/package-list.txt"
            fi
            ;;
    esac
}

# Monitoring alert
send_alert() {
    local severity="$1"
    local message="$2"
    
    log "ALERT" "[$severity] $message"
    
    # Send email notification
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "Homelab Alert: $severity" "admin@homelab.local"
    fi
    
    # Send Slack notification
    if command -v curl >/dev/null 2>&1; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$severity] $message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# Main execution
main() {
    local config_file="${1:-$SCRIPT_DIR/config.yaml}"
    local command="${2:-help}"
    
    log "INFO" "Starting homelab automation script"
    validate_config "$config_file"
    check_system_health
    
    case "$command" in
        "backup")
            perform_backup "$3" "$4" "$5"
            ;;
        "user")
            manage_users "$3" "$4"
            ;;
        "service")
            manage_services "$3" "$4"
            ;;
        "update")
            perform_updates "$3"
            ;;
        "health")
            check_system_health
            ;;
        *)
            echo "Usage: $0 [config_file] {backup|user|service|update|health} [args...]"
            exit 1
            ;;
    esac
    
    log "INFO" "Automation script completed successfully"
}

# Execute main function
main "$@"
```

### PowerShell Automation
```powershell
# homelab-automation.ps1
# Windows automation script for homelab management

param(
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = "$PSScriptRoot\config.yaml",
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("Backup", "User", "Service", "Update", "Health")]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string[]]$Arguments
)

# Configuration and logging
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$LogFile = "C:\Logs\homelab-automation.log"

function Write-Log {
    param([string]$Level, [string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-Prerequisites {
    Write-Log "INFO" "Checking prerequisites"
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Log "ERROR" "PowerShell 5.0 or higher required"
        exit 1
    }
    
    # Check administrator privileges
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Log "ERROR" "Administrator privileges required"
        exit 1
    }
    
    # Check required modules
    $RequiredModules = @("ActiveDirectory", "ServerManager")
    foreach ($Module in $RequiredModules) {
        if (-NOT (Get-Module -Name $Module -ListAvailable)) {
            Write-Log "ERROR" "Required module not found: $Module"
            exit 1
        }
    }
    
    Write-Log "INFO" "Prerequisites check passed"
}

function Backup-System {
    param([string]$Type, [string]$Destination)
    
    Write-Log "INFO" "Starting $Type backup"
    
    $BackupPath = "$Destination\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -Path $BackupPath -ItemType Directory -Force
    
    switch ($Type) {
        "Files" {
            $Sources = Get-Content -Path $PSScriptRoot\backup-sources.txt
            foreach ($Source in $Sources) {
                if (Test-Path $Source) {
                    $FileName = Split-Path $Source -Leaf
                    Compress-Archive -Path $Source -Destination "$BackupPath\$FileName.zip"
                    Write-Log "INFO" "Backed up: $Source"
                }
            }
        }
        
        "Registry" {
            $RegKeys = Get-Content -Path $PSScriptRoot\registry-keys.txt
            foreach ($Key in $RegKeys) {
                if (Test-Path $Key) {
                    $FileName = $Key -replace '[\\/:*?"<>|]', '_'
                    reg export $Key "$BackupPath\$FileName.reg"
                    Write-Log "INFO" "Exported registry: $Key"
                }
            }
        }
        
        "System" {
            # System state backup
            Export-Certificate -FilePath "$BackupPath\certificates.cer"
            Get-WindowsFeature | Export-Clixml -Path "$BackupPath\windows-features.xml"
            Get-Service | Export-Clixml -Path "$BackupPath\services.xml"
            Write-Log "INFO" "System state backed up"
        }
    }
    
    Write-Log "INFO" "Backup completed: $BackupPath"
}

function Manage-Users {
    param([string]$Action, [string]$Username)
    
    Write-Log "INFO" "User management: $Action $Username"
    
    switch ($Action) {
        "Create" {
            if (Get-ADUser -Filter "SamAccountName -eq '$Username'" -ErrorAction SilentlyContinue) {
                Write-Log "WARN" "User $Username already exists"
                return
            }
            
            $UserParams = @{
                SamAccountName = $Username
                UserPrincipalName = "$Username@homelab.local"
                Name = $Username
                AccountPassword = (ConvertTo-SecureString "TempPass123!" -AsPlainText -Force)
                Enabled = $true
                ChangePasswordAtLogon = $true
                Path = "OU=Users,DC=homelab,DC=local"
            }
            
            New-ADUser @UserParams
            Write-Log "INFO" "Created user: $Username"
        }
        
        "Disable" {
            Disable-ADAccount -Identity $Username
            Write-Log "INFO" "Disabled user: $Username"
        }
        
        "Delete" {
            Remove-ADUser -Identity $Username -Confirm:$false
            Write-Log "INFO" "Deleted user: $Username"
        }
    }
}

function Manage-Services {
    param([string]$Action, [string]$ServiceName)
    
    Write-Log "INFO" "Service management: $Action $ServiceName"
    
    switch ($Action) {
        "Start" {
            Start-Service -Name $ServiceName
            Write-Log "INFO" "Started service: $ServiceName"
        }
        
        "Stop" {
            Stop-Service -Name $ServiceName -Force
            Write-Log "INFO" "Stopped service: $ServiceName"
        }
        
        "Restart" {
            Restart-Service -Name $ServiceName -Force
            Write-Log "INFO" "Restarted service: $ServiceName"
        }
        
        "Status" {
            $Service = Get-Service -Name $ServiceName
            if ($Service.Status -eq "Running") {
                Write-Log "INFO" "Service $ServiceName is running"
            } else {
                Write-Log "WARN" "Service $ServiceName is not running (Status: $($Service.Status))"
            }
        }
    }
}

function Update-System {
    param([string]$UpdateType)
    
    Write-Log "INFO" "Starting $UpdateType updates"
    
    switch ($UpdateType) {
        "Windows" {
            Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot
            Write-Log "INFO" "Windows updates installed"
        }
        
        "Features" {
            $Features = Get-Content -Path $PSScriptRoot\features.txt
            foreach ($Feature in $Features) {
                Install-WindowsFeature -Name $Feature -IncludeManagementTools
                Write-Log "INFO" "Installed feature: $Feature"
            }
        }
        
        "Applications" {
            $Applications = Get-Content -Path $PSScriptRoot\applications.txt
            foreach ($App in $Applications) {
                # Application-specific installation logic
                Write-Log "INFO" "Installing application: $App"
            }
        }
    }
}

function Test-SystemHealth {
    Write-Log "INFO" "Performing system health checks"
    
    # Check disk space
    $Disks = Get-WmiObject -Class Win32_LogicalDisk
    foreach ($Disk in $Disks) {
        $FreePercent = [math]::Round(($Disk.FreeSpace / $Disk.Size) * 100, 2)
        if ($FreePercent -lt 20) {
            Write-Log "WARN" "Low disk space on $($Disk.DeviceID): ${FreePercent}% free"
        }
    }
    
    # Check memory usage
    $Memory = Get-WmiObject -Class Win32_OperatingSystem
    $MemoryUsage = [math]::Round((($Memory.TotalVisibleMemorySize - $Memory.FreePhysicalMemory) / $Memory.TotalVisibleMemorySize) * 100, 2)
    if ($MemoryUsage -gt 85) {
        Write-Log "WARN" "High memory usage: ${MemoryUsage}%"
    }
    
    # Check critical services
    $CriticalServices = Get-Content -Path $PSScriptRoot\critical-services.txt
    foreach ($ServiceName in $CriticalServices) {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($Service -and $Service.Status -ne "Running") {
            Write-Log "ERROR" "Critical service not running: $ServiceName"
        }
    }
    
    # Check event logs for errors
    $RecentErrors = Get-EventLog -LogName System -EntryType Error -After (Get-Date).AddHours(-24)
    if ($RecentErrors.Count -gt 0) {
        Write-Log "WARN" "Found $($RecentErrors.Count) system errors in last 24 hours"
    }
}

# Main execution
try {
    Test-Prerequisites
    
    switch ($Command) {
        "Backup" {
            Backup-System -Type $Arguments[0] -Destination $Arguments[1]
        }
        
        "User" {
            Manage-Users -Action $Arguments[0] -Username $Arguments[1]
        }
        
        "Service" {
            Manage-Services -Action $Arguments[0] -ServiceName $Arguments[1]
        }
        
        "Update" {
            Update-System -UpdateType $Arguments[0]
        }
        
        "Health" {
            Test-SystemHealth
        }
        
        default {
            Write-Host "Usage: .\homelab-automation.ps1 [-ConfigFile <path>] -Command <Backup|User|Service|Update|Health> [-Arguments <args...>]"
            exit 1
        }
    }
    
    Write-Log "INFO" "Automation script completed successfully"
    
} catch {
    Write-Log "ERROR" "Script failed: $($_.Exception.Message)"
    Write-Log "ERROR" "Stack trace: $($_.Exception.StackTrace)"
    exit 1
}
```

## 🔧 Configuration Management

### Ansible Configuration
```yaml
# ansible.cfg
[defaults]
inventory = ./inventory
host_key_checking = False
retry_files_enabled = False
roles_path = ./roles
log_path = ./ansible.log
stdout_callback = yaml

# inventory/hosts
[homelab_servers]
server1.homelab.local ansible_host=192.168.1.100
server2.homelab.local ansible_host=192.168.1.101

[database_servers]
db1.homelab.local ansible_host=192.168.1.110
db2.homelab.local ansible_host=192.168.1.111

[web_servers]
web1.homelab.local ansible_host=192.168.1.120
web2.homelab.local ansible_host=192.168.1.121

[all:vars]
ansible_user = admin
ansible_ssh_private_key_file = ~/.ssh/homelab_key
ansible_python_interpreter = /usr/bin/python3
```

### Ansible Playbooks
```yaml
# playbooks/server-setup.yml
---
- name: Homelab Server Setup
  hosts: homelab_servers
  become: yes
  vars:
    timezone: America/New_York
    ntp_servers:
      - 0.pool.ntp.org
      - 1.pool.ntp.org
      - 2.pool.ntp.org
    common_packages:
      - vim
      - htop
      - curl
      - wget
      - git
      - unzip
      - build-essential

  tasks:
    - name: Update package cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Upgrade all packages
      apt:
        upgrade: dist

    - name: Install common packages
      apt:
        name: "{{ common_packages }}"
        state: present

    - name: Configure timezone
      timezone:
        name: "{{ timezone }}"

    - name: Configure NTP
      template:
        src: ntp.conf.j2
        dest: /etc/ntp.conf
      notify: restart ntp

    - name: Ensure NTP service is running
      service:
        name: ntp
        state: started
        enabled: yes

    - name: Create homelab user
      user:
        name: homelab
        groups: sudo,docker
        shell: /bin/bash
        create_home: yes
        generate_ssh_key: yes
        ssh_key_bits: 4096
        ssh_key_comment: "homelab@{{ ansible_hostname }}"

    - name: Configure SSH
      template:
        src: sshd_config.j2
        dest: /etc/ssh/sshd_config
      notify: restart ssh

    - name: Configure firewall
      ufw:
        state: enabled
        policy: deny
        rule: allow
        port: "{{ item }}"
        proto: tcp
      loop:
        - 22
        - 80
        - 443

    - name: Set up log rotation
      template:
        src: logrotate.conf.j2
        dest: /etc/logrotate.d/homelab

  handlers:
    - name: restart ntp
      service:
        name: ntp
        state: restarted

    - name: restart ssh
      service:
        name: ssh
        state: restarted

# playbooks/database-setup.yml
---
- name: Database Server Setup
  hosts: database_servers
  become: yes
  vars:
    mysql_root_password: "{{ vault_mysql_root_password }}"
    mysql_databases:
      - name: homelab_app
        encoding: utf8mb4
        collation: utf8mb4_unicode_ci
    mysql_users:
      - name: homelab_user
        password: "{{ vault_mysql_app_password }}"
        priv: "homelab_app.*:ALL"

  tasks:
    - name: Install MySQL server
      apt:
        name:
          - mysql-server
          - mysql-client
          - python3-pymysql
        state: present

    - name: Set MySQL root password
      mysql_user:
        name: root
        password: "{{ mysql_root_password }}"
        login_unix_socket: /var/run/mysqld/mysqld.sock
        state: present

    - name: Create MySQL configuration
      template:
        src: my.cnf.j2
        dest: /etc/mysql/my.cnf
      notify: restart mysql

    - name: Create databases
      mysql_db:
        name: "{{ item.name }}"
        encoding: "{{ item.encoding }}"
        collation: "{{ item.collation }}"
        login_user: root
        login_password: "{{ mysql_root_password }}"
      loop: "{{ mysql_databases }}"

    - name: Create database users
      mysql_user:
        name: "{{ item.name }}"
        password: "{{ item.password }}"
        priv: "{{ item.priv }}"
        login_user: root
        login_password: "{{ mysql_root_password }}"
      loop: "{{ mysql_users }}"

    - name: Ensure MySQL service is running
      service:
        name: mysql
        state: started
        enabled: yes

  handlers:
    - name: restart mysql
      service:
        name: mysql
        state: restarted
```

### Docker Compose Automation
```yaml
# docker-compose.automation.yml
version: '3.8'

services:
  # Configuration management
  ansible:
    image: python:3.9-slim
    volumes:
      - ./ansible:/ansible
      - /var/run/docker.sock:/var/run/docker.sock
    working_dir: /ansible
    command: >
      sh -c "
        pip install ansible &&
        ansible-playbook -i inventory playbooks/server-setup.yml
      "

  # Monitoring stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123

  # Backup automation
  backup:
    image: alpine:latest
    volumes:
      - ./backups:/backups
      - /var/lib:/source/var
      - /etc:/source/etc
      - /home:/source/home
    command: >
      sh -c "
        apk add --no-cache tar &&
        while true; do
          echo 'Starting backup: $(date)' &&
          tar -czf /backups/full-$(date +%Y%m%d_%H%M%S).tar.gz -C /source . &&
          find /backups -name '*.tar.gz' -mtime +7 -delete &&
          echo 'Backup completed: $(date)' &&
          sleep 86400
        done
      "

volumes:
  prometheus_data:
  grafana_data:

# deploy.sh
#!/bin/bash
# Automated deployment script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

check_prerequisites() {
    log "Checking prerequisites"
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        log "ERROR: Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        log "ERROR: Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log "ERROR: Docker is not running"
        exit 1
    fi
    
    log "Prerequisites check passed"
}

deploy_services() {
    log "Deploying homelab services"
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    docker-compose pull
    
    # Stop existing services
    docker-compose down
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy"
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "Up (healthy)"; then
        log "Services deployed successfully"
    else
        log "ERROR: Some services are not healthy"
        docker-compose ps
        exit 1
    fi
}

update_configuration() {
    log "Updating configuration"
    
    # Pull latest configuration
    cd "$PROJECT_ROOT"
    git pull origin main
    
    # Validate configuration
    if ! docker-compose config >/dev/null 2>&1; then
        log "ERROR: Docker Compose configuration is invalid"
        exit 1
    fi
    
    log "Configuration updated and validated"
}

rollback() {
    log "Performing rollback"
    
    cd "$PROJECT_ROOT"
    
    # Get previous commit
    PREVIOUS_COMMIT=$(git rev-parse HEAD~1)
    
    # Checkout previous commit
    git checkout "$PREVIOUS_COMMIT"
    
    # Redeploy
    docker-compose down
    docker-compose up -d
    
    log "Rollback completed"
}

case "${1:-deploy}" in
    "deploy")
        check_prerequisites
        update_configuration
        deploy_services
        ;;
    "update")
        update_configuration
        deploy_services
        ;;
    "rollback")
        rollback
        ;;
    "status")
        docker-compose ps
        ;;
    *)
        echo "Usage: $0 {deploy|update|rollback|status}"
        exit 1
        ;;
esac
```

## 🐳 Container Orchestration

### Kubernetes Automation
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: homelab
  labels:
    name: homelab
    environment: production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: homelab-config
  namespace: homelab
data:
  app.properties: |
    database.url=jdbc:postgresql://postgres:5432/homelab
    redis.url=redis://redis:6379
    logging.level=INFO
  nginx.conf: |
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://app:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: homelab-app
  namespace: homelab
  labels:
    app: homelab-app
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: homelab-app
  template:
    metadata:
      labels:
        app: homelab-app
        version: v1
    spec:
      containers:
      - name: app
        image: homelab/app:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: homelab-config
              key: app.properties
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: homelab-config
              key: app.properties
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: homelab-app-service
  namespace: homelab
spec:
  selector:
    app: homelab-app
  ports:
  - port: 80
    targetPort: 3000
    name: http
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: homelab-ingress
  namespace: homelab
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - app.homelab.local
    secretName: homelab-tls
  rules:
  - host: app.homelab.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: homelab-app-service
            port:
              number: 80

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: homelab-app-hpa
  namespace: homelab
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: homelab-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Helm Charts
```yaml
# helm/homelab/Chart.yaml
apiVersion: v2
name: homelab
description: A Helm chart for homelab services
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
- name: postgresql
  version: 12.x.x
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled
- name: redis
  version: 17.x.x
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled

# helm/homelab/values.yaml
replicaCount: 3

image:
  repository: homelab/app
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: app.homelab.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: homelab-tls
      hosts:
        - app.homelab.local

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    postgresPassword: "securepassword"
    database: "homelab"
  primary:
    persistence:
      enabled: true
      size: 20Gi

redis:
  enabled: true
  auth:
    enabled: true
    password: "redispassword"
  master:
    persistence:
      enabled: true
      size: 8Gi

# helm/homelab/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "homelab.fullname" . }}
  labels:
    {{- include "homelab.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "homelab.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "homelab.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          env:
            - name: DATABASE_URL
              value: "postgresql://{{ .Values.postgresql.auth.postgresqlUsername }}:{{ .Values.postgresql.auth.postgresqlPassword }}@{{ .Release.Name }}-postgresql:5432/{{ .Values.postgresql.auth.database }}"
            - name: REDIS_URL
              value: "redis://{{ .Release.Name }}-redis-master:6379"
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## 📊 Monitoring Automation

### Prometheus Automation
```yaml
# monitoring/prometheus-automation.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert-rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets: 
        - 'server1.homelab.local:9100'
        - 'server2.homelab.local:9100'
        - 'db1.homelab.local:9100'
        - 'web1.homelab.local:9100'

  - job_name: 'process-exporter'
    static_configs:
      - targets:
        - 'server1.homelab.local:9256'
        - 'server2.homelab.local:9256'

  - job_name: 'blackbox-exporter'
    metrics_path: /probe
    static_configs:
      - targets:
        - 'https://app.homelab.local'
        - 'https://api.homelab.local'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

# alert-rules/system-alerts.yml
groups:
  - name: homelab-system-alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes on {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 5 minutes on {{ $labels.instance }}"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 5m
        labels:
          severity: critical
          service: system
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 10% on {{ $labels.instance }} (mountpoint: {{ $labels.mountpoint }})"

      - alert: ServiceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
          service: system
        annotations:
          summary: "Service down: {{ $labels.instance }}"
          description: "{{ $labels.job }} service on {{ $labels.instance }} has been down for more than 2 minutes"
```

### Automated Response Scripts
```bash
#!/bin/bash
# automated-response.sh
# Automated response to alerts

ALERT_TYPE="$1"
INSTANCE="$2"
SEVERITY="$3"
MESSAGE="$4"

log_response() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Automated response: $*"
}

restart_service() {
    local service="$1"
    log_response "Attempting to restart service: $service"
    
    if systemctl restart "$service"; then
        log_response "Successfully restarted service: $service"
        echo "Service $service restarted successfully" | mail -s "Homelab Alert Recovery" admin@homelab.local
    else
        log_response "Failed to restart service: $service"
        # Escalate to manual intervention
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"CRITICAL: Failed to restart $service on $INSTANCE\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

cleanup_disk() {
    local mountpoint="$1"
    log_response "Performing disk cleanup on: $mountpoint"
    
    # Clean temporary files
    find "$mountpoint/tmp" -type f -mtime +7 -delete 2>/dev/null || true
    find "$mountpoint/var/tmp" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Clean log files older than 30 days
    find "$mountpoint/var/log" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    # Clean package cache
    if command -v apt >/dev/null 2>&1; then
        apt-get clean
    fi
    
    log_response "Disk cleanup completed for: $mountpoint"
}

scale_service() {
    local service="$1"
    local direction="$2"
    
    log_response "Scaling $service: $direction"
    
    case "$direction" in
        "up")
            kubectl scale deployment "$service" --replicas=5 -n homelab
            ;;
        "down")
            kubectl scale deployment "$service" --replicas=2 -n homelab
            ;;
    esac
}

case "$ALERT_TYPE" in
    "HighCPUUsage")
        if [[ "$SEVERITY" == "critical" ]]; then
            # Investigate high CPU process
            top -bn1 | head -20 > "/tmp/cpu-analysis-$INSTANCE.log"
            restart_service "application"
        fi
        ;;
        
    "HighMemoryUsage")
        if [[ "$SEVERITY" == "critical" ]]; then
            restart_service "application"
        fi
        ;;
        
    "DiskSpaceLow")
        # Get mountpoint from alert details
        MOUNTPOINT=$(echo "$MESSAGE" | grep -o 'mountpoint: [^)]*' | cut -d' ' -f2)
        cleanup_disk "$MOUNTPOINT"
        ;;
        
    "ServiceDown")
        SERVICE=$(echo "$MESSAGE" | grep -o 'job: [^,]*' | cut -d' ' -f2)
        restart_service "$SERVICE"
        ;;
        
    "HighLoadAverage")
        # Scale up application
        scale_service "homelab-app" "up"
        ;;
        
    *)
        log_response "Unknown alert type: $ALERT_TYPE"
        ;;
esac
```

## 🔗 CI/CD Integration

### GitLab CI/CD
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy
  - monitoring

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs/client"

before_script:
  - echo "Starting CI/CD pipeline"
  - docker info

test:
  stage: test
  image: python:3.9
  services:
    - postgres:13
    - redis:6
  variables:
    POSTGRES_DB: homelab_test
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
    REDIS_URL: redis://redis:6379
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest tests/ --cov=. --cov-report=xml
  coverage: '/Total coverage: (\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - echo "Building Docker image"
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - echo "Pushing Docker image"
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - develop

deploy_staging:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.homelab.local
  script:
    - echo "Deploying to staging"
    - kubectl config use-context $KUBE_CONTEXT_STAGING
    - kubectl set image deployment homelab-app homelab-app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n homelab-staging
    - kubectl rollout status deployment homelab-app -n homelab-staging
  only:
    - develop

deploy_production:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://app.homelab.local
  script:
    - echo "Deploying to production"
    - kubectl config use-context $KUBE_CONTEXT_PROD
    - kubectl set image deployment homelab-app homelab-app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n homelab
    - kubectl rollout status deployment homelab-app -n homelab
    - kubectl rollout status deployment homelab-app -n homelab
  when: manual
  only:
    - main

monitoring:
  stage: monitoring
  image: alpine:latest
  script:
    - echo "Updating monitoring configuration"
    - curl -X POST -H "Authorization: Bearer $PROMETHEUS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"deploy","labels":{"environment":"'$CI_ENVIRONMENT'","version":"'$CI_COMMIT_SHA'"}}' \
      "$PROMETHEUS_URL/api/v1/annotations"
  dependencies:
    - deploy_staging
    - deploy_production
```

### GitHub Actions
```yaml
# .github/workflows/homelab-ci.yml
name: Homelab CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: homelab_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.IMAGE_NAME }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.24.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to production
      run: |
        kubectl set image deployment homelab-app homelab-app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n homelab
        kubectl rollout status deployment homelab-app -n homelab
        kubectl get pods -n homelab
```

## 📚 Best Practices

### Code Organization
```bash
# Recommended directory structure
automation/
├── ansible/
│   ├── inventory/
│   ├── playbooks/
│   ├── roles/
│   └── group_vars/
├── scripts/
│   ├── bash/
│   ├── powershell/
│   └── python/
├── kubernetes/
│   ├── namespaces/
│   ├── deployments/
│   ├── services/
│   └── helm/
├── docker/
│   ├── compose-files/
│   └── dockerfiles/
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
├── ci-cd/
│   ├── .gitlab-ci.yml
│   └── .github/
├── docs/
├── tests/
└── README.md
```

### Security Considerations
```bash
# Automation security checklist

Credential Management:
  ✓ Use environment variables or vaults
  ✓ Never hardcode passwords in scripts
  ✓ Rotate credentials regularly
  ✓ Use SSH keys instead of passwords
  ✓ Implement least privilege access

Code Security:
  ✓ Validate all inputs
  ✓ Use parameterized scripts
  ✓ Implement error handling
  ✓ Secure temporary files
  ✓ Remove sensitive data from logs

Infrastructure Security:
  ✓ Secure communication channels
  ✓ Use TLS/SSL for all communications
  ✓ Implement network segmentation
  ✓ Regular security updates
  ✓ Monitor automation activities

Compliance and Auditing:
  ✓ Log all automation activities
  ✓ Implement audit trails
  ✓ Regular security reviews
  ✓ Document automation processes
  ✓ Compliance checks
```

### Monitoring and Logging
```bash
# Automation monitoring implementation

# Logging standards
LOG_FORMAT="timestamp,level,message,source,user"
LOG_ROTATION="daily"
LOG_RETENTION="30 days"

# Metrics collection
AUTOMATION_METRICS = {
    script_success_rate: 0.95,
    script_duration_avg: 300,
    error_rate_threshold: 0.05,
    alert_response_time: 60
}

# Monitoring dashboard alerts
- script_success_rate < 0.90
- script_duration_avg > 600
- error_rate > 0.10
- alert_response_time > 300
```

## 🚨 Troubleshooting

### Common Automation Issues
```bash
# Debugging automation scripts
# Enable debug mode
set -x  # Bash
$DebugPreference = "Continue"  # PowerShell

# Common issues and solutions

1. Permission denied:
   - Check script permissions: ls -la script.sh
   - Fix: chmod +x script.sh
   - Use sudo for system operations

2. Environment variables not found:
   - Check if exported: export | grep VAR_NAME
   - Source configuration: source config.sh
   - Use absolute paths

3. Network connectivity issues:
   - Test connectivity: ping host
   - Check DNS: nslookup hostname
   - Verify firewall rules

4. Service failures:
   - Check service status: systemctl status service
   - View logs: journalctl -u service -f
   - Restart service: systemctl restart service

5. Configuration errors:
   - Validate YAML/JSON: yamllint file.yaml
   - Check syntax: bash -n script.sh
   - Test in staging environment
```

### Recovery Procedures
```bash
# Automation recovery script
#!/bin/bash
# recover-automation.sh

BACKUP_DIR="/backups/automation"
ROLLBACK_COUNT=5

recover_from_backup() {
    local service="$1"
    echo "Recovering $service from backup"
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR/$service"* | head -1)
    
    # Restore backup
    tar -xzf "$LATEST_BACKUP" -C /
    
    # Restart service
    systemctl restart "$service"
    
    # Verify recovery
    if systemctl is-active --quiet "$service"; then
        echo "Successfully recovered $service"
    else
        echo "Failed to recover $service"
        exit 1
    fi
}

# Manual rollback procedures
git reset --hard HEAD~1  # Git rollback
kubectl rollout undo deployment/app  # Kubernetes rollback
docker-compose down && docker-compose up -d  # Docker rollback
```

## 📖 Further Reading

### Documentation
- [Ansible Documentation](https://docs.ansible.com/)
- [Kubernetes Automation](https://kubernetes.io/docs/concepts/workloads/controllers/)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Books and Courses
- [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/)
- [The Phoenix Project](https://itrevolutionbooks.com/)
- [Effective DevOps](https://www.oreilly.com/library/view/effective-devops/9781492076825/)

### Communities
- Reddit: r/devops, r/ansible, r/kubernetes
- DevOps Stack Exchange
- Automation forums and Slack channels

### Advanced Topics
- Infrastructure as Code (Terraform, CloudFormation)
- GitOps (ArgoCD, Flux)
- Configuration Management (Chef, Puppet, Salt)
- Monitoring as Code (Prometheus as Code, Grafana as Code)

---

**Ready to dive deeper?** Check our [System Administration](index.md) overview for comprehensive admin planning!

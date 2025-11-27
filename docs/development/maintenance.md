# Maintenance Guide

## Overview

This guide covers routine maintenance tasks, troubleshooting procedures, and performance optimization for the Homelab Documentation Hub platform.

## Routine Maintenance

### Daily Tasks

#### System Health Checks
```bash
#!/bin/bash
# Daily health check script
HEALTH_LOG="/var/log/homelab-docs-health.log"
DATE=$(date +%Y-%m-%d)

# Check Docker containers
echo "$(date): Checking Docker containers..." >> $HEALTH_LOG
docker-compose -f docker/docker-compose.yml ps >> $HEALTH_LOG 2>&1

# Check service health
services=("nginx:80" "mkdocs:8000" "ai-backend:8001" "redis:6379")

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "$(date): ✅ $service_name is healthy" >> $HEALTH_LOG
    else
        echo "$(date): ❌ $service_name is unhealthy" >> $HEALTH_LOG
        # Send alert notification
        curl -X POST -H "Content-Type: application/json" \
             -d "{\"service\": \"$service_name\", \"status\": \"unhealthy\", \"timestamp\": \"$(date -I)\"}" \
             http://localhost:8001/api/alerts >> $HEALTH_LOG 2>&1 || true
    fi
done

# Check disk space
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [[ ${disk_usage%.*} -gt 85 ]]; then
    echo "$(date): ⚠️ Disk usage high: ${disk_usage}%" >> $HEALTH_LOG
fi

# Check memory usage
mem_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if [[ $(echo "$mem_usage > 80" | bc -l) ]]; then
    echo "$(date): ⚠️ Memory usage high: ${mem_usage}%" >> $HEALTH_LOG
fi

echo "$(date): Daily health check completed" >> $HEALTH_LOG
```

#### Log Rotation and Cleanup
```bash
#!/bin/bash
# Log rotation and cleanup script
LOG_RETENTION_DAYS=30
BACKUP_RETENTION_DAYS=7
LOG_DIR="/var/log/homelab-docs"
BACKUP_DIR="/backup/homelab-docs"

# Rotate application logs
find $LOG_DIR -name "*.log" -type f -mtime +$LOG_RETENTION_DAYS -delete

# Compress old backup files
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +$LOG_RETENTION_DAYS -exec gzip {} \;

# Cleanup temporary files
find /tmp -name "homelab-docs-*" -type f -mtime +1 -delete

# Cleanup Docker unused resources
docker system prune -f
docker volume prune -f

echo "Log rotation and cleanup completed"
```

### Weekly Tasks

#### Database Maintenance
```bash
#!/bin/bash
# Weekly database maintenance script
DATE=$(date +%Y-%m-%d)

# Redis maintenance
redis-cli BGSAVE
redis-cli --rdb keys "*" | wc -l > /tmp/redis_keys_count_$DATE

# Check Redis memory usage
redis-cli INFO memory | grep "used_memory_human" > /tmp/redis_memory_$DATE

# Optimize Redis
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Check Redis persistence
if ! redis-cli LASTSAVE | grep -q "OK"; then
    redis-cli BGSAVE
    echo "Triggered Redis background save"
fi
```

#### Security Updates
```bash
#!/bin/bash
# Weekly security maintenance script

# Update Docker images
docker pull nginx:latest
docker pull redis:latest
docker pull python:3.11-slim

# Update system packages
apt update && apt upgrade -y

# Check for security vulnerabilities
docker scan nginx:latest
docker scan redis:latest

# Update SSL certificates (if expiring soon)
if [[ -f "docker/ssl/fullchain.pem" ]]; then
    cert_expiry=$(openssl x509 -in docker/ssl/fullchain.pem -noout -dates | awk '/notAfter/ {print $1}')
    cert_expiry_epoch=$(date -d "$cert_expiry" +%s)
    current_epoch=$(date +%s)
    days_until_expiry=$(( (cert_expiry_epoch - current_epoch) / 86400 ))
    
    if [[ $days_until_expiry -lt 30 ]]; then
        echo "SSL certificate expires in $days_until_expiry days"
        # Generate renewal alert
        echo "SSL certificate renewal needed" | mail -s "SSL Certificate Alert" admin@example.com
    fi
fi
```

#### Performance Optimization
```bash
#!/bin/bash
# Weekly performance optimization script

# Restart services for memory cleanup
docker-compose -f docker/docker-compose.yml restart redis
docker-compose -f docker/docker-compose.yml restart ai-backend

# Optimize database
redis-cli MEMORY PURGE

# Clear Docker cache
docker builder prune -a

# Update configuration for optimal performance
# Update nginx.conf with performance optimizations
# Update Redis configuration for memory optimization

echo "Performance optimization completed"
```

### Monthly Tasks

#### Full System Backup
```bash
#!/bin/bash
# Monthly full system backup script
MONTH=$(date +%Y-%m)
BACKUP_DIR="/backup/homelab-docs/monthly/$MONTH"

mkdir -p $BACKUP_DIR

# Backup all Docker volumes
docker run --rm -v homelab-docs_ai_uploads:/data -v $BACKUP_DIR:/backup \
    alpine tar czf "/backup/uploads-$MONTH.tar.gz" -C /data .

docker run --rm -v homelab-docs_redis:/data -v $BACKUP_DIR:/backup \
    alpine tar czf "/backup/redis-$MONTH.tar.gz" -C /data .

# Backup configuration files
tar -czf "$BACKUP_DIR/configs-$MONTH.tar.gz" .env docker/ scripts/

# Backup documentation
tar -czf "$BACKUP_DIR/docs-$MONTH.tar.gz" docs/

# Create backup manifest
echo "Monthly backup for $MONTH" > $BACKUP_DIR/backup-manifest.txt
echo "Created: $(date)" >> $BACKUP_DIR/backup-manifest.txt
echo "Files:" >> $BACKUP_DIR/backup-manifest.txt
ls -la $BACKUP_DIR >> $BACKUP_DIR/backup-manifest.txt

# Verify backup integrity
for file in $BACKUP_DIR/*.tar.gz; do
    if tar -tzf "$file" > /dev/null; then
        echo "✅ $file is valid"
    else
        echo "❌ $file is corrupted"
    fi
done

echo "Monthly backup completed: $BACKUP_DIR"
```

#### Security Audit
```bash
#!/bin/bash
# Monthly security audit script
AUDIT_DATE=$(date +%Y-%m-%d)
AUDIT_DIR="/var/log/security-audit/$AUDIT_DATE"
mkdir -p $AUDIT_DIR

# Check Docker container security
echo "Docker Security Audit" > $AUDIT_DIR/docker-security.txt
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedAt}}" >> $AUDIT_DIR/docker-security.txt

# Check for exposed ports
echo "Network Security Audit" > $AUDIT_DIR/network-security.txt
netstat -tuln | grep LISTEN >> $AUDIT_DIR/network-security.txt

# Check file permissions
echo "File Permissions Audit" > $AUDIT_DIR/permissions.txt
find /opt/homelab-docs -type f -perm /o+w >> $AUDIT_DIR/permissions.txt 2>/dev/null || true

# Check SSL certificates
echo "SSL Certificate Audit" > $AUDIT_DIR/ssl-audit.txt
for cert in docker/ssl/*.pem; do
    echo "Certificate: $cert" >> $AUDIT_DIR/ssl-audit.txt
    openssl x509 -in $cert -noout -dates >> $AUDIT_DIR/ssl-audit.txt
    echo "" >> $AUDIT_DIR/ssl-audit.txt
done

# Generate security report
echo "Security Audit Report - $AUDIT_DATE" > $AUDIT_DIR/security-report.txt
echo "=========================" >> $AUDIT_DIR/security-report.txt
cat $AUDIT_DIR/docker-security.txt >> $AUDIT_DIR/security-report.txt
cat $AUDIT_DIR/network-security.txt >> $AUDIT_DIR/security-report.txt
cat $AUDIT_DIR/permissions.txt >> $AUDIT_DIR/security-report.txt
cat $AUDIT_DIR/ssl-audit.txt >> $AUDIT_DIR/security-report.txt

echo "Security audit completed: $AUDIT_DIR"
```

## Monitoring and Alerting

### Health Monitoring Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'homelab-docs'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/api/metrics'
    scrape_interval: 5s
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Homelab Documentation Hub",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"homelab-docs\"}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "min": 0,
            "max": 1
            " thresholds": [
              {
                "value": 0,
                "color": "red"
              },
              {
                "value": 1,
                "color": "green"
              }
            ]
          }
        }
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_sum[5m])"
          }
        ],
        "yAxes": [
          {
            "format": "short",
            "label": "Time"
          }
        ],
        "xAxes": [
          {
            "format": "short",
            "label": "Response Time"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### Alert Configuration

#### Email Alerts
```bash
#!/bin/bash
# Email alert configuration
ALERT_EMAIL="admin@example.com"
SMTP_SERVER="smtp.example.com"
SMTP_PORT="587"
SMTP_USER="alerts@example.com"
SMTP_PASS="your_smtp_password"

send_email_alert() {
    local subject=$1
    local message=$2
    
    echo -e "Subject: $subject\n\n$message" | \
        ssmtp -C "login://$SMTP_USER:$SMTP_PASS@$SMTP_SERVER:$SMTP_PORT" \
        -f "alerts@example.com" "$ALERT_EMAIL"
}

# Example usage
send_email_alert "Service Down" "The nginx service is not responding on $(hostname)"
```

#### Slack Integration
```bash
#!/bin/bash
# Slack alert integration
SLACK_WEBHOOK="YOUR_SLACK_WEBHOOK_URL_HERE"
SLACK_CHANNEL="#alerts"

send_slack_alert() {
    local message=$1
    local color=$2
    
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"channel\":\"$SLACK_CHANNEL\",\"text\":\"$message\",\"color\":\"$color\"}" \
        "$SLACK_WEBHOOK"
}

# Example usage
send_slack_alert "🚨 Service Alert: nginx is down" "danger"
send_slack_alert "✅ Service Recovery: nginx is up" "good"
```

## Troubleshooting Guide

### Common Issues

#### Docker Container Issues

##### Container Won't Start
```bash
# Check container logs
docker logs homelab-docs-mkdocs
docker logs homelab-docs-ai-backend

# Check container status
docker inspect homelab-docs-mkdocs

# Check resource usage
docker stats

# Common fixes
# 1. Restart services
docker-compose -f docker/docker-compose.yml restart

# 2. Rebuild images
docker-compose -f docker/docker-compose.yml build --no-cache

# 3. Clean up and restart
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up --force-recreate
```

##### High Memory Usage
```bash
# Check memory usage by container
docker stats --no-stream | grep -E "(mkdocs|ai-backend|redis|nginx)"

# Check for memory leaks
docker exec homelab-docs-ai-backend python -m tracemalloc --count 10 --dump

# Restart high-memory container
docker restart homelab-docs-ai-backend

# Optimize memory usage
# Update docker-compose.yml with memory limits
# Update application configuration for memory efficiency
```

##### Network Connectivity Issues
```bash
# Check network configuration
docker network ls
docker network inspect homelab-docs_default

# Test connectivity between containers
docker exec homelab-docs-mkdocs ping homelab-docs-ai-backend

# Check port conflicts
netstat -tuln | grep -E ":(80|8000|8001|443|6379)"

# Restart network
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up
```

#### Application Issues

##### AI Backend Not Responding
```bash
# Check backend logs
docker logs homelab-docs-ai-backend | tail -50

# Check backend health
curl http://localhost:8001/health

# Check OpenAI API key
docker exec homelab-docs-ai-backend python -c "
import os
print('OpenAI API Key:', bool(os.getenv('OPENAI_API_KEY')))
"

# Restart backend
docker restart homelab-docs-ai-backend

# Check resource allocation
docker stats homelab-docs-ai-backend
```

##### Search Functionality Issues
```bash
# Check search API
curl -X POST http://localhost:8001/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}'

# Check Elasticsearch (if used)
curl -X GET "http://localhost:9200/_cluster/health?pretty"

# Rebuild search index
docker exec homelab-docs-ai-backend python -c "
from ai_backend.app import create_app
app = create_app()
with app.app_context():
    from ai_backend.search import rebuild_index
    rebuild_index()
"

# Clear search cache
docker exec homelab-docs-redis redis-cli FLUSHALL
```

##### Documentation Rendering Issues
```bash
# Check MkDocs logs
docker logs homelab-docs-mkdocs

# Check MkDocs configuration
docker exec homelab-docs-mkdocs cat mkdocs.yml

# Rebuild documentation
docker exec homelab-docs-mkdocs mkdocs build --clean

# Check file permissions
docker exec homelab-docs-mkdocs ls -la docs/
```

#### Performance Issues

##### Slow Response Times
```bash
# Profile API endpoints
curl -w "@-" -o /dev/null -s "GET /api/health" http://localhost:8001

# Check database performance
docker exec homelab-docs-redis redis-cli INFO commandstats

# Monitor system resources
docker stats --no-stream | head -5

# Optimize database
docker exec homelab-docs-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Update configuration for performance
# Adjust worker processes
# Enable caching
# Optimize database queries
```

##### High CPU Usage
```bash
# Check CPU usage by process
docker exec homelab-docs-ai-backend top -b -n 1

# Profile application
docker exec homelab-docs-ai-backend python -m cProfile -o /tmp/profile.stats -s timeit

# Identify resource-intensive operations
# Check logs for CPU-intensive tasks
# Monitor AI API usage

# Scale if needed
# Increase container resources
# Implement caching
# Optimize algorithms
```

### Emergency Procedures

#### Service Recovery
```bash
#!/bin/bash
# Emergency service recovery script

# Stop all services
echo "Stopping all services..."
docker-compose -f docker/docker-compose.yml down

# Check for data corruption
echo "Checking for data corruption..."
# Run filesystem checks
# Verify database integrity

# Start services one by one
echo "Starting Redis..."
docker-compose -f docker/docker-compose.yml up -d redis
sleep 5

echo "Starting AI Backend..."
docker-compose -f docker/docker-compose.yml up -d ai-backend
sleep 10

echo "Starting MkDocs..."
docker-compose -f docker/docker-compose.yml up -d mkdocs
sleep 5

echo "Starting Nginx..."
docker-compose -f docker/docker-compose.yml up -d nginx

# Verify all services are running
docker-compose -f docker/docker-compose.yml ps

echo "Emergency recovery completed"
```

#### Data Recovery
```bash
#!/bin/bash
# Data recovery script
BACKUP_DIR="/backup/homelab-docs/emergency"
RESTORE_DIR="/tmp/emergency-restore"

# Create restore directory
mkdir -p $RESTORE_DIR

# Find latest backup
LATEST_BACKUP=$(find $BACKUP_DIR -name "*.tar.gz" -type f -printf '%T@%p\t%f\n' | sort -nr | head -1 | awk '{print $2}')

if [[ -n "$LATEST_BACKUP" ]]; then
    echo "Restoring from: $LATEST_BACKUP"
    
    # Extract backup
    tar -xzf "$BACKUP_DIR/$LATEST_BACKUP" -C $RESTORE_DIR
    
    # Stop services
    docker-compose -f docker/docker-compose.yml down
    
    # Restore Docker volumes
    if [[ -f "$RESTORE_DIR/uploads" ]]; then
        docker run --rm -v $RESTORE_DIR/uploads:/data \
            alpine tar xzf "$RESTORE_DIR/uploads" -C /data
    fi
    
    if [[ -f "$RESTORE_DIR/redis" ]]; then
        docker run --rm -v $RESTORE_DIR/redis:/data \
            alpine tar xzf "$RESTORE_DIR/redis" -C /data
    fi
    
    # Restore configuration files
    if [[ -f "$RESTORE_DIR/configs.tar.gz" ]]; then
        tar -xzf "$RESTORE_DIR/configs.tar.gz"
    fi
    
    # Start services
    docker-compose -f docker/docker-compose.yml up -d
    
    echo "Data recovery completed from $LATEST_BACKUP"
else
    echo "No backup found for recovery"
fi
```

## Performance Optimization

### Database Optimization

#### Redis Configuration
```bash
# /usr/local/etc/redis/redis.conf

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
stop-writes-on-bgsave yes

# Security
requirepass your_strong_password_here
rename-command FLUSHDB "SECURE_FLUSH"

# Performance
tcp-keepalive 300
timeout 0
```

#### Database Monitoring
```bash
#!/bin/bash
# Database monitoring script
REDIS_CLI="redis-cli"

# Memory usage
echo "Redis Memory Usage:"
$REDIS_CLI info memory | grep -E "(used_memory|maxmemory)"

# Key statistics
echo "Redis Key Statistics:"
$REDIS_CLI info keyspace

# Connection statistics
echo "Redis Connection Statistics:"
$REDIS_CLI info clients

# Performance metrics
echo "Redis Performance Metrics:"
$REDIS_CLI info stats

# Slow queries (if enabled)
$REDIS_CLI slowlog get 10
```

### Application Optimization

#### Caching Strategy
```python
# Python caching configuration
CACHE_TYPE = "redis"
CACHE_TTL = 3600  # 1 hour
CACHE_MAX_SIZE = 1000

# Cache configuration
if CACHE_TYPE == "redis":
    REDIS_URL = "redis://localhost:6379/0"
    REDIS_PASSWORD = None

# Cache implementation
def get_from_cache(key):
    if CACHE_TYPE == "redis":
        import redis
        r = redis.Redis.from_url(REDIS_URL, password=REDIS_PASSWORD)
        return r.get(key)
    return None

def set_to_cache(key, value, ttl=None):
    if CACHE_TYPE == "redis":
        import redis
        r = redis.Redis.from_url(REDIS_URL, password=REDIS_PASSWORD)
        r.setex(key, value, ttl or CACHE_TTL)
```

#### Load Balancing
```yaml
# docker-compose.yml with multiple backend instances
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ai-backend-1
      - ai-backend-2

  ai-backend-1:
    build: ./ai-backend
    environment:
      - REDIS_URL=redis://redis:6379/0
      - WORKER_ID=1
    depends_on:
      - redis

  ai-backend-2:
    build: ./ai-backend
    environment:
      - REDIS_URL=redis://redis:6379/1
      - WORKER_ID=2
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

```nginx
# Load balancing configuration
upstream ai_backend {
    least_conn;
    server ai-backend-1:8000;
    server ai-backend-2:8000;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://ai_backend;
    }
}
```

## Security Maintenance

### Regular Security Tasks

#### SSL Certificate Management
```bash
#!/bin/bash
# SSL certificate management script
CERT_DIR="docker/ssl"
DOMAIN="yourdomain.com"

# Check certificate expiry
check_cert_expiry() {
    local cert_file="$CERT_DIR/fullchain.pem"
    local expiry_date=$(openssl x509 -in "$cert_file" -noout -dates | awk '/notAfter/ {print $1}')
    local expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    if [[ $days_until_expiry -lt 30 ]]; then
        echo "Certificate expires in $days_until_expiry days"
        return 1
    fi
    
    return 0
}

# Generate new certificate
generate_cert() {
    local cert_name="$DOMAIN-$(date +%Y%m%d)"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERT_DIR/$cert_name.key" \
        -out "$CERT_DIR/$cert_name.crt" \
        -subj "/C=US/ST=State/L=City/O=Homelab/CN=$DOMAIN"
    
    echo "New certificate generated: $cert_name"
}

# Update Nginx configuration
update_nginx_config() {
    local cert_name="$DOMAIN-$(date +%Y%m%d)"
    
    # Update nginx.conf with new certificate paths
    sed -i "s|ssl_certificate .*|ssl_certificate $CERT_DIR/$cert_name.crt|g" docker/nginx.conf
    sed -i "s|ssl_certificate_key .*|ssl_certificate_key $CERT_DIR/$cert_name.key|g" docker/nginx.conf
    
    echo "Nginx configuration updated"
}

# Rotate certificates
rotate_certificates() {
    if check_cert_expiry; then
        generate_cert
        update_nginx_config
        docker-compose -f docker/docker-compose.yml restart nginx
        echo "Certificates rotated successfully"
    else
        echo "Certificate is still valid"
    fi
}
```

#### Security Scanning
```bash
#!/bin/bash
# Security scanning script
SCAN_DATE=$(date +%Y-%m-%d)
SCAN_REPORT="/var/log/security-scan/$SCAN_DATE.md"

mkdir -p "$(dirname "$SCAN_REPORT")"

# Docker security scan
echo "Docker Security Scan - $SCAN_DATE" > $SCAN_REPORT
echo "=========================" >> $SCAN_REPORT

echo "## Docker Images" >> $SCAN_REPORT
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" >> $SCAN_REPORT

echo "## Docker Security" >> $SCAN_REPORT
docker scan --format json >> $SCAN_REPORT

# Network security scan
echo "## Network Security" >> $SCAN_REPORT
netstat -tuln | grep LISTEN >> $SCAN_REPORT

# File permissions audit
echo "## File Permissions" >> $SCAN_REPORT
find /opt/homelab-docs -type f -perm /o+w >> $SCAN_REPORT 2>/dev/null || true

echo "Security scan completed: $SCAN_REPORT"
```

### Incident Response

#### Security Incident Procedure
```bash
#!/bin/bash
# Security incident response script
INCIDENT_DATE=$(date +%Y-%m-%d)
INCIDENT_LOG="/var/log/security-incident/$INCIDENT_DATE.log"

# Immediate actions
immediate_actions() {
    echo "SECURITY INCIDENT DETECTED - $(date)" >> $INCIDENT_LOG
    
    # Isolate affected systems
    echo "Isolating affected systems..." >> $INCIDENT_LOG
    
    # Stop unnecessary services
    docker-compose -f docker/docker-compose.yml stop ai-backend
    
    # Enable enhanced logging
    # Increase log levels
    # Enable audit logging
    
    # Change passwords
    # Rotate API keys
    
    echo "Immediate actions completed" >> $INCIDENT_LOG
}

# Investigation
investigate() {
    echo "Starting investigation..." >> $INCIDENT_LOG
    
    # Collect logs
    docker logs homelab-docs-nginx > /tmp/nginx-incident.log
    docker logs homelab-docs-ai-backend > /tmp/backend-incident.log
    
    # Analyze logs for suspicious activity
    grep -i "error\|fail\|auth\|unauthorized" /tmp/nginx-incident.log
    grep -i "error\|fail\|auth\|unauthorized" /tmp/backend-incident.log
    
    # Check for unusual processes
    docker exec homelab-docs-ai-backend ps aux
    
    # Check network connections
    docker exec homelab-docs-ai-backend netstat -tuln
    
    echo "Investigation completed" >> $INCIDENT_LOG
}

# Recovery
recovery() {
    echo "Starting recovery..." >> $INCIDENT_LOG
    
    # Restore from backup if needed
    # Rebuild containers
    # Update configurations
    # Test systems
    
    # Monitor for continued issues
    # Implement additional security measures
    
    echo "Recovery completed" >> $INCIDENT_LOG
}

# Incident response workflow
echo "Security incident response workflow triggered"
immediate_actions
investigate
recovery
```

## Backup and Disaster Recovery

### Backup Strategies

#### 3-2-1 Backup Strategy
```bash
#!/bin/bash
# 3-2-1 backup strategy implementation
BACKUP_DIR="/backup/homelab-docs"
RETENTION_DAYS_DAILY=7
RETENTION_DAYS_WEEKLY=30
RETENTION_DAYS_MONTHLY=90

# Daily backups
create_daily_backup() {
    local date=$(date +%Y-%m-%d)
    local backup_dir="$BACKUP_DIR/daily/$date"
    
    mkdir -p "$backup_dir"
    
    # Backup configuration and database
    tar -czf "$backup_dir/config-$date.tar.gz" .env docker/
    
    # Backup Docker volumes
    docker run --rm \
        -v homelab-docs_ai_uploads:/data \
        -v "$backup_dir":/backup \
        alpine tar czf "backup/uploads-$date.tar.gz" -C /data
    
    # Cleanup old daily backups
    find "$BACKUP_DIR/daily" -name "*.tar.gz" -mtime +$RETENTION_DAYS_DAILY -delete
}

# Weekly backups
create_weekly_backup() {
    local date=$(date +%Y-%m-%d)
    local backup_dir="$BACKUP_DIR/weekly/$date"
    
    mkdir -p "$backup_dir"
    
    # Full system backup
    docker run --rm \
        -v homelab-docs_ai_uploads:/data \
        -v homelab-docs_redis:/data \
        -v "$backup_dir":/backup \
        alpine tar czf "backup/full-$date.tar.gz" -C /data
    
    # Cleanup old weekly backups
    find "$BACKUP_DIR/weekly" -name "*.tar.gz" -mtime +$RETENTION_DAYS_WEEKLY -delete
}

# Monthly backups
create_monthly_backup() {
    local date=$(date +%Y-%m-%d)
    local backup_dir="$BACKUP_DIR/monthly/$date"
    
    mkdir -p "$backup_dir"
    
    # Archive all backups
    tar -czf "$backup_dir/archive-$date.tar.gz" "$BACKUP_DIR/daily"
    tar -czf "$backup_dir/configs-$date.tar.gz" .env docker/ scripts/
    
    # Cleanup old monthly archives
    find "$BACKUP_DIR/monthly" -name "*.tar.gz" -mtime +$RETENTION_DAYS_MONTHLY -delete
}

# Execute backup strategy
echo "Starting 3-2-1 backup strategy"
create_daily_backup
create_weekly_backup
create_monthly_backup
echo "3-2-1 backup strategy completed"
```

#### Offsite Backup
```bash
#!/bin/bash
# Offsite backup script
BACKUP_DIR="/backup/homelab-docs"
REMOTE_BACKUP="user@backup-server.com:/backups/homelab-docs"

# Sync backups to remote location
sync_to_remote() {
    echo "Syncing backups to remote location..."
    
    # Using rsync for efficient sync
    rsync -avz --delete \
        --exclude="*.tmp" \
        --exclude="*.log" \
        "$BACKUP_DIR/" \
        "$REMOTE_BACKUP"
    
    # Verify sync
    if [[ $? -eq 0 ]]; then
        echo "Remote backup completed successfully"
    else
        echo "Remote backup failed"
        # Send alert
        # Check network connectivity
        # Retry sync
    fi
}

# Offsite backup verification
verify_remote_backup() {
    echo "Verifying remote backup..."
    
    # Check remote directory
    ssh user@backup-server "ls -la /backups/homelab-docs" > /tmp/remote-backup-list.txt
    
    # Compare local and remote
    # Check file sizes and modification times
    # Verify backup integrity
    
    echo "Remote backup verification completed"
}

# Execute offsite backup
echo "Starting offsite backup"
sync_to_remote
verify_remote_backup
```

### Disaster Recovery

#### Recovery Procedures
```bash
#!/bin/bash
# Disaster recovery script
RECOVERY_DATE=$(date +%Y-%m-%d)
RECOVERY_LOG="/var/log/disaster-recovery/$RECOVERY_DATE.log"

mkdir -p "$(dirname "$RECOVERY_LOG")"

# Assess damage
assess_damage() {
    echo "Assessing damage..." >> $RECOVERY_LOG
    
    # Check system status
    docker-compose -f docker/docker-compose.yml ps >> $RECOVERY_LOG 2>&1
    
    # Check data integrity
    # Check file systems
    # Check database consistency
    
    # Document current state
    echo "System assessment completed" >> $RECOVERY_LOG
}

# Recovery plan
create_recovery_plan() {
    echo "Creating recovery plan..." >> $RECOVERY_LOG
    
    # Identify critical services
    # Prioritize recovery tasks
    # Estimate recovery time
    # Plan resource allocation
    
    echo "Recovery plan created" >> $RECOVERY_LOG
}

# Execute recovery
execute_recovery() {
    echo "Executing recovery..." >> $RECOVERY_LOG
    
    # Restore from backups
    # Rebuild systems
    # Test functionality
    # Monitor for issues
    
    echo "Recovery execution completed" >> $RECOVERY_LOG
}

# Disaster recovery workflow
echo "Initiating disaster recovery procedure"
assess_damage
create_recovery_plan
execute_recovery
```

## Maintenance Scheduling

### Cron Jobs Setup

#### Daily Maintenance
```bash
# /etc/cron.d/homelab-docs-daily
# Daily health checks at 2 AM
0 2 * * /opt/homelab-docs/scripts/daily-health.sh >> /var/log/homelab-docs-daily.log 2>&1

# Daily log rotation at 3 AM
0 3 * * /opt/homelab-docs/scripts/rotate-logs.sh >> /var/log/homelab-docs-daily.log 2>&1

# Daily backup at 4 AM
0 4 * * /opt/homelab-docs/scripts/daily-backup.sh >> /var/log/homelab-docs-daily.log 2>&1
```

#### Weekly Maintenance
```bash
# /etc/cron.d/homelab-docs-weekly
# Weekly maintenance every Sunday at 1 AM
0 1 * * 0 /opt/homelab-docs/scripts/weekly-maintenance.sh >> /var/log/homelab-docs-weekly.log 2>&1

# Weekly backup every Sunday at 2 AM
0 2 * * 0 /opt/homelab-docs/scripts/weekly-backup.sh >> /var/log/homelab-docs-weekly.log 2>&1
```

#### Monthly Maintenance
```bash
# /etc/cron.d/homelab-docs-monthly
# Monthly maintenance on the 1st of each month at 3 AM
0 3 1 * * /opt/homelab-docs/scripts/monthly-maintenance.sh >> /var/log/homelab-docs-monthly.log 2>&1

# Monthly backup on the 1st of each month at 4 AM
0 4 1 * * /opt/homelab-docs/scripts/monthly-backup.sh >> /var/log/homelab-docs-monthly.log 2>&1
```

## Documentation

### Maintenance Documentation
- **Runbooks**: Step-by-step procedures for common maintenance tasks
- **Checklists**: Comprehensive checklists for maintenance activities
- **Incident Reports**: Templates for documenting security incidents
- **Performance Reports**: Regular performance analysis and reporting

### Knowledge Base
- **Troubleshooting Guides**: Solutions to common issues
- **Best Practices**: Maintenance best practices and guidelines
- **Configuration Reference**: Complete configuration documentation

### Change Management
- **Change Log**: Detailed log of all changes made
- **Rollback Procedures**: Steps to undo changes if needed
- **Testing Procedures**: Testing protocols for changes
- **Approval Workflows**: Change approval processes

---

*This maintenance guide provides comprehensive procedures for keeping the Homelab Documentation Hub platform running smoothly and securely.*

---
title: Monitoring
description: Complete monitoring and alerting solutions for homelab environments
---

# Monitoring and Observability

Effective monitoring is crucial for maintaining a healthy homelab environment. This section covers metrics collection, visualization, alerting, and log management to keep your systems running smoothly.

## 📊 Monitoring Stack Overview

### Classic Stack (Prometheus-based)
```bash
Prometheus     # Metrics collection
Grafana        # Visualization
AlertManager   # Alerting
Node Exporter  # System metrics
```

### Modern Stack (ELK-based)
```bash
Elasticsearch   # Log storage
Kibana        # Log visualization
Logstash      # Log processing
Beats         # Log shippers
```

### All-in-One Solutions
```bash
Netdata       # Real-time monitoring
Zabbix        # Enterprise monitoring
Observium    # Network monitoring
LibreNMS      # Network monitoring
```

## 📚 Monitoring Documentation

### [Grafana Dashboards](grafana.md)
- Dashboard creation and management
- Data source configuration
- Alert rules and notifications
- Community dashboards

### [Prometheus Setup](prometheus.md)
- Metrics collection and storage
- Service discovery
- Exporters configuration
- Querying and alerting

### [Alert Management](alerts.md)
- Alert rule configuration
- Notification channels
- Incident response procedures
- Escalation policies

## 🎯 What to Monitor

### System Metrics

#### CPU and Memory
```bash
CPU Usage:       Overall utilization, per-core, load average
Memory Usage:    Total, used, free, cached, swap
Process Count:   Number of running processes
Context Switches: System scheduling efficiency
```

#### Storage and I/O
```bash
Disk Usage:      Used/available space, inode usage
Disk I/O:       Read/write operations, latency, queue depth
File Descriptors: Open files, limits
Mount Points:    Availability, permissions
```

#### Network Metrics
```bash
Bandwidth:       In/out traffic by interface
Packet Loss:     Error rates, dropped packets
Connections:     Active TCP/UDP connections
Latency:         Round-trip times, jitter
```

### Application Metrics

#### Web Services
```bash
Response Time:   Request processing time
Error Rate:      HTTP error codes, exceptions
Throughput:      Requests per second
Active Users:     Concurrent sessions
```

#### Database Metrics
```bash
Connections:     Active, idle, max connections
Query Performance: Slow queries, execution time
Database Size:    Table sizes, index usage
Replication:      Lag, status
```

#### Container Metrics
```bash
Resource Usage:   CPU, memory per container
Network I/O:      Traffic per container
Storage I/O:      Disk usage per container
Health Status:    Container uptime, restarts
```

## 🏗️ Architecture Patterns

### Centralized Monitoring
```
Services → Collectors → Central Server → Dashboards/Alerts
```

**Advantages:**
- Single point of management
- Consistent data storage
- Simplified alerting

**Disadvantages:**
- Single point of failure
- Network dependency
- Scalability concerns

### Distributed Monitoring
```
Services → Local Collectors → Aggregation Layer → Storage/Visualization
```

**Advantages:**
- Better scalability
- Network resilience
- Local processing

**Disadvantages:**
- More complex setup
- Data consistency challenges
- Higher resource usage

### Hybrid Approach
```
Critical Services → Central Monitoring
Standard Services → Distributed Monitoring
```

## 🔧 Implementation Examples

### Prometheus + Grafana Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: 
        - 'server1:9100'
        - 'server2:9100'

  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']

  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - http://example.com
        - https://api.example.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
```

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "Homelab Overview",
    "panels": [
      {
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

### Docker Monitoring Setup

#### Docker Compose Monitoring Stack
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true

volumes:
  prometheus_data:
  grafana_data:
```

### AlertManager Configuration

#### AlertManager Setup
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'alerts@yourdomain.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@yourdomain.com'
                subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```

## 📈 Essential Dashboards

### System Overview Dashboard
```yaml
Panels:
  - System Status (all services up/down)
  - CPU Usage (per server)
  - Memory Usage (per server)
  - Disk Usage (per server)
  - Network Traffic (per interface)
  - Uptime (per server)
```

### Application Dashboard
```yaml
Panels:
  - Request Rate (RPS)
  - Response Time (percentiles)
  - Error Rate (5xx, 4xx)
  - Active Connections
  - Database Connections
  - Cache Hit Rate
```

### Container Dashboard
```yaml
Panels:
  - Container CPU Usage
  - Container Memory Usage
  - Container Network I/O
  - Container Disk I/O
  - Container Restart Count
  - Image Size Distribution
```

## 🚨 Alerting Strategy

### Alert Severity Levels
```bash
Critical:    System down, data loss, security breach
Warning:     High resource usage, performance degradation
Info:        Scheduled maintenance, informational events
```

### Essential Alerts

#### System Alerts
```yaml
- System down (no metrics for 5 minutes)
- High CPU usage (>90% for 10 minutes)
- High memory usage (>95% for 5 minutes)
- Low disk space (<10% available)
- Network connectivity loss
```

#### Application Alerts
```yaml
- High error rate (>5% for 5 minutes)
- Slow response time (>2 seconds p95)
- Database connection issues
- Cache miss rate spike
- Service unavailable
```

#### Security Alerts
```yaml
- Failed login attempts (threshold)
- Unusual network traffic
- Firewall rule changes
- Privilege escalation attempts
- Unknown processes
```

## 🔍 Log Management

### Log Collection Strategies

#### Centralized Logging
```bash
Applications → Log Forwarders → Central Log Server → SIEM/Analysis
```

#### Log Levels
```bash
ERROR:      Critical errors, system failures
WARN:       Warning conditions, potential issues
INFO:       General information, state changes
DEBUG:       Detailed debugging information
TRACE:       Very detailed execution tracing
```

#### Log Retention Policies
```bash
ERROR logs:      1 year
WARN logs:       6 months
INFO logs:       3 months
DEBUG logs:      1 month
TRACE logs:      1 week
```

### ELK Stack Example

#### Logstash Configuration
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "nginx" {
    grok {
      match => { "message" => "%{NGINXACCESS}" }
    }
  }
  
  date {
    match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

## 📋 Best Practices

### General Guidelines
- [ ] Monitor everything that can fail
- [ ] Set meaningful thresholds
- [ ] Test alerting systems
- [ ] Document alert procedures
- [ ] Review and update dashboards

### Performance Considerations
- [ ] Optimize metric collection
- [ ] Use appropriate retention periods
- [ ] Monitor the monitoring system
- [ ] Scale horizontally when needed
- [ ] Cache frequently accessed data

### Security Considerations
- [ ] Secure monitoring endpoints
- [ ] Use authentication and authorization
- [ ] Encrypt sensitive data
- [ ] Regular security updates
- [ ] Audit access logs

## 🛠️ Troubleshooting Monitoring

### Common Issues

#### Missing Metrics
```bash
# Check collector status
curl http://localhost:9100/metrics

# Verify Prometheus configuration
promtool check config prometheus.yml

# Check network connectivity
telnet target 9100
```

#### Alert Not Firing
```bash
# Check alert rules
promtool check rules alert_rules.yml

# Verify AlertManager configuration
amtool check-config alertmanager.yml

# Test alert manually
curl -X POST http://localhost:9093/api/v1/alerts -d '[{"labels":{"alertname":"Test"}}]'
```

#### Dashboard Loading Issues
```bash
# Check Grafana logs
docker logs grafana

# Verify data source connectivity
curl http://localhost:9090/api/v1/query?query=up

# Check Grafana configuration
ls -la /etc/grafana/
```

---

**Ready to monitor?** Start with our [Grafana Dashboards](grafana.md) guide for beautiful visualizations!

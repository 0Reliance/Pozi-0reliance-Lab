---
title: Prometheus Monitoring Setup
description: Complete guide for Prometheus installation, configuration, and metric collection in homelab environments
---

# Prometheus Monitoring Setup

Prometheus is the de facto standard for monitoring and alerting in modern homelabs. This comprehensive guide covers Prometheus installation, configuration, metric collection, and integration with other monitoring tools.

## 📊 Prometheus Fundamentals

### Monitoring Architecture
```bash
# Prometheus Architecture Overview

Prometheus Server:
  Role: Central monitoring and storage
  Functions: Metric collection, querying, alerting
  Storage: Time-series database (TSDB)
  Query Language: PromQL (Prometheus Query Language)

Data Collection:
  Pull-based: Active scraping of targets
  Protocols: HTTP/HTTPS, multiple formats
  Intervals: Configurable scrape intervals
  Retention: Configurable data retention

Service Discovery:
  Static: Manually configured targets
  DNS: DNS-based service discovery
  File: File-based target discovery
  Kubernetes: K8s API-based discovery
  Consul: HashiCorp Consul integration

Exporters:
  Node Exporter: System metrics (CPU, memory, disk)
  Blackbox Exporter: Network probing (HTTP, TCP, ICMP)
  cAdvisor: Container metrics
  Custom Exporters: Application-specific metrics
```

### Core Concepts
```bash
# Prometheus Data Model

Metrics:
  Types: Counter, Gauge, Histogram, Summary
  Labels: Key-value pairs for dimensionality
  Naming: Consistent naming conventions
  Units: Standard unit specifications

Time Series:
  Definition: Metric + unique label set
  Storage: Compressed time-series data
  Retention: Configurable retention periods
  Sampling: Regular interval collection

Queries:
  Language: PromQL (Prometheus Query Language)
  Functions: Mathematical, aggregation, temporal
  Range Vectors: Time-range queries
  Instant Vectors: Point-in-time queries

Alerting:
  Rules: Alert condition definitions
  Evaluation: Regular rule evaluation
  Silences: Temporary alert suppression
  Routing: Alertmanager notification routing
```

## 🔧 Prometheus Installation

### System Requirements
```bash
# Minimum Requirements
CPU: 2+ cores (4+ recommended)
RAM: 4GB+ (8GB+ recommended for large setups)
Storage: 50GB+ SSD (500GB+ for long retention)
Network: Gigabit Ethernet

# Recommended Homelab Setup
CPU: 4+ cores
RAM: 8GB+ 
Storage: 500GB+ SSD
Network: 10GbE (for high-volume data)

# Performance Considerations
- SSD storage for better I/O performance
- Sufficient RAM for caching and queries
- Network bandwidth for multiple targets
- Consider dedicated monitoring server
```

### Binary Installation
```bash
# Download Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-2.40.0.linux-amd64

# Create Prometheus User
sudo useradd --no-create-home --shell /bin/false prometheus

# Create Directories
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus
sudo mkdir -p /var/log/prometheus

# Copy Files
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
sudo cp -r consoles /etc/prometheus/
sudo cp -r console_libraries /etc/prometheus/

# Set Permissions
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus
sudo chown -R prometheus:prometheus /var/log/prometheus
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

### Docker Installation
```bash
# Pull Prometheus Image
docker pull prom/prometheus:v2.40.0

# Create Directories
sudo mkdir -p /prometheus/data
sudo mkdir -p /prometheus/config
sudo chown -R 65534:65534 /prometheus

# Docker Compose Configuration
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.40.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - /prometheus/data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:v1.5.0
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.rootfs=/rootfs'
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
EOF

docker-compose up -d
```

### Systemd Service
```bash
# Create Systemd Service
sudo tee /etc/systemd/system/prometheus.service <<EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --storage.tsdb.retention.time=30d \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
EOF

# Enable and Start Service
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus

# Verify Service
sudo systemctl status prometheus
curl http://localhost:9090/metrics
```

## ⚙️ Configuration

### Basic Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'homelab'
    region: 'datacenter-1'

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'blackbox'
    metrics_path: /probe
    static_configs:
      - targets:
        - http://google.com
        - https://github.com
        - http://localhost:8080

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Advanced Configuration
```yaml
# Advanced prometheus.yml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
  external_labels:
    environment: 'production'

# Remote Write (for long-term storage)
remote_write:
  - url: "http://influxdb:8086/api/v1/prom/write?db=prometheus"
    queue_config:
      max_samples_per_send: 1000
      max_shards: 200
      capacity: 2500

# Remote Read (for federation)
remote_read:
  - url: "http://influxdb:8086/api/v1/prom/read?db=prometheus"
    read_recent: true

# Storage Configuration
storage:
  tsdb:
    path: /var/lib/prometheus
    retention.time: 30d
    retention.size: 100GB
    wal-compression: true

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - default
            - monitoring
    relabel_configs:
      - source_labels: [__meta_kubernetes_endpoint_ready]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
        replacement: /metrics
      - source_labels: [__address__, __metrics_path__]
        action: replace
        target_label: __metrics_address__
        regex: ([^:]+)(?::\d+)?
        replacement: $1:9090$2
      - source_labels: [__meta_kubernetes_endpoint_address_target_name]
        action: replace
        target_label: instance
        regex: (.+)
        replacement: $1
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: keep
        regex: https
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: replace
        target_label: __scheme__
        regex: (.+)
        replacement: https
      - source_labels: [__scheme__, __metrics_address__]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
        replacement: $1
    scheme: https
    tls_config:
      insecure_skip_verify: true
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
```

## 📈 Exporters Setup

### Node Exporter
```bash
# Download and Install Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
sudo cp node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin/

# Create Service Account
sudo useradd --no-create-home --shell /bin/false node_exporter

# Create Systemd Service
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --collector.cpu \
    --collector.diskstats \
    --collector.filesystem \
    --collector.meminfo \
    --collector.netdev \
    --collector.stat

[Install]
WantedBy=multi-user.target
EOF

# Enable and Start Service
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

### Blackbox Exporter
```yaml
# blackbox.yml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions:
        - HTTP/1.1
        - HTTP/2
      valid_status_codes: [200, 201, 202]
      method: GET
      headers:
        User-Agent: "Prometheus-Blackbox-Exporter/2.0"
      
  http_post_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions:
        - HTTP/1.1
        - HTTP/2
      valid_status_codes: [200, 201, 202]
      method: POST
      headers:
        Content-Type: "application/json"
      body: '{"test": "data"}'
      
  tcp_connect:
    prober: tcp
    timeout: 3s
    
  icmp_ping:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
```

### Docker Container Metrics
```yaml
# cAdvisor Configuration
cadvisor:
  image: gcr.io/cadvisor/cadvisor:v0.44.0
  container_name: cadvisor
  ports:
    - "8080:8080"
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:rw
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
    - /dev/disk/:/dev/disk:ro
  privileged: true
  devices:
    - /dev/kmsg
  restart: unless-stopped
  command:
    - --housekeeping_interval=10s
    - --max_housekeeping_interval=30s
    - --max_containers=200
    - --storage_duration=60s

# Prometheus Configuration for cAdvisor
- job_name: 'cadvisor'
  scrape_interval: 15s
  metrics_path: /metrics
  static_configs:
    - targets: ['cadvisor:8080']
```

## 🚨 Alerting Configuration

### Alert Rules
```yaml
# rules/alerts.yml
groups:
  - name: system_alerts
    interval: 30s
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is down"
          description: "Instance {{ $labels.instance }} has been down for more than 5 minutes."

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% on {{ $labels.instance }} for more than 5 minutes."

      - alert: HighMemoryUsage
        expr: (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 < 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Available memory is below 20% on {{ $labels.instance }}."

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 10% on {{ $labels.instance }} (mountpoint: {{ $labels.mountpoint }})"

  - name: network_alerts
    interval: 30s
    rules:
      - alert: EndpointDown
        expr: probe_success == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Endpoint {{ $labels.instance }} is down"
          description: "Endpoint {{ $labels.instance }} ({{ $labels.job }}) has been down for more than 2 minutes."

      - alert: SlowResponse
        expr: probe_duration_seconds > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response from {{ $labels.instance }}"
          description: "Response time from {{ $labels.instance }} is above 2 seconds."
```

### Alertmanager Configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@homelab.local'
  smtp_auth_username: 'alerts@homelab.local'
  smtp_auth_password: 'app-password'
  smtp_require_tls: true

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
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/'
        send_resolved: true

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@homelab.local'
        subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
          {{ end }}

  - name: 'warning-alerts'
    email_configs:
      - to: 'team@homelab.local'
        subject: '[WARNING] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

## 🔍 Querying and Analysis

### PromQL Examples
```bash
# Basic Queries
up                                    # Which instances are up?
node_cpu_seconds_total                  # Total CPU time
node_memory_MemAvailable_bytes       # Available memory
rate(node_cpu_seconds_total[5m])     # CPU usage rate

# Aggregation
sum(rate(node_cpu_seconds_total[5m])) by (instance)    # CPU per instance
avg(node_memory_MemAvailable_bytes) by (instance)     # Average memory
topk(5, rate(http_requests_total[5m]))             # Top 5 busiest services

# Time Range Queries
rate(http_requests_total[1h])                         # Requests per hour
increase(node_cpu_seconds_total[1h])                  # CPU time in last hour
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Conditional Logic
up == 0                                  # Down instances
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.2  # Low memory
rate(node_cpu_seconds_total{mode="idle"}[5m]) < 0.2  # High CPU

# Mathematical Operations
100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)  # CPU percentage
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100  # Disk usage
```

### Recording Rules
```yaml
# rules/recordings.yml
groups:
  - name: system_recording_rules
    interval: 30s
    rules:
      - record: instance:cpu_usage_percent
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

      - record: instance:memory_usage_percent
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

      - record: instance:disk_usage_percent
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100

      - record: instance:network_receive_rate
        expr: rate(node_network_receive_bytes_total[5m]) * 8

      - record: instance:network_transmit_rate
        expr: rate(node_network_transmit_bytes_total[5m]) * 8

  - name: application_recording_rules
    interval: 30s
    rules:
      - record: application:request_rate
        expr: sum by (job, instance) (rate(http_requests_total[5m]))

      - record: application:error_rate
        expr: sum by (job, instance) (rate(http_requests_total{status=~"5.."}[5m])) / sum by (job, instance) (rate(http_requests_total[5m])) * 100

      - record: application:response_time_p95
        expr: histogram_quantile(0.95, sum by (le, job, instance) (rate(http_request_duration_seconds_bucket[5m])))
```

## 📊 Dashboard Integration

### Grafana Data Source
```bash
# Add Prometheus as Grafana Data Source
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' \
  http://admin:admin@grafana:3000/api/datasources
```

### Example Dashboard JSON
```json
{
  "dashboard": {
    "title": "Homelab System Overview",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 90}
              ]
            }
          }
        }
      },
      {
        "title": "Memory Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 90}
              ]
            }
          }
        }
      },
      {
        "title": "Disk Usage",
        "type": "table",
        "targets": [
          {
            "expr": "(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100",
            "legendFormat": "{{instance}} - {{mountpoint}}"
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "excludeByName": {"Time": true},
              "indexByName": {},
              "renameByName": {
                "Value": "Usage %"
              }
            }
          }
        ]
      }
    ]
  }
}
```

## 🔧 Advanced Configuration

### Remote Storage Integration
```yaml
# Long-term storage with Thanos
global:
  external_labels:
    cluster: 'homelab'
    replica: 'prometheus-1'

remote_write:
  - url: "http://thanos-receive:19291/api/v1/receive"
    send_exemplars: true
    send_timeout: 30s
    queue_config:
      max_samples_per_send: 10000
      max_shards: 200
      capacity: 25000

# Federation
scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s
    honor_labels: true
    metrics_path: /federate
    static_configs:
      - targets: ['prometheus-1:9090', 'prometheus-2:9090']
```

### High Availability Setup
```bash
# HA Prometheus with Thanos
version: '3.8'

services:
  prometheus-1:
    image: prom/prometheus:v2.40.0
    command:
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
      - '--storage.tsdb.retention.time=15d'
      - '--web.external-url=http://prometheus-1:9090'
    volumes:
      - ./prometheus1.yml:/etc/prometheus/prometheus.yml
      - prometheus1-data:/prometheus
    ports:
      - "9090:9090"

  prometheus-2:
    image: prom/prometheus:v2.40.0
    command:
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
      - '--storage.tsdb.retention.time=15d'
      - '--web.external-url=http://prometheus-2:9090'
    volumes:
      - ./prometheus2.yml:/etc/prometheus/prometheus.yml
      - prometheus2-data:/prometheus
    ports:
      - "9091:9090"

  thanos-receive:
    image: quay.io/thanos/thanos:v0.31.0
    command:
      - receive
      - --tsdb.path=/data
      - --objstore.config-file=/conf/bucket.yml
      - --grpc-address=0.0.0.0:19291
      - --http-address=0.0.0.0:19292
    volumes:
      - thanos-data:/data
      - ./thanos-bucket.yml:/conf/bucket.yml
    ports:
      - "19291:19291"
      - "19292:19292"
```

## 🚨 Troubleshooting

### Common Issues
```bash
# Service Not Starting
sudo journalctl -u prometheus -f
sudo prometheus --config.file=/etc/prometheus/prometheus.yml --check

# Metrics Not Collecting
curl http://localhost:9090/targets
curl http://localhost:9100/metrics
curl http://blackbox-exporter:9115/probe?module=http_2xx&target=http://example.com

# High Memory Usage
curl http://localhost:9090/api/v1/status/tsdb
curl http://localhost:9090/api/v1/status/config

# Slow Queries
curl -g 'http://localhost:9090/api/v1/query?query=up&time=2023-01-01T00:00:00Z'
curl 'http://localhost:9090/api/v1/query_range?query=rate(node_cpu_seconds_total[5m])&start=2023-01-01T00:00:00Z&end=2023-01-01T01:00:00Z&step=15s'
```

### Performance Tuning
```yaml
# Performance Optimization
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  query_log_file: /var/log/prometheus/query.log

# Query Concurrency
query:
  max_concurrency: 20
  timeout: 2m

# Storage Optimization
storage:
  tsdb:
    path: /var/lib/prometheus
    retention.time: 15d
    retention.size: 50GB
    wal-compression: true
    samples.per.chunk: 1000
    chunks.to.persist: 5
```

## 📋 Backup and Recovery

### Data Backup
```bash
#!/bin/bash
# Prometheus Backup Script

BACKUP_DIR="/backups/prometheus"
DATE=$(date +%Y%m%d-%H%M%S)
PROMETHEUS_DATA="/var/lib/prometheus"

mkdir -p "$BACKUP_DIR"

# Create snapshot
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Find and copy snapshot
SNAPSHOT_DIR=$(find "$PROMETHEUS_DATA/snapshots" -type d -name "*$(date +%Y%m%d)*" | head -1)
if [ -n "$SNAPSHOT_DIR" ]; then
    tar czf "$BACKUP_DIR/prometheus-snapshot-$DATE.tar.gz" -C "$PROMETHEUS_DATA/snapshots" "$(basename "$SNAPSHOT_DIR")"
    echo "Backup created: $BACKUP_DIR/prometheus-snapshot-$DATE.tar.gz"
else
    echo "No snapshot found"
    exit 1
fi

# Backup configuration
cp /etc/prometheus/prometheus.yml "$BACKUP_DIR/prometheus-config-$DATE.yml"
cp -r /etc/prometheus/rules "$BACKUP_DIR/rules-$DATE"

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.yml" -mtime +7 -delete
```

## 📖 Further Reading

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Reference](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alerting Documentation](https://prometheus.io/docs/alerting/latest/overview/)

### Communities
- Reddit: r/prometheus, r/monitoring, r/homelab
- Prometheus Community Slack
- CNCF Discord Server

### Advanced Topics
- Thanos for long-term storage
- Cortex for horizontal scaling
- VictoriaMetrics for performance
- OpenTelemetry integration

---

**Ready to dive deeper?** Check our [Monitoring](index.md) overview for comprehensive monitoring planning!

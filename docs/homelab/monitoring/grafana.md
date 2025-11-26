---
title: Grafana Dashboard Setup
description: Complete guide for Grafana installation, dashboard creation, and data visualization in homelab environments
---

# Grafana Dashboard Setup

Grafana is the leading open-source visualization and analytics platform that transforms monitoring data into beautiful, insightful dashboards. This comprehensive guide covers Grafana installation, configuration, dashboard creation, and integration with various data sources.

## 📊 Grafana Fundamentals

### Grafana Architecture
```bash
# Grafana Architecture Overview

Frontend (Web UI):
  Role: User interface and dashboard rendering
  Technology: React, TypeScript, Go
  Features: Drag-and-drop editor, real-time updates
  Access: HTTP/HTTPS, authentication methods

Backend (Grafana Server):
  Role: Data processing and API server
  Database: SQLite (default), PostgreSQL, MySQL
  Session Management: Database, Redis, or memory
  Plugins: Dynamic loading system

Data Sources:
  Types: Time-series databases, SQL databases, APIs
  Examples: Prometheus, InfluxDB, PostgreSQL, Elasticsearch
  Authentication: API keys, credentials, certificates
  Querying: Native query languages, SQL, custom

Dashboards:
  Format: JSON configuration
  Panels: Visualizations (graphs, tables, stats)
  Variables: Dynamic filtering and selection
  Templating: Template variables for interactivity
```

### Core Concepts
```bash
# Grafana Components

Data Sources:
  Configuration: Connection settings, authentication
  Types: Prometheus, InfluxDB, PostgreSQL, etc.
  Health: Connection testing, query validation
  Permissions: Role-based access control

Dashboards:
  Panels: Individual visualizations
  Rows: Panel organization and layout
  Variables: Dynamic dashboard filtering
  Annotations: Event marking and documentation

Users and Teams:
  Roles: Viewer, Editor, Admin
  Authentication: Local, LDAP, OAuth, SAML
  Permissions: Dashboard, data source, organization access

Plugins:
  Types: Data source, panel, application
  Repository: Grafana.com plugin registry
  Installation: CLI, web interface, manual
  Management: Enable, disable, update
```

## 🔧 Grafana Installation

### System Requirements
```bash
# Minimum Requirements
CPU: 1+ core (2+ recommended)
RAM: 512MB+ (1GB+ recommended for production)
Storage: 1GB+ (10GB+ for logs and plugins)
Network: HTTP/HTTPS access

# Recommended Homelab Setup
CPU: 2+ cores
RAM: 4GB+ 
Storage: 20GB+ SSD
Network: Gigabit Ethernet

# Database Requirements
SQLite: Built-in, suitable for small deployments
PostgreSQL: Recommended for production, high performance
MySQL: Alternative production database
```

### Binary Installation
```bash
# Download Grafana
wget https://dl.grafana.com/oss/release/grafana-10.0.0.linux-amd64.tar.gz
tar -zxvf grafana-10.0.0.linux-amd64.tar.gz
cd grafana-10.0.0

# Create Grafana User
sudo useradd --system --no-create-home --shell /bin/false grafana

# Create Directories
sudo mkdir -p /etc/grafana/provisioning/{datasources,dashboards}
sudo mkdir -p /var/lib/grafana
sudo mkdir -p /var/log/grafana

# Copy Files
sudo cp bin/grafana-server /usr/local/bin/
sudo cp bin/grafana-cli /usr/local/bin/
sudo cp -r conf /etc/grafana/
sudo cp -r public /usr/share/grafana/
sudo cp -r plugins-bundled /var/lib/grafana/plugins/

# Set Permissions
sudo chown -R grafana:grafana /etc/grafana
sudo chown -R grafana:grafana /var/lib/grafana
sudo chown -R grafana:grafana /var/log/grafana
sudo chown grafana:grafana /usr/local/bin/grafana-*
```

### Docker Installation
```bash
# Pull Grafana Image
docker pull grafana/grafana-oss:10.0.0

# Create Directories
sudo mkdir -p /grafana/data
sudo mkdir -p /grafana/logs
sudo mkdir -p /grafana/provisioning
sudo chown -R 472:472 /grafana

# Docker Compose Configuration
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  grafana:
    image: grafana/grafana-oss:10.0.0
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
      - ./grafana/logs:/var/log/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/grafana.ini:/etc/grafana/grafana.ini
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped

  grafana-db:
    image: postgres:15
    container_name: grafana-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=grafana
      - POSTGRES_USER=grafana
      - POSTGRES_PASSWORD=grafana123
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres-data:
EOF

docker-compose up -d
```

### Systemd Service
```bash
# Create Systemd Service
sudo tee /etc/systemd/system/grafana.service <<EOF
[Unit]
Description=Grafana
After=network.target

[Service]
User=grafana
Group=grafana
Type=notify
Restart=on-failure
RuntimeDirectory=grafana
RuntimeDirectoryMode=0750
WorkingDirectory=/usr/share/grafana
ExecStart=/usr/local/bin/grafana-server \
  --config=/etc/grafana/grafana.ini \
  --pidfile=/var/run/grafana/grafana.pid \
  cfg:default.paths.logs=/var/log/grafana \
  cfg:default.paths.data=/var/lib/grafana \
  cfg:default.paths.plugins=/var/lib/grafana/plugins

[Install]
WantedBy=multi-user.target
EOF

# Create Runtime Directory
sudo mkdir -p /var/run/grafana
sudo chown grafana:grafana /var/run/grafana

# Enable and Start Service
sudo systemctl daemon-reload
sudo systemctl enable grafana
sudo systemctl start grafana

# Verify Service
sudo systemctl status grafana
curl http://localhost:3000/api/health
```

## ⚙️ Configuration

### Basic Configuration
```ini
# /etc/grafana/grafana.ini

[server]
# Protocol (http, https, socket)
protocol = http
# HTTP port
http_port = 3000
# Domain to use
domain = localhost
# Redirect to correct domain if host header does not match domain
enforce_domain = false

[security]
# Admin user name (cli or env variable only)
admin_user = admin
# Admin password (cli or env variable only)
admin_password = admin123
# Secret key for signing
secret_key = SW2YcwTIb9zpOOhoPmiGodhLWE4AwbT8U23FLqpGA
# Disable user signup / registration
allow_sign_up = false

[database]
# Either "mysql", "postgres" or "sqlite3", it's your choice
type = postgres
# For "postgres" or "mysql", use either "unix" or "tcp"
host = grafana-db:5432
# Database name
name = grafana
# For "postgres" or "mysql"
user = grafana
# For "postgres" or "mysql"
password = grafana123

[log]
# Either "console", "file", "syslog". Default is console and file
mode = console, file
# Buffer log writes for better performance
# options ["", "buffer"]
buffer_len = 10000
# Log level
level = info
# For "file" mode, log file path
file = /var/log/grafana/grafana.log

[users]
# Disable user signup / registration
allow_sign_up = false
# Allow non admin users to create organizations
allow_org_create = false
# Set to true to automatically assign new users to the default organization (id 1)
auto_assign_org = true
# Default role new users will be automatically assigned (if disabled above is set to true)
auto_assign_org_role = Viewer
```

### Advanced Configuration
```ini
# Advanced grafana.ini settings

[auth.anonymous]
# Enable anonymous access
enabled = false
# Specify organization name that should be used for unauthenticated users
org_name = Main Org.
# Specify role for unauthenticated users
org_role = Viewer

[auth.basic]
# Enable basic authentication
enabled = true

[smtp]
# Enable mail sending
enabled = true
# SMTP host and port
host = smtp.gmail.com:587
# Username and password
user = grafana@homelab.local
password = app-password
# Use TLS encryption
skip_verify = false
from_address = grafana@homelab.local
from_name = Grafana

[alerting]
# Disable alerting engine
enabled = true
# Execute alerts in background concurrent
execute_alerts = true
# Default setting for new alert rules
frequency_interval = 60s
# Default setting for new alert rules
grace_period = 5m
# Notification engine
notification_timeout = 30s

[plugins]
# Enable or disable the plugin manager
plugin_admin_enabled = true
# Enter a comma-separated list of plugins to allow loading
allow_loading_unsigned_plugins = false
# Enter a comma-separated list of plugins to update
plugin_update_seconds = 86400
```

## 📈 Data Sources Configuration

### Prometheus Data Source
```bash
# Add Prometheus via API
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "Prometheus-Homelab",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true,
    "jsonData": {
      "timeInterval": "15s",
      "queryTimeout": "60s",
      "httpMethod": "POST"
    },
    "secureJsonData": {}
  }' \
  http://localhost:3000/api/datasources

# Prometheus Configuration JSON
{
  "name": "Prometheus-Homelab",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "isDefault": true,
  "editable": true,
  "jsonData": {
    "timeInterval": "15s",
    "queryTimeout": "60s",
    "httpMethod": "POST",
    "exemplarTraceIdDestinations": []
  },
  "secureJsonData": {}
}
```

### InfluxDB Data Source
```bash
# Add InfluxDB via API
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "InfluxDB-Homelab",
    "type": "influxdb",
    "url": "http://influxdb:8086",
    "database": "homelab",
    "user": "grafana",
    "password": "grafana123",
    "access": "proxy",
    "jsonData": {
      "version": "Flux",
      "organization": "homelab",
      "defaultBucket": "metrics",
      "tlsSkipVerify": true
    },
    "secureJsonData": {
      "password": "grafana123"
    }
  }' \
  http://localhost:3000/api/datasources
```

### PostgreSQL Data Source
```bash
# Add PostgreSQL via API
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "PostgreSQL-Homelab",
    "type": "postgres",
    "url": "grafana-db:5432",
    "database": "applications",
    "user": "grafana",
    "password": "grafana123",
    "access": "proxy",
    "jsonData": {
      "sslmode": "disable"
    },
    "secureJsonData": {
      "password": "grafana123"
    }
  }' \
  http://localhost:3000/api/datasources
```

## 🎨 Dashboard Creation

### System Overview Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Homelab System Overview",
    "tags": ["homelab", "system", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "CPU Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}",
            "refId": "A"
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
            },
            "mappings": [],
            "color": {
              "mode": "thresholds"
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"],
            "fields": ""
          },
          "orientation": "auto",
          "textMode": "auto",
          "colorMode": "value"
        }
      },
      {
        "id": 2,
        "title": "Memory Usage",
        "type": "stat",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}",
            "refId": "B"
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
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          }
        }
      },
      {
        "id": 3,
        "title": "Disk Usage",
        "type": "table",
        "targets": [
          {
            "expr": "(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100",
            "legendFormat": "{{instance}} - {{mountpoint}}",
            "refId": "C",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
        "transformations": [
          {
            "id": "organize",
            "options": {
              "excludeByName": {"Time": true},
              "indexByName": {},
              "renameByName": {
                "Value": "Usage %",
                "instance": "Instance",
                "mountpoint": "Mount Point"
              }
            }
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

### Network Traffic Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Network Traffic Monitor",
    "tags": ["network", "traffic", "monitoring"],
    "panels": [
      {
        "id": 1,
        "title": "Network In",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total[5m]) * 8",
            "legendFormat": "{{instance}} - {{device}} RX",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "bps",
            "color": {"mode": "palette-classic"}
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Network Out",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_transmit_bytes_total[5m]) * 8",
            "legendFormat": "{{instance}} - {{device}} TX",
            "refId": "B"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "bps",
            "color": {"mode": "palette-classic"}
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "15s"
  }
}
```

### Service Status Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Service Status Monitor",
    "tags": ["services", "status", "uptime"],
    "panels": [
      {
        "id": 1,
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"node-exporter\"}",
            "legendFormat": "{{instance}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {"options": {"text": "UP", "color": "green"}, "value": "1"},
              {"options": {"text": "DOWN", "color": "red"}, "value": "0"}
            ],
            "color": {"mode": "value"}
          }
        },
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "probe_duration_seconds",
            "legendFormat": "{{instance}}",
            "refId": "B"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "color": {"mode": "palette-classic"}
          }
        },
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
      }
    ],
    "variables": [
      {
        "name": "instance",
        "type": "query",
        "datasource": "Prometheus-Homelab",
        "query": "label_values(up, instance)",
        "multi": true,
        "includeAll": true
      }
    ]
  }
}
```

## 🔧 Advanced Features

### Dashboard Variables
```json
{
  "dashboard": {
    "variables": [
      {
        "name": "datasource",
        "type": "datasource",
        "datasource": null,
        "regex": "",
        "query": "prometheus",
        "refresh": 1,
        "current": {
          "selected": false,
          "text": "Prometheus-Homelab",
          "value": "prometheus-Homelab"
        }
      },
      {
        "name": "instance",
        "type": "query",
        "datasource": "$datasource",
        "query": "label_values(up, instance)",
        "refresh": 1,
        "sort": 1,
        "multi": true,
        "includeAll": true,
        "allValue": ".*"
      },
      {
        "name": "interval",
        "type": "interval",
        "datasource": null,
        "query": "1m,5m,10m,30m,1h,6h,12h,1d",
        "refresh": 0,
        "current": {
          "selected": false,
          "text": "5m",
          "value": "5m"
        }
      }
    ]
  }
}
```

### Annotations
```bash
# Create Annotation via API
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "dashboardId": 1,
    "panelId": null,
    "time": 1634567890000,
    "timeEnd": 1634571490000,
    "tags": ["deployment", "maintenance"],
    "text": "Application deployment completed successfully"
  }' \
  http://localhost:3000/api/annotations

# Annotation Query in Panels
{
  "targets": [
    {
      "expr": "rate(http_requests_total[5m])",
      "refId": "A"
    }
  ],
  "annotations": {
    "list": [
      {
        "datasource": "-- Grafana --",
        "enable": true,
        "name": "Deployments",
        "iconColor": "rgba(255, 96, 96, 1)",
        "type": "tags"
      }
    ]
  }
}
```

## 🚨 Alerting in Grafana

### Alert Rules
```json
{
  "dashboard": {
    "panels": [
      {
        "id": 1,
        "title": "CPU Alert",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "refId": "A"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {
                "params": [80],
                "type": "gt"
              },
              "operator": {
                "type": "and"
              },
              "query": {
                "params": ["A", "5m", "now"]
              },
              "reducer": {
                "params": [],
                "type": "last"
              },
              "type": "query"
            }
          ],
          "executionErrorState": "alerting",
          "for": "5m",
          "frequency": "60s",
          "handler": 1,
          "name": "CPU Usage High",
          "noDataState": "no_data",
          "notifications": []
        }
      }
    ]
  }
}
```

### Notification Channels
```bash
# Email Notification Channel
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "Email Alert",
    "type": "email",
    "settings": {
      "addresses": "admin@homelab.local",
      "subject": "Grafana Alert: [Alert Name]",
      "message": "Alert: [Alert Name]\n\nDetails: [Alert Details]\n\nView: [Dashboard URL]"
    },
    "secureSettings": {
      "password": "email-password"
    }
  }' \
  http://localhost:3000/api/alert-notifications

# Slack Notification Channel
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "Slack Alert",
    "type": "slack",
    "settings": {
      "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
      "channel": "#homelab-alerts",
      "username": "Grafana",
      "iconEmoji": ":robot_face:"
    }
  }' \
  http://localhost:3000/api/alert-notifications

# Webhook Notification Channel
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "Webhook Alert",
    "type": "webhook",
    "settings": {
      "url": "http://alertmanager:9093/api/v1/alerts",
      "httpMethod": "POST",
      "httpHeaderName1": "Authorization",
      "httpHeaderValue1": "Bearer token123"
    }
  }' \
  http://localhost:3000/api/alert-notifications
```

## 🔌 Plugin Management

### Plugin Installation
```bash
# Install via CLI
grafana-cli plugins install grafana-piechart-panel
grafana-cli plugins install grafana-worldmap-panel
grafana-cli plugins install grafana-simple-json-datasource

# Install from Community Repository
grafana-cli plugins install alexanderzobnin-zabbix-app

# List Installed Plugins
grafana-cli plugins ls

# Update Plugins
grafana-cli plugins update-all

# Remove Plugin
grafana-cli plugins remove grafana-piechart-panel

# Install Specific Version
grafana-cli plugins install grafana-clock-panel 1.2.0
```

### Popular Plugins
```bash
# Visualization Plugins
grafana-piechart-panel          # Pie charts
grafana-worldmap-panel          # World maps
grafana-clock-panel             # Clock displays
grafana-heatmap-panel           # Heat maps
grafana-statusmap-panel        # Status maps

# Data Source Plugins
grafana-simple-json-datasource  # Simple JSON API
grafana-influxdb-flux-datasource # InfluxDB Flux
grafana-azure-data-explorer     # Azure Monitor
grafana-snowflake-datasource    # Snowflake

# Application Plugins
alexanderzobnin-zabbix-app   # Zabbix integration
raintank-worldping-app        # WorldPing monitoring
grafana-kubernetes-app         # Kubernetes plugin
```

## 📊 Dashboard Provisioning

### Automated Dashboard Import
```yaml
# /etc/grafana/provisioning/dashboards/dashboard.yml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

### Dashboard JSON Files
```bash
# Download existing dashboard
curl -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  http://localhost:3000/api/dashboards/uid/YOUR-DASHBOARD-UID | jq '.dashboard' > dashboard.json

# Import dashboard via API
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "dashboard": '{"dashboard": {"title": "System Monitor"}, "overwrite": true}',
    "folderId": 0,
    "overwrite": true
  }' \
  http://localhost:3000/api/dashboards/db
```

## 🔧 Performance Optimization

### Configuration Tuning
```ini
# Performance settings in grafana.ini
[server]
# Enable gzip compression
enable_gzip = true
# HTTP timeout in seconds
http_addr = 0.0.0.0:3000

[database]
# Maximum number of open connections to the database
max_open_conn = 0
# Maximum number of idle connections to the database
max_idle_conn = 2
# Connection max lifetime
conn_max_lifetime = 14400

[session]
# Session provider type
provider = database
# Session duration
provider_config = session_life_time = 86400

[cache]
# Cache provider
provider = redis
# Redis configuration
provider_config = addr = localhost:6379
db = 0
password = redis123
```

### Database Optimization
```bash
# PostgreSQL Optimization for Grafana
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Connection Pooling
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'
```

## 🔒 Security Configuration

### Authentication Setup
```ini
# LDAP Authentication
[auth.ldap]
enabled = true
config_file = /etc/grafana/ldap.toml
allow_sign_up = true

# LDAP Configuration File
[[servers]]
host = "ldap.homelab.local"
port = 389
use_ssl = false
start_tls = false
ssl_skip_verify = false
bind_dn = "cn=admin,dc=homelab,dc=local"
bind_password = "ldap_password"
search_filter = "(|(uid=%s)(sAMAccountName=%s))"
search_base_dns = "dc=homelab,dc=local"

[servers.attributes]
member_of = "memberOf"
email = "mail"
name = "givenName"
surname = "sn"
username = "sAMAccountName"

# OAuth Authentication
[auth.generic_oauth]
enabled = true
name = OAuth
allow_sign_up = true
client_id = oauth_client_id
client_secret = oauth_client_secret
scopes = openid profile email
auth_url = https://oauth-provider.com/auth
token_url = https://oauth-provider.com/token
api_url = https://oauth-provider.com/userinfo
team_ids_attribute_path = teams
```

### Role-Based Access Control
```bash
# Create Organization
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "Production"
  }' \
  http://localhost:3000/api/orgs

# Create Team
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "name": "Developers",
    "email": "devs@homelab.local"
  }' \
  http://localhost:3000/api/teams

# Add User to Team
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "userId": 2
  }' \
  http://localhost:3000/api/teams/1/members
```

## 🚨 Troubleshooting

### Common Issues
```bash
# Grafana Not Starting
sudo journalctl -u grafana -f
sudo -u grafana grafana-server --config=/etc/grafana/grafana.ini --homepath=/usr/share/grafana

# Data Source Connection Issues
curl -v http://prometheus:9090/api/v1/query?query=up
curl -v http://influxdb:8086/ping
psql -h grafana-db -U grafana -d grafana -c "SELECT 1;"

# Dashboard Loading Issues
curl -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  http://localhost:3000/api/dashboards/uid/YOUR-DASHBOARD-UID

# Plugin Issues
grafana-cli plugins ls
sudo -u grafana grafana-cli plugins install --verbose grafana-piechart-panel
```

### Debug Configuration
```bash
# Enable Debug Mode
# Add to grafana.ini
[log]
level = debug

# Check Configuration
grafana-server --config=/etc/grafana/grafana.ini --homepath=/usr/share/grafana -test

# Database Migration Issues
sudo -u grafana grafana-cli admin migrate-database
```

## 📋 Backup and Recovery

### Grafana Backup
```bash
#!/bin/bash
# Grafana Backup Script

BACKUP_DIR="/backups/grafana"
DATE=$(date +%Y%m%d-%H%M%S)
GRAFANA_DATA="/var/lib/grafana"
GRAFANA_CONFIG="/etc/grafana"

mkdir -p "$BACKUP_DIR"

# Backup Database
if [ -f "$GRAFANA_DATA/grafana.db" ]; then
    cp "$GRAFANA_DATA/grafana.db" "$BACKUP_DIR/grafana.db-$DATE"
    echo "Database backed up: $BACKUP_DIR/grafana.db-$DATE"
fi

# Backup Configuration
tar czf "$BACKUP_DIR/grafana-config-$DATE.tar.gz" -C "$GRAFANA_CONFIG" .

# Backup Plugins
tar czf "$BACKUP_DIR/grafana-plugins-$DATE.tar.gz" -C "$GRAFANA_DATA" plugins/

# Backup Dashboards via API
curl -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  "http://localhost:3000/api/search?query=dashboard" | \
  jq '.[] | select(.type == "dash-db") | .uid' | \
  while read uid; do
    curl -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
      "http://localhost:3000/api/dashboards/uid/$uid" | \
      jq '.dashboard' > "$BACKUP_DIR/dashboard-$uid-$DATE.json"
  done

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "*" -mtime +7 -delete

echo "Grafana backup completed: $DATE"
```

### Restore Process
```bash
# Restore Database
sudo systemctl stop grafana
sudo -u grafana cp /backups/grafana/grafana.db-YYYYMMDDHHMMSS /var/lib/grafana/grafana.db

# Restore Configuration
sudo tar xzf /backups/grafana/grafana-config-YYYYMMDDHHMMSS.tar.gz -C /etc/grafana/

# Restart Grafana
sudo systemctl start grafana
```

## 📖 Further Reading

### Documentation
- [Grafana Documentation](https://grafana.com/docs/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [Plugin Development](https://grafana.com/docs/plugins/developing/)

### Communities
- Reddit: r/grafana, r/monitoring, r/homelab
- Grafana Community Forums
- Grafana Discord Server

### Advanced Topics
- Custom plugin development
- Grafana Enterprise features
- High availability setup
- Multi-tenant architecture

---


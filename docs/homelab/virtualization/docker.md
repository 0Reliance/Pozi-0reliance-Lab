---
title: Docker Containerization Setup
description: Complete guide for Docker installation, container management, and orchestration in homelab environments
---

# Docker Containerization Setup

Docker has revolutionized application deployment and management in homelab environments. This comprehensive guide covers Docker installation, container management, networking, storage, and orchestration best practices.

## 🐳 Docker Fundamentals

### Containerization Concepts
```bash
# Docker Architecture Overview

Docker Daemon (dockerd):
  Role: Background service managing containers
  Responsibilities: Image management, container lifecycle
  Communication: REST API, UNIX socket
  Management: systemd service

Docker Client (docker):
  Role: Command-line interface for Docker daemon
  Commands: build, run, push, pull, compose
  Authentication: UNIX socket or TCP

Docker Images:
  Role: Immutable templates for containers
  Layers: Read-only filesystem layers
  Storage: Docker Hub, private registries
  Formats: OCI compliant, layered architecture

Docker Containers:
  Role: Running instances of images
  Isolation: Process, filesystem, network, user
  Lifecycle: Create, start, stop, restart, remove
```

### Container vs Virtual Machines
```bash
# Container Advantages
Performance:
  - Native kernel execution (no hypervisor overhead)
  - Faster startup times (seconds vs minutes)
  - Lower resource overhead
  - Better density (more containers per host)

Portability:
  - Consistent environments across systems
  - "Build once, run anywhere"
  - Platform-agnostic images
  - Version-controlled configurations

Isolation:
  - Process-level isolation
  - Resource constraints
  - Network segmentation
  - Filesystem separation

# VM Advantages
Stronger Isolation:
  - Hardware-level virtualization
  - Separate kernel and drivers
  - Better security boundaries
  - Full OS flexibility

Established Tooling:
  - Mature management tools
  - Traditional backup methods
  - Legacy application support
  - Standard OS administration
```

## 🔧 Docker Installation

### System Preparation
```bash
# Docker System Requirements
Minimum:
  CPU: 64-bit processor
  RAM: 2GB+ (4GB+ recommended)
  Storage: 20GB+ (50GB+ recommended)
  OS: Ubuntu 20.04+, CentOS 8+, Debian 11+

Recommended Homelab:
  CPU: 4+ cores
  RAM: 8GB+ (16GB+ recommended)
  Storage: 100GB+ SSD
  Network: Gigabit Ethernet
  Optional: Dedicated storage pool

# Remove Old Versions
sudo apt remove -y docker docker-engine docker.io containerd runc
sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# Install Docker Dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

# Add Docker GPG Key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker Repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install Docker Engine (CentOS/RHEL)
sudo dnf install -y yum-utils
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Docker Configuration
```bash
# Add User to Docker Group
sudo usermod -aG docker $USER
newgrp docker

# Enable and Start Docker Service
sudo systemctl enable docker
sudo systemctl start docker

# Verify Installation
docker --version
docker compose version
docker run hello-world

# Configure Docker Daemon
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "registry-mirrors": [
    "https://mirror.gcr.io",
    "https://registry-1.docker.io"
  ]
}
EOF

# Restart Docker Service
sudo systemctl restart docker
```

## 🖥️ Container Management

### Basic Docker Commands
```bash
# Image Management
docker search ubuntu                    # Search images
docker pull ubuntu:22.04               # Pull image
docker images                           # List local images
docker rmi ubuntu:22.04               # Remove image
docker image prune                      # Remove unused images

# Container Lifecycle
docker run -it ubuntu:22.04 /bin/bash  # Run interactive container
docker run -d nginx                    # Run detached container
docker ps                              # List running containers
docker ps -a                           # List all containers
docker stop <container-id>              # Stop container
docker start <container-id>             # Start container
docker restart <container-id>           # Restart container
docker rm <container-id>                # Remove container

# Container Interaction
docker exec -it <container-id> /bin/bash  # Execute command in container
docker logs <container-id>                 # View container logs
docker stats <container-id>                # View container statistics
docker top <container-id>                 # View container processes
```

### Advanced Container Operations
```bash
# Container Naming and Labels
docker run -d --name web-server -l app=nginx -l environment=production nginx

# Resource Limits
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  --pids-limit=100 \
  --name limited-container \
  nginx

# Port Mapping and Networking
docker run -d \
  -p 8080:80 \
  -p 8443:443 \
  --name web-server \
  nginx

# Volume Mounting
docker run -d \
  -v /host/data:/container/data \
  -v /host/config:/container/config:ro \
  --name data-container \
  nginx

# Environment Variables
docker run -d \
  -e DATABASE_URL="postgresql://user:pass@db:5432/mydb" \
  -e DEBUG=true \
  --name app-container \
  myapp:latest
```

### Dockerfile Creation
```bash
# Multi-stage Dockerfile Example
# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production Stage
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Environment-specific Dockerfile
ARG BUILD_ENV=production
ENV NODE_ENV=${BUILD_ENV}
ENV PORT=3000

# Security Hardening
FROM alpine:3.18
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser
WORKDIR /app
COPY --chown=appuser:appgroup . .
CMD ["./app"]
```

## 🌐 Docker Networking

### Network Types
```bash
# Bridge Network (Default)
docker network create app-network
docker run -d --network app-network --name web-app nginx
docker run -d --network app-network --name db-app postgres

# Host Network
docker run -d --network host --name host-network-app nginx

# None Network (No network access)
docker run -d --network none --name isolated-app myapp

# Overlay Network (Multi-host)
docker network create --driver overlay --attachable multi-host-network

# Macvlan Network (Direct host connectivity)
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  macvlan-network
```

### Network Configuration
```bash
# Custom Bridge Network
docker network create \
  --driver bridge \
  --subnet=172.20.0.0/16 \
  --gateway=172.20.0.1 \
  --ip-range=172.20.1.0/24 \
  homelab-network

# Container with Static IP
docker run -d \
  --network homelab-network \
  --ip 172.20.1.100 \
  --name static-ip-container \
  nginx

# Network Aliases
docker network connect \
  --alias database \
  --alias postgres \
  homelab-network \
  postgres-container

# Network Isolation
docker network create --internal isolated-network
docker run -d --network isolated-network isolated-app
```

## 💾 Docker Storage

### Volume Management
```bash
# Named Volumes (Recommended)
docker volume create app-data
docker volume create logs-volume --opt type=tmpfs --opt device=tmpfs --opt o=size=100m

# Volume Usage
docker run -d \
  -v app-data:/app/data \
  -v logs-volume:/app/logs \
  --name volume-container \
  myapp

# Volume Management
docker volume ls                              # List volumes
docker volume inspect app-data                  # Volume details
docker volume create --label environment=prod prod-data
docker volume prune                           # Remove unused volumes

# Bind Mounts (Development)
docker run -d \
  -v /home/user/project:/app \
  -v /home/user/config:/app/config:ro \
  --name dev-container \
  myapp
```

### Storage Drivers
```bash
# Check Storage Driver
docker info | grep "Storage Driver"

# Recommended Storage Drivers:
# - overlay2: Default, best performance
# - btrfs: Good for data-heavy workloads
# - zfs: Excellent data integrity
# - devicemapper: Good for production

# Configure Storage Driver
# Edit /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}

# Storage Optimization
# Use tmpfs for temporary data
docker run -d \
  --tmpfs /tmp:rw,size=100m \
  --tmpfs /var/log:rw,size=50m \
  --name tmpfs-container \
  myapp
```

## 🔄 Docker Compose

### Docker Compose Installation
```bash
# Docker Compose Plugin (Recommended)
# Already included with Docker Desktop and recent Docker installations
docker compose version

# Alternative: Standalone Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Docker Compose Configuration
```yaml
# docker-compose.yml Example
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - web-data:/usr/share/nginx/html
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - frontend
      - backend

  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - app-data:/app/data
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    restart: unless-stopped
    networks:
      - backend

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - backend

volumes:
  web-data:
    driver: local
  app-data:
    driver: local
  db-data:
    driver: local
  redis-data:
    driver: local

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

### Docker Compose Commands
```bash
# Service Management
docker compose up -d                    # Start all services
docker compose down                      # Stop and remove containers
docker compose up -d --build            # Rebuild and start
docker compose restart                  # Restart all services
docker compose stop                     # Stop all services
docker compose start                    # Start stopped services

# Service Management (Individual)
docker compose up -d web               # Start specific service
docker compose restart app              # Restart specific service
docker compose stop db                  # Stop specific service

# Scale Services
docker compose up -d --scale app=3     # Run multiple instances
docker compose up -d --scale web=2

# Logs and Monitoring
docker compose logs -f                  # Follow all logs
docker compose logs -f web             # Follow specific service logs
docker compose ps                      # List services and status
docker compose top                      # Show running processes
docker compose exec app bash           # Execute command in service

# Maintenance
docker compose pull                    # Pull latest images
docker compose build                    # Build images
docker compose rm                      # Remove stopped containers
docker compose down -v                 # Remove containers and volumes
```

## 🚀 Production Best Practices

### Security Hardening
```bash
# Rootless Docker
# Install as non-root user
curl -fsSL https://get.docker.com/rootless | sh
export DOCKER_HOST=unix:///run/user/1001/docker.sock
systemctl --user start docker

# Security Scanner
docker scan myapp:latest
docker scan --severity high myapp:latest

# Content Trust
export DOCKER_CONTENT_TRUST=1
docker pull trusted-registry/ubuntu:22.04

# Secure Base Images
# Use specific versions instead of latest
FROM node:18.17.0-alpine AS builder
FROM nginx:1.25.1-alpine AS production

# Multi-stage builds reduce attack surface
FROM node:18-alpine AS builder
# ... build process
FROM scratch AS production
COPY --from=builder /app .
CMD ["./app"]

# Non-root user
FROM alpine:3.18
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser
```

### Performance Optimization
```bash
# Resource Limits
docker run -d \
  --memory="2g" \
  --cpus="2.0" \
  --cpuset-cpus="0,1" \
  --memory-reservation="1g" \
  --cpu-shares=512 \
  optimized-container

# Health Checks
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Logging Configuration
docker run -d \
  --log-driver json-file \
  --log-opt max-size="10m" \
  --log-opt max-file="3" \
  production-container

# Cleanup Automation
# Set up cron job for cleanup
0 2 * * * docker system prune -f --volumes
0 3 * * 0 docker image prune -f -a
```

### Backup and Recovery
```bash
# Container Backup
docker export <container-id> | gzip > container-backup.tar.gz

# Image Backup
docker save -o image-backup.tar myapp:latest
gzip image-backup.tar

# Volume Backup
docker run --rm -v my-volume:/data -v $(pwd):/backup alpine tar czf /backup/volume-backup.tar.gz /data

# Automated Backup Script
#!/bin/bash
BACKUP_DIR="/backups/docker"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup images
docker save -o "$BACKUP_DIR/images-$DATE.tar" $(docker images -q)
gzip "$BACKUP_DIR/images-$DATE.tar"

# Backup volumes
docker volume ls --format "{{.Name}}" | while read volume; do
    docker run --rm -v "$volume":/data -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/volume-$volume-$DATE.tar.gz" /data
done

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

## 📊 Monitoring and Logging

### Container Monitoring
```bash
# Docker Stats
docker stats                              # Live resource usage
docker stats --no-stream                  # Single snapshot
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" web-app

# System Information
docker system df                          # Disk usage
docker system events                       # System events
docker system prune                        # Clean up unused resources

# Container Inspection
docker inspect web-app                    # Full container details
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-app
docker inspect --format='{{.State.Health}}' web-app
```

### Centralized Logging
```yaml
# docker-compose.yml with logging
version: '3.8'

services:
  app:
    image: myapp:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "environment=production,service=app"

  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
    volumes:
      - es-data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.8.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  es-data:
```

## 🔧 Advanced Features

### Docker Swarm Mode
```bash
# Initialize Swarm
docker swarm init --advertise-addr <MANAGER-IP>

# Join Worker Nodes
docker swarm join --token <TOKEN> <MANAGER-IP>:2377

# Create Service
docker service create \
  --name web-service \
  --replicas 3 \
  --publish 80:80 \
  nginx

# Scale Service
docker service scale web-service=5

# Rolling Update
docker service update \
  --image nginx:1.25 \
  --update-parallelism 1 \
  --update-delay 10s \
  web-service

# Service Management
docker service ls
docker service ps web-service
docker service logs web-service
```

### Docker Registry
```bash
# Local Registry
docker run -d \
  -p 5000:5000 \
  --name local-registry \
  -v registry-data:/var/lib/registry \
  registry:2

# Secure Registry with TLS
docker run -d \
  -p 5000:5000 \
  --name secure-registry \
  -v /path/to/certs:/certs \
  -v registry-data:/var/lib/registry \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  registry:2

# Push to Registry
docker tag myapp:latest localhost:5000/myapp:latest
docker push localhost:5000/myapp:latest
```

### Multi-arch Builds
```bash
# Docker Buildx for Multi-arch
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# Multi-arch Build
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag myorg/myapp:latest \
  --push \
  .

# Cross-compilation
docker buildx build \
  --platform linux/arm64 \
  --tag myorg/myapp:arm64 \
  --load \
  .
```

## 🚨 Troubleshooting

### Common Issues
```bash
# Container Won't Start
docker logs <container-id>                # Check logs
docker inspect <container-id>              # Check configuration
docker run --rm -it --entrypoint /bin/sh <image> # Debug container

# Network Issues
docker network ls                          # List networks
docker network inspect <network-name>       # Network details
docker exec <container-id> ip addr          # Container networking

# Storage Issues
docker system df                            # Disk usage
docker volume ls                           # List volumes
docker volume inspect <volume-name>          # Volume details

# Permission Issues
docker run --user 1000:1000 myapp         # Run as specific user
docker run --userns=host myapp             # Use host user namespace
```

### Debug Commands
```bash
# Container Debugging
docker run -it --rm --network container:<container-id> nicolaka/netshoot
docker run -it --rm --pid container:<container-id> alpine
docker run -it --rm --volumes-from <container-id> alpine

# System Debugging
docker info                              # System information
docker version                            # Version information
docker system events                       # System events
docker context ls                         # Context information

# Performance Debugging
docker exec <container-id> top             # Container processes
docker stats --no-stream <container-id>    # Resource usage
docker exec <container-id> df -h          # Disk usage
```

## 📖 Further Reading

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Communities
- Reddit: r/docker, r/selfhosted, r/homelab
- Docker Forums
- Docker Discord Community

### Advanced Topics
- Kubernetes Orchestration
- CI/CD Integration
- GitOps with Docker
- Container Security Scanning

---

**Ready to dive deeper?** Check our [Virtualization](index.md) overview for comprehensive virtualization planning!

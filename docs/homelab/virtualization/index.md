---
title: Virtualization
description: Complete virtualization setup guides for homelab environments
---

# Virtualization

Virtualization is the backbone of modern homelabs, allowing you to run multiple isolated environments on a single physical machine. This section covers Proxmox, Docker, Kubernetes, and VM management.

## 🖥️ Virtualization Technologies

### Type 1 Hypervisors (Bare Metal)
```bash
Proxmox VE    # KVM-based, user-friendly
ESXi           # VMware enterprise
XCP-ng         # XEN-based, free
Hyper-V        # Windows Server
```

### Type 2 Hypervisors (Hosted)
```bash
VirtualBox     # Development, testing
KVM/QEMU       # Linux native
VMware Workstation # Commercial, feature-rich
```

### Container Platforms
```bash
Docker         # Most popular, app-focused
Podman         # Rootless, daemonless
LXD/LXC        # System containers
```

### Container Orchestration
```bash
Kubernetes     # Industry standard
Docker Swarm   # Simple, Docker-native
Nomad          # HashiCorp alternative
```

## 📚 Virtualization Documentation

### [Proxmox Setup](proxmox.md)
- Installation and configuration
- VM creation and management
- Storage integration
- Cluster setup

### [Docker Containers](docker.md)
- Container best practices
- Docker Compose
- Networking and storage
- Production deployment

### [Kubernetes Cluster](kubernetes.md)
- Multi-node cluster setup
- Application deployment
- Monitoring and logging
- Service mesh integration

## 🏗️ Choosing Your Platform

### Proxmox VE - Recommended for Homelabs

**Advantages:**
- Web-based management interface
- Built-in KVM and LXC support
- ZFS integration
- Live migration
- Backup integration
- Free and open-source

**Hardware Requirements:**
```bash
Minimum:
- CPU: 64-bit with Intel VT-x/AMD-V
- RAM: 4GB+ (8GB+ recommended)
- Storage: 32GB+ SSD
- Network: Gigabit ethernet

Recommended:
- CPU: 6+ cores with virtualization
- RAM: 16GB+ (32GB+ for many VMs)
- Storage: 500GB+ SSD + HDD array
- Network: 2+ Gigabit ports
```

### Docker - Application Containerization

**Best For:**
- Application deployment
- Microservices
- Development environments
- Stateless services

**Use Cases:**
```bash
Web Services:      Nginx, Apache, Node.js
Databases:         PostgreSQL, MySQL, Redis
Media:             Plex, Jellyfin, Emby
Monitoring:        Grafana, Prometheus, InfluxDB
Development:       GitLab, Jenkins, SonarQube
```

### Kubernetes - Container Orchestration

**Best For:**
- Production workloads
- High availability
- Auto-scaling
- Service discovery

**Complexity Level:**
- **Beginner**: Docker Swarm
- **Intermediate**: Single-node K8s
- **Advanced**: Multi-node K8s cluster

## 🛠️ Resource Planning

### CPU Allocation

#### Virtual Machine CPU Planning
```bash
General Purpose VM: 2 vCPU
Database Server:     4-8 vCPU
Web Server:         2-4 vCPU
Development VM:     2-4 vCPU
Media Server:       2-4 vCPU + GPU passthrough
```

#### Container CPU Planning
```bash
Small service:      0.1-0.5 vCPU
Web application:    0.5-2 vCPU
Database:           1-4 vCPU
Media processing:   2+ vCPU
```

### Memory Planning

#### VM Memory Allocation
```bash
Lightweight Linux:   512MB - 1GB
Desktop Linux:      2GB - 4GB
Windows Server:     4GB - 8GB
Database Server:    8GB - 16GB
Development VM:     4GB - 8GB
```

#### Container Memory Limits
```bash
Microservice:       64MB - 256MB
Web app:           256MB - 1GB
Database:          1GB - 4GB
Cache service:      256MB - 512MB
```

### Storage Planning

#### VM Storage Requirements
```bash
OS Disk:           20GB - 50GB
Application:       50GB - 200GB
Database:          100GB - 500GB
Backup storage:    2x - 3x primary size
```

#### Container Storage
```bash
Application data:  10GB - 100GB
Database:          50GB - 500GB
Media files:       100GB - 1TB+
Logs:              5GB - 50GB (rotating)
```

## 🔧 Setup Examples

### Proxmox Installation
```bash
# 1. Download Proxmox ISO
# 2. Create bootable USB
# 3. Install on target hardware
# 4. Configure network interfaces
# 5. Set up storage (ZFS recommended)

# Post-installation configuration
# Add enterprise repository (optional)
echo "deb https://enterprise.proxmox.com/debian/pve bullseye pve-enterprise" > /etc/apt/sources.list.d/pve-enterprise.list

# Update system
apt update && apt dist-upgrade -y

# Install useful packages
apt install -y htop iftop iotop nethogs
```

### Docker Setup on Ubuntu
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker $USER

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Test installation
docker run hello-world
docker-compose --version
```

### Single-Node Kubernetes (k3s)
```bash
# Install k3s (lightweight Kubernetes)
curl -sfL https://get.k3s.io | sh -

# Get kubeconfig
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Test cluster
kubectl get nodes
kubectl get pods --all-namespaces
```

## 📊 Performance Optimization

### Storage Performance

#### ZFS for Proxmox
```bash
# Create ZFS pool for VMs
zpool create -f -o ashift=12 rpool mirror /dev/nvme0n1 /dev/nvme1n1

# Create datasets
zfs create -o compression=lz4 rpool/vms
zfs create -o compression=lz4 rpool/containers
zfs create -o compression=off rpool/images

# Enable features
zfs set atime=off rpool/vms
zfs set recordsize=1M rpool/vms
```

#### Docker Storage Optimization
```bash
# Use SSD for Docker
sudo systemctl stop docker
sudo mv /var/lib/docker /mnt/ssd/docker
sudo ln -s /mnt/ssd/docker /var/lib/docker
sudo systemctl start docker

# Configure log rotation
echo '{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}' | sudo tee /etc/docker/daemon.json
```

### Network Optimization

#### VM Network Configuration
```bash
# Create network bridges in Proxmox
# Bridge (vmbr0) - WAN connectivity
# Bridge (vmbr1) - Internal network
# Bridge (vmbr2) - Storage network

# Enable SR-IOV for network cards (if supported)
echo "options vfio-pci ids=10ec:8168" >> /etc/modprobe.d/vfio.conf
update-initramfs -u -k all
```

#### Container Networking
```yaml
# Docker Compose with custom network
version: '3.8'
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/24

services:
  web:
    networks:
      - frontend
    ports:
      - "80:80"
  
  database:
    networks:
      - backend
    ports: []  # No external access
```

### CPU and Memory Tuning

#### VM Performance Tuning
```bash
# Enable CPU pinning for critical VMs
# Set VM BIOS to OVMF (UEFI)
# Enable virtio drivers
# Use SSD cache for storage
# Configure huge pages

# Enable huge pages
echo 1024 > /proc/sys/vm/nr_hugepages
echo 'vm.nr_hugepages=1024' >> /etc/sysctl.conf
```

#### Container Resource Limits
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    environment:
      - MALLOC_ARENA_MAX=2
```

## 📈 Monitoring and Management

### Proxmox Monitoring
```bash
# Install monitoring tools
apt install -y proxmox-backup-client zabbix-agent

# Configure ZFS monitoring
zpool status
zfs list
iostat -x 1

# VM performance monitoring
qm list
pct list
```

### Docker Monitoring
```bash
# Monitor container resources
docker stats
docker system df
docker system events

# Log monitoring
docker logs -f container-name
docker-compose logs -f
```

### Kubernetes Monitoring
```bash
# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Monitor cluster resources
kubectl top nodes
kubectl top pods --all-namespaces

# Check cluster health
kubectl get componentstatuses
kubectl cluster-info
```

## 🔍 Common Issues and Solutions

### Performance Problems

#### VM Slow Performance
```bash
# Check for I/O bottlenecks
iotop
iostat -x 1

# Verify virtio drivers
lspci | grep -i virtio

# Check CPU scheduling
cat /proc/interrupts
```

#### Container Resource Issues
```bash
# Check resource limits
docker inspect container-name | grep -A 10 "Resources"

# Monitor resource usage
docker stats --no-stream

# Clean up unused resources
docker system prune -a
```

### Storage Issues

#### Running Out of Space
```bash
# Check disk usage
df -h
du -sh /var/lib/*

# Clean up old images
docker image prune -a
docker container prune

# Clean VM disks
qm cleanup <vmid> --disk
```

### Network Problems

#### Container Networking Issues
```bash
# Check network configuration
docker network ls
docker network inspect bridge

# Restart networking
docker network prune
systemctl restart docker
```

#### VM Network Issues
```bash
# Check bridge configuration
brctl show
ip addr show

# Restart network services
systemctl restart networking
```

## 📋 Best Practices

### Security
- [ ] Regular updates and patches
- [ ] Network segmentation
- [ ] Resource limits
- [ ] Image scanning for containers
- [ ] Access control and RBAC

### Performance
- [ ] Monitor resource usage
- [ ] Optimize storage I/O
- [ ] Use appropriate drivers
- [ ] Configure networking properly
- [ ] Regular maintenance

### Backup and Recovery
- [ ] Automated backups
- [ ] Test restore procedures
- [ ] Offsite backup storage
- [ ] Documentation
- [ ] Disaster recovery plan

### Management
- [ ] Configuration as code
- [ ] Version control
- [ ] Monitoring and alerting
- [ ] Log management
- [ ] Documentation

---

**Ready to virtualize?** Start with our [Proxmox Setup](proxmox.md) guide for enterprise-grade virtualization!

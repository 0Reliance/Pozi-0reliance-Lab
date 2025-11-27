# Homelab Documentation Hub - Installation Guide

## Overview

The Homelab Documentation Hub is a comprehensive platform for managing homelab documentation with AI-powered features. This guide provides step-by-step installation instructions for various deployment scenarios.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.0GHz+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 10GB free space
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+), macOS (10.15+), Windows 10+
- **Docker**: 20.10+ (if using Docker deployment)
- **Python**: 3.8+ (if using local deployment)

### Recommended Requirements
- **CPU**: 4 cores, 3.0GHz+
- **RAM**: 8GB (16GB for production)
- **Storage**: 20GB+ SSD
- **Network**: Stable internet connection for AI features

## Installation Methods

### Method 1: Automated Setup (Recommended)

#### Prerequisites
1. Install Docker and Docker Compose
2. Install Git
3. Ensure ports 80, 8000, 8001 are available

#### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd homelab-docs

# 2. Run automated setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# The setup script will:
# - Validate system requirements
# - Check and validate environment variables
# - Set up directory structure
# - Generate SSL certificates (self-signed for development)
# - Build Docker images
# - Deploy all services
# - Configure automated backups
# - Perform health checks
```

#### What the Setup Script Does

The automated setup script (`scripts/setup.sh`) performs comprehensive deployment:

1. **System Requirements Check**
   - Verifies Docker and Docker Compose installation
   - Checks available memory (minimum 2GB recommended)
   - Validates disk space (minimum 5GB required)
   - Warns about potential performance limitations

2. **Environment Validation**
   - Creates `.env` from `.env.example` if needed
   - Validates required environment variables (OPENAI_API_KEY, SECRET_KEY)
   - Checks OpenAI API key format
   - Verifies secret key length and complexity

3. **Directory Structure Setup**
   - Creates necessary directories: `logs/`, `backups/`, `uploads/`, `data/`, `ssl/`
   - Sets appropriate permissions for security

4. **SSL Certificate Generation**
   - Generates self-signed certificates for development
   - Warns about using proper certificates for production

5. **Docker Image Building**
   - Builds MkDocs and AI backend images
   - Handles build errors gracefully

6. **Service Deployment**
   - Starts all services using Docker Compose
   - Performs health checks on each service
   - Waits for services to be ready

7. **Backup Automation**
   - Configures automated daily backups via cron
   - Sets up backup retention policies

### Method 2: Manual Docker Compose

#### Prerequisites
1. Install Docker and Docker Compose
2. Install Git
3. Ensure ports 80, 8000, 8001 are available

#### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd homelab-docs

# 2. Copy environment configuration
cp .env.example .env

# 3. Edit environment variables (see Configuration section)
nano .env

# 4. Build and start services
docker-compose -f docker/docker-compose.yml up --build -d

# 5. Verify installation
docker-compose -f docker/docker-compose.yml ps
```

#### Environment Configuration
Edit `.env` file with your settings:

```bash
# OpenAI API Key (required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Git Repository (optional, for git integration)
GIT_REPO_URL=https://github.com/your-username/docs-repo.git

# Secret Key for sessions
SECRET_KEY=change-this-to-a-secure-random-string

# Domain (optional, for SSL setup)
DOMAIN=localhost

# Email (optional, for notifications)
ADMIN_EMAIL=admin@example.com
```

#### Verification
```bash
# Check if all services are running
curl http://localhost
curl http://localhost:8001/health
curl http://localhost/api/docs

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Method 2: Local Development

#### Prerequisites
1. Python 3.8+
2. Node.js 16+ (optional, for frontend development)
3. Git
4. Virtual environment (recommended)

#### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd Pozi-0reliance-Lab

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install MkDocs dependencies
pip install -r requirements.txt

# 4. Install AI backend dependencies
cd ai-backend
pip install -r requirements.txt
cd ..

# 5. Start MkDocs server
mkdocs serve --dev-addr=0.0.0.0:8000 &

# 6. Start AI backend
cd ai-backend
python main.py &
```

#### Local Development Verification
```bash
# MkDocs: http://localhost:8000
# AI Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Method 3: Production Deployment

#### Using Docker with SSL

```bash
# 1. Generate SSL certificates
mkdir -p docker/ssl
cd docker/ssl

# Self-signed certificate (for development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem -out fullchain.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Or use Let's Encrypt (for production)
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem .
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem .
cd ..

# 2. Update environment variables
echo "DOMAIN=yourdomain.com" >> .env
echo "SSL_CERT_PATH=docker/ssl/fullchain.pem" >> .env
echo "SSL_KEY_PATH=docker/ssl/privkey.pem" >> .env

# 3. Deploy with Docker Compose
docker-compose -f docker/docker-compose.yml up --build -d
```

#### Production Environment Variables
```bash
# Production settings
OPENAI_API_KEY=your_production_api_key
SECRET_KEY=your_very_secure_secret_key_here
DOMAIN=yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
SSL_CERT_PATH=/path/to/ssl/cert.pem
SSL_KEY_PATH=/path/to/ssl/privkey.pem

# Security settings
REQUIRE_AUTH=true
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
LOG_LEVEL=INFO
```

## Configuration Options

### AI Features Configuration

#### OpenAI Setup
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to environment: `OPENAI_API_KEY=sk-...`
3. Test AI features in admin panel

#### Alternative AI Providers
```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Hugging Face
HUGGINGFACE_API_KEY=your_huggingface_key

# Custom API
CUSTOM_API_URL=https://your-api-endpoint.com
CUSTOM_API_KEY=your_custom_api_key
```

### Security Configuration

#### Authentication
```bash
# Enable authentication
REQUIRE_AUTH=true

# Create admin user
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here

# JWT settings
JWT_SECRET_KEY=your_jwt_secret_here
JWT_EXPIRE_HOURS=24
```

#### SSL/TLS Configuration
```bash
# Force HTTPS
FORCE_HTTPS=true

# SSL Configuration
SSL_CERT_PATH=/path/to/certificate.pem
SSL_KEY_PATH=/path/to/private.key

# HSTS Security Header
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=true
```

### Database Configuration

#### Redis Settings
```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password

# Session storage
SESSION_TYPE=redis
SESSION_REDIS_URL=redis://localhost:6379/1
```

#### File Storage
```bash
# Upload settings
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.txt,.md,.pdf,.doc,.docx

# Storage type
STORAGE_TYPE=local
# STORAGE_TYPE=s3  # For AWS S3
# STORAGE_TYPE=google-cloud  # For Google Cloud
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER

# Install Node.js (for development)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Clone and run
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd Pozi-0reliance-Lab
docker-compose -f docker/docker-compose.yml up --build -d
```

### macOS

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker
brew install --cask docker

# Install Python
brew install python3

# Clone and run
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd Pozi-0reliance-Lab
docker-compose -f docker/docker-compose.yml up --build -d
```

### Windows

```bash
# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop/

# Install Git for Windows
# Download from https://git-scm.com/download/win

# Install Python
# Download from https://www.python.org/downloads/windows/

# Clone and run (using PowerShell or Git Bash)
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd Pozi-0reliance-Lab
docker-compose -f docker/docker-compose.yml up --build -d
```

## Networking Configuration

### Port Mapping

| Service  | Port | Protocol | Description |
|-----------|------|----------|-------------|
| Nginx     | 80   | HTTP     | Main web interface |
| Nginx     | 443  | HTTPS    | Secure web interface |
| MkDocs     | 8000 | HTTP     | Documentation server |
| AI Backend | 8001 | HTTP     | API and AI services |
| Redis      | 6379 | TCP      | Caching and sessions |

### Firewall Configuration

```bash
# Linux (ufw)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
sudo ufw allow 6379/tcp

# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8001 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 6379 -j ACCEPT

# Windows Firewall
# Allow ports through Windows Defender Firewall settings
```

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Check Docker status
sudo systemctl status docker

# Check Docker logs
docker logs homelab-docs-mkdocs
docker logs homelab-docs-ai-backend
docker logs homelab-docs-nginx

# Reset Docker
docker-compose -f docker/docker-compose.yml down
docker system prune -f
docker-compose -f docker/docker-compose.yml up --build
```

#### Permission Issues
```bash
# Fix Docker permissions
sudo chown -R $USER:$USER ./docker
sudo chmod -R 755 ./docker

# Fix file permissions
chmod +x scripts/*.sh
```

#### Memory Issues
```bash
# Check system resources
free -h
df -h

# Increase swap space (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Network Issues
```bash
# Check port availability
netstat -tuln | grep -E ':(80|443|8000|8001|6379)'

# Test connectivity
curl -I http://localhost
curl -I http://localhost:8000
curl -I http://localhost:8001
```

### Logging and Debugging

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# View detailed logs
docker-compose -f docker/docker-compose.yml logs -f --tail=100

# Check service health
curl http://localhost:8001/health
curl http://localhost:8001/api/health
```

## Performance Optimization

### Docker Optimization

```yaml
# docker-compose.yml performance settings
services:
  mkdocs:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
  
  ai-backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Caching Configuration

```bash
# Redis caching
REDIS_URL=redis://localhost:6379/1

# Browser caching (in nginx.conf)
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Database Optimization

```bash
# Redis memory optimization
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_POOL_MAX_OVERFLOW=30
```

## Backup and Recovery

### Automated Backup System

The Homelab Documentation Hub includes a comprehensive automated backup system that handles:

- **Docker Volumes**: All application data and uploads
- **Configuration Files**: Environment variables, Docker configs, scripts
- **Documentation**: All markdown files and content
- **SSL Certificates**: Security certificates for HTTPS
- **Metadata**: Backup manifests and integrity reports

#### Backup Script Features

The included `scripts/backup.sh` script provides:

```bash
# Daily backup (default retention: 30 days)
./scripts/backup.sh daily

# Weekly backup (default retention: 90 days)
./scripts/backup.sh weekly

# Monthly backup (default retention: 365 days)
./scripts/backup.sh monthly

# List available backups
./scripts/backup.sh list [daily|weekly|monthly]

# Restore from backup
./scripts/backup.sh restore 20240101_120000 [daily|weekly|monthly]

# Show help
./scripts/backup.sh help
```

#### Backup Contents

Each backup includes:
- `config.tar.gz` - Configuration files (.env, docker/, scripts/)
- `docs.tar.gz` - Documentation content
- `uploads.tar.gz` - User uploads and files
- `ssl.tar.gz` - SSL certificates
- `volume_*.tar.gz` - Docker volumes (ai_uploads, redis_data, etc.)
- `manifest.json` - Backup metadata and system info
- `backup_report.txt` - Detailed backup report
- `file_list.txt` - Complete file inventory

#### Backup Automation Setup

The setup script automatically configures backup automation:

```bash
# Manual setup (if not using automated setup)
# Add to crontab for daily backups at 2 AM
crontab -e

# Add this line:
0 2 * * * cd /path/to/homelab-docs && ./scripts/backup.sh daily >> logs/backup.log 2>&1

# Weekly backup (Sundays at 3 AM)
0 3 * * 0 cd /path/to/homelab-docs && ./scripts/backup.sh weekly >> logs/backup.log 2>&1

# Monthly backup (1st of month at 4 AM)
0 4 1 * * cd /path/to/homelab-docs && ./scripts/backup.sh monthly >> logs/backup.log 2>&1
```

#### Backup Verification and Integrity

All backups include automatic verification:

```bash
# Manual backup verification
./scripts/backup.sh verify /path/to/backup

# Check backup integrity
tar -tzf backups/daily/20240101_120000/config.tar.gz >/dev/null 2>&1
echo $?

# View backup report
cat backups/daily/20240101_120000/backup_report.txt

# Check backup manifest
cat backups/daily/20240101_120000/manifest.json
```

#### Recovery Procedures

##### Full System Recovery

```bash
# List available backups to restore from
./scripts/backup.sh list daily

# Restore from specific backup (interactive)
./scripts/backup.sh restore 20240101_120000 daily

# The restore process will:
# 1. Verify backup integrity
# 2. Stop all services
# 3. Restore configuration files
# 4. Restore documentation
# 5. Restore uploads
# 6. Restore Docker volumes
# 7. Restart services
# 8. Verify system health
```

##### Manual Recovery Steps

```bash
# 1. Stop services
cd docker
docker-compose down

# 2. Restore configuration
tar -xzf backups/daily/20240101_120000/config.tar.gz -C ../

# 3. Restore documentation
tar -xzf backups/daily/20240101_120000/docs.tar.gz -C ../

# 4. Restore uploads
tar -xzf backups/daily/20240101_120000/uploads.tar.gz -C ../

# 5. Restore Docker volumes
docker run --rm -v homelab-docs_ai_uploads:/data \
    -v $(pwd)/../backups/daily/20240101_120000:/backup:ro \
    alpine tar xzf /backup/volume_homelab-docs_ai_uploads.tar.gz -C /data

docker run --rm -v homelab-docs_redis_data:/data \
    -v $(pwd)/../backups/daily/20240101_120000:/backup:ro \
    alpine tar xzf /backup/volume_homelab-docs_redis_data.tar.gz -C /data

# 6. Restart services
docker-compose up -d

# 7. Verify recovery
curl http://localhost:8001/health
```

#### Backup Configuration

Customize backup behavior with environment variables:

```bash
# Backup location
BACKUP_DIR=/custom/backup/path

# Retention periods
DAILY_RETENTION=30      # days
WEEKLY_RETENTION=90     # days
MONTHLY_RETENTION=365   # days

# Compression settings
COMPRESSION_LEVEL=6       # 1-9, 6 is default

# Logging
BACKUP_LOG_FILE=/var/log/homelab-backup.log
```

#### Offsite Backup Integration

Configure offsite backups with cloud storage:

```bash
# Add to backup script for cloud sync
# Example: AWS S3
aws s3 sync backups/ s3://your-backup-bucket/homelab-docs/

# Example: Google Cloud Storage
gsutil -m rsync -r backups/ gs://your-backup-bucket/homelab-docs/

# Example: rsync to remote server
rsync -avz --delete backups/ user@backup-server:/backups/homelab-docs/
```

#### Disaster Recovery Planning

##### Emergency Response Checklist

1. **Assess Situation**
   ```bash
   # Check service status
   docker-compose ps
   
   # Check system health
   ./scripts/backup.sh health-check
   
   # Identify affected services
   curl http://localhost:8001/health
   ```

2. **Initiate Recovery**
   ```bash
   # Stop all services
   docker-compose down
   
   # Choose appropriate backup
   ./scripts/backup.sh list daily
   ```

3. **Execute Recovery**
   ```bash
   # Perform full restore
   ./scripts/backup.sh restore [backup_timestamp] daily
   
   # Verify services
   docker-compose ps
   curl http://localhost:8001/health
   ```

4. **Post-Recovery Validation**
   ```bash
   # Test documentation access
   curl http://localhost
   
   # Test AI functionality
   curl http://localhost:8001/api/generate -X POST
   
   # Check data integrity
   ./scripts/backup.sh verify-current
   ```

#### Backup Monitoring and Alerts

Monitor backup operations:

```bash
# Check backup logs
tail -f logs/backup.log

# Monitor backup directory size
du -sh backups/

# Check last backup status
./scripts/backup.sh status

# Email notification setup (example)
echo "Backup completed: $(date)" | mail -s "Homelab Docs Backup" admin@example.com
```

#### Performance Considerations

- **Backup Schedule**: During low-traffic hours (2-4 AM)
- **Storage Requirements**: ~2-5GB per full backup
- **Network Bandwidth**: Consider for offsite backups
- **Compression**: Level 6 balances speed and size
- **Retention**: Adjust based on storage capacity and compliance

#### Security Best Practices

- **Encryption**: Backup storage should be encrypted
- **Access Control**: Restrict backup file permissions
- **Offsite Storage**: Store backups in separate location
- **Testing**: Regularly test restore procedures
- **Audit**: Log all backup and restore operations

```bash
# Secure backup permissions
chmod 700 backups/
chmod 600 backups/*/*

# Backup encryption example
gpg --symmetric --cipher-algo AES256 backups/daily/20240101_120000.tar.gz
```

## Monitoring and Maintenance

### Health Checks

```bash
# Service health monitoring script
#!/bin/bash
SERVICES=("nginx:80" "mkdocs:8000" "ai-backend:8001" "redis:6379")

for service in "${SERVICES[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service_name is healthy"
    else
        echo "❌ $service_name is unhealthy"
    fi
done
```

### Log Rotation

```bash
# Configure logrotate for Docker containers
cat > /etc/logrotate.d/homelab-docs << EOF
/var/lib/docker/containers/*/*-json.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /path/to/docker/docker-compose.yml restart
    endscript
}
EOF
```

## Security Hardening

### SSL/TLS Setup

```bash
# Generate strong SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout homelab-docs.key -out homelab-docs.crt \
  -subj "/C=US/ST=State/L=City/O=HomelabDocs/CN=homelab-docs.local" \
  -addext "subjectAltName=DNS:localhost,DNS:homelab-docs.local"

# Configure nginx for SSL
# Update docker/nginx.conf with SSL configuration
```

### Authentication and Authorization

```bash
# Create admin user with strong password
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | cut -c1-25)

# Enable two-factor authentication
ENABLE_2FA=true
2FA_SECRET_KEY=your_2fa_secret_here
```

### Network Security

```bash
# Configure firewall rules
# Allow only necessary ports
# Implement rate limiting
# Enable intrusion detection

# SSL/TLS best practices
# Use strong cipher suites
# Implement HSTS
# Regular certificate rotation
```

## Version Updates

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Update Docker images
docker-compose -f docker/docker-compose.yml pull

# Recreate containers with latest images
docker-compose -f docker/docker-compose.yml up --force-recreate -d
```

### Database Migration

```bash
# Backup before migration
./backup.sh

# Run migration script
docker-compose -f docker/docker-compose.yml exec ai-backend python migrate.py

# Verify migration
curl http://localhost:8001/api/health
```

## Support and Community

### Getting Help

1. **Documentation**: [https://homelab-docs.readthedocs.io/](https://homelab-docs.readthedocs.io/)
2. **GitHub Issues**: [https://github.com/0Reliance/Pozi-0reliance-Lab/issues](https://github.com/0Reliance/Pozi-0reliance-Lab/issues)
3. **Discussions**: [https://github.com/0Reliance/Pozi-0reliance-Lab/discussions](https://github.com/0Reliance/Pozi-0reliance-Lab/discussions)
4. **Wiki**: [https://github.com/0Reliance/Pozi-0reliance-Lab/wiki](https://github.com/0Reliance/Pozi-0reliance-Lab/wiki)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Reporting Issues

When reporting issues, please include:
- Operating system and version
- Docker version (if applicable)
- Browser and version (for web UI issues)
- Error messages and logs
- Steps to reproduce the issue
- Expected vs. actual behavior

## FAQ

### General Questions

**Q: Can I run this without Docker?**
A: Yes, see the "Local Development" section for Python-based installation.

**Q: Do I need an OpenAI API key?**
A: AI features require an OpenAI API key, but the basic documentation functionality works without it.

**Q: How much does this cost to run?**
A: The main costs are for the OpenAI API (usage-based) and hosting. Open-source components are free.

### Technical Questions

**Q: What ports need to be open?**
A: Ports 80, 443, 8000, 8001, and 6379 need to be accessible.

**Q: Can I use a different AI provider?**
A: Yes, the AI backend can be configured to work with OpenAI-compatible APIs.

**Q: How do I backup my data?**
A: See the "Backup and Recovery" section for automated backup procedures.

# Deployment Options

You can deploy Homelab Documentation Hub using several methods:

1. **Local Development**
   - Run `mkdocs serve` and `python ai-backend/main.py` locally for development.
2. **Docker Compose**
   - Use `docker-compose -f docker/docker-compose.yml up --build -d` to run all services in containers.
3. **Static Site Build (Production)**
   - Use the `mkdocs-builder` service in Docker Compose to build static files:
     ```bash
     docker-compose --profile build up mkdocs-builder
     ```
   - Serve the `site/` directory with Nginx or GitHub Pages.
4. **CI/CD Pipeline**
   - Automated tests, builds, and deploys are handled via GitHub Actions (`.github/workflows/ci.yml` and `deploy.yml`).
   - On push or release, the site is built and published to GitHub Pages.
5. **GitHub Pages**
   - The site is automatically deployed to https://0Reliance.github.io/Pozi-0reliance-Lab/ via CI.

See `RELEASE.md` for the full release and deployment checklist.

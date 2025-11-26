# 🚀 Homelab Documentation Hub - Beta Deployment Guide

## 📋 Overview

This guide provides complete instructions for deploying the Homelab Documentation Hub to production and migrating to the new public repository.

## 🎯 Repository Migration

### Step 1: Create New Repository
1. Navigate to https://github.com/0Reliance/Pozi-0reliance-Lab
2. Create a new repository (if not already created)
3. Ensure it's set as public
4. Initialize with a README if desired

### Step 2: Push Clean History
```bash
# Add the new remote repository
git remote add beta https://github.com/0Reliance/Pozi-0reliance-Lab.git

# Push the current state (clean history for beta)
git push beta main

# Set beta as primary remote (optional)
git remote set-url origin https://github.com/0Reliance/Pozi-0reliance-Lab.git
```

### Step 3: Verify Migration
- Check that all files are present in the new repository
- Verify the site builds correctly from the new location
- Test all functionality

## 🛠️ Deployment Options

### Option 1: GitHub Pages (Recommended)
```bash
# Install mkdocs-material with gh-pages support
pip install mkdocs-material mkdocs-gh-pages-plugin

# Configure mkdocs.yml for GitHub Pages
# Add to plugins section:
# - gh-pages:
#     remote_branch: gh-pages
#     remote_name: origin

# Deploy to GitHub Pages
mkdocs gh-deploy --force
```

### Option 2: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8000
```

### Option 3: Static Web Server
```bash
# Build the site
mkdocs build

# Deploy the site/ directory to any web server
# Examples:
# - Apache: Copy to /var/www/html/
# - Nginx: Copy to /usr/share/nginx/html/
# - S3: Sync site/ directory to S3 bucket
```

## 🔧 Configuration Requirements

### Environment Variables
```bash
# AI Backend Configuration
AI_API_KEY=your_openai_api_key
AI_MODEL=gpt-3.5-turbo
REDIS_URL=redis://localhost:6379

# Site Configuration
SITE_URL=https://your-domain.com
SITE_NAME=Homelab Documentation Hub
```

### Docker Requirements
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB storage minimum

### Python Requirements
- Python 3.8+
- See requirements.txt for complete list

## 🚀 Production Deployment Steps

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/0Reliance/Pozi-0reliance-Lab.git
cd Pozi-0reliance-Lab

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Deploy with Docker Compose
docker-compose up -d
```

### 3. SSL/TLS Configuration
```bash
# Using Let's Encrypt with Nginx
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Health check script
./scripts/health-check.sh
```

### Backup Procedures
```bash
# Automated backup
./scripts/backup.sh

# Manual backup
tar -czf homelab-docs-backup-$(date +%Y%m%d).tar.gz .
```

### Updates & Maintenance
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Change default passwords
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review API permissions
- [ ] Set up rate limiting
- [ ] Enable logging

### API Security
```bash
# Secure AI API endpoints
# Use environment variables for API keys
# Implement rate limiting
# Add authentication for admin functions
```

## 🌐 CDN & Performance Optimization

### Static Asset Optimization
```yaml
# mkdocs.yml optimizations
plugins:
  - search
  - minify:
      minify_html: true
  - git-revision-date-localized
  - awesome-pages
```

### CDN Configuration
- Configure CDN for static assets
- Enable gzip compression
- Set appropriate cache headers
- Use HTTP/2 if available

## 📈 Scaling Considerations

### Horizontal Scaling
- Load balancer configuration
- Multiple container instances
- Database scaling
- Session management

### Performance Monitoring
- Response time monitoring
- Error rate tracking
- Resource utilization
- User analytics

## 🆘 Troubleshooting

### Common Issues
1. **Build Failures**: Check Python dependencies
2. **Docker Issues**: Verify Docker daemon status
3. **AI Backend**: Check API keys and Redis connection
4. **Performance**: Review resource allocation

### Debug Commands
```bash
# Build issues
mkdocs build --verbose

# Docker issues
docker-compose logs web
docker-compose logs ai-backend

# Service health
curl http://localhost:8000/health
```

## 📞 Support & Resources

### Documentation
- Site: https://your-domain.com
- API Docs: https://your-domain.com/api
- Admin Guide: https://your-domain.com/admin

### Community Support
- GitHub Issues: https://github.com/0Reliance/Pozi-0reliance-Lab/issues
- Discussions: https://github.com/0Reliance/Pozi-0reliance-Lab/discussions

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Repository migrated to new location
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Backup procedures in place
- [ ] Monitoring configured

### Post-Deployment
- [ ] Site builds successfully
- [ ] All pages load correctly
- [ ] AI assistant functional
- [ ] Search working
- [ ] Mobile responsive
- [ ] Performance acceptable
- [ ] Security measures active

---

**Status**: ✅ **BETA DEPLOYMENT READY**  
**Repository**: https://github.com/0Reliance/Pozi-0reliance-Lab  
**Timeline**: Ready for immediate deployment

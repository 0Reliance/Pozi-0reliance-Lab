# Homelab Documentation System - Troubleshooting Action Plan

## 🚨 Critical Issues Identified

### Current System Status
- **All containers are in restart loops**
- **Redis is the only healthy container**
- **System completely non-functional**

### Root Cause Analysis

#### 1. Shell Compatibility Issue (Critical)
**Problem**: MkDocs container failing with `sh: 3: source: not found`
**Impact**: Prevents documentation service from starting
**Root Cause**: Using `source` command in `/bin/sh` environment

#### 2. FastAPI Import Error (Critical)
**Problem**: `ModuleNotFoundError: No module named 'fastapi.middleware.base'`
**Impact**: AI backend service cannot start
**Root Cause**: FastAPI 0.122.0 changed import paths, code using deprecated imports

#### 3. Container Dependency Cascade (High)
**Problem**: Nginx cannot resolve upstream `mkdocs:8000`
**Impact**: Reverse proxy fails, blocking all external access
**Root Cause**: MkDocs container not running due to shell issues

#### 4. Missing Environment Configuration (High)
**Problem**: Likely missing `.env` file with required secrets
**Impact**: Authentication and OpenAI integration failures
**Root Cause**: No environment file present from investigation

## 🔧 Comprehensive Fix Plan

### Phase 1: Immediate Container Fixes (Priority: Critical)

#### 1.1 Fix MkDocs Container Shell Issue
```yaml
# Update docker-compose.yml command
command: >
  sh -c "
    cd /app &&
    . venv/bin/activate &&  # Use '.' instead of 'source'
    mkdocs serve --dev-addr=0.0.0.0:8000 --watch
  "
```

#### 1.2 Fix FastAPI Import Issues
```python
# Update ai-backend/main.py imports
# FROM: from fastapi.middleware.base import BaseHTTPMiddleware
# TO: from starlette.middleware.base import BaseHTTPMiddleware
```

#### 1.3 Update AI Backend Requirements
```txt
# Ensure compatible versions
fastapi>=0.104.0,<0.120.0
starlette>=0.27.0
```

### Phase 2: Environment Configuration (Priority: High)

#### 2.1 Create Environment File
```bash
# Generate required secrets
SECRET_KEY=$(openssl rand -hex 32)
```

#### 2.2 Configure Required Variables
```env
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=generated-32-character-secret
ALLOWED_ORIGINS=http://localhost:8000,http://localhost
REDIS_URL=redis://redis:6379/0
```

### Phase 3: Container Orchestration Fixes (Priority: High)

#### 3.1 Fix Docker Compose Dependencies
```yaml
# Update health checks and dependencies
depends_on:
  mkdocs:
    condition: service_healthy
  ai-backend:
    condition: service_healthy
  redis:
    condition: service_started
```

#### 3.2 Improve Restart Policies
```yaml
restart: unless-stopped
deploy:
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
```

### Phase 4: Security Hardening (Priority: Medium)

#### 4.1 Update Docker Security
```yaml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp:noexec,nosuid,size=100m
```

#### 4.2 Network Isolation
```yaml
networks:
  homelab-docs-network:
    driver: bridge
    internal: false
    enable_ipv6: false
```

### Phase 5: Monitoring and Logging (Priority: Medium)

#### 5.1 Implement Proper Logging
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### 5.2 Health Check Improvements
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

## 📋 Implementation Checklist

### Immediate Actions (First 30 minutes)
- [ ] Fix MkDocs container shell command in docker-compose.yml
- [ ] Update FastAPI imports in ai-backend/main.py
- [ ] Create .env file with required secrets
- [ ] Update ai-backend requirements.txt with compatible versions

### Container Rebuild (Next 15 minutes)
- [ ] Stop all containers: `docker-compose down`
- [ ] Rebuild images: `docker-compose build --no-cache`
- [ ] Start services: `docker-compose up -d`
- [ ] Verify container status: `docker ps`

### Validation (Next 15 minutes)
- [ ] Test MkDocs service: `curl http://localhost:8000`
- [ ] Test AI backend: `curl http://localhost:8001/health`
- [ ] Test Nginx proxy: `curl http://localhost`
- [ ] Check logs for errors: `docker-compose logs`

### Functionality Testing (Next 30 minutes)
- [ ] Test documentation access through web interface
- [ ] Test AI backend API endpoints
- [ ] Verify authentication flow
- [ ] Test file upload functionality

## 🚀 Recovery Commands

### Complete System Reset
```bash
# Stop and remove all containers
docker-compose down --volumes --remove-orphans

# Remove built images
docker-compose down --rmi all

# Clean up unused resources
docker system prune -f

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d

# Monitor startup
docker-compose logs -f
```

### Individual Service Resets
```bash
# Reset MkDocs only
docker-compose stop mkdocs
docker-compose build mkdocs --no-cache
docker-compose up -d mkdocs

# Reset AI Backend only
docker-compose stop ai-backend
docker-compose build ai-backend --no-cache
docker-compose up -d ai-backend
```

## 🔍 Troubleshooting Commands

### Container Diagnostics
```bash
# Check all container status
docker ps -a

# View recent logs
docker-compose logs --tail=50

# Monitor real-time logs
docker-compose logs -f

# Check container resource usage
docker stats

# Inspect container configuration
docker inspect homelab-docs-mkdocs
```

### Network Diagnostics
```bash
# Check network connectivity
docker network ls
docker network inspect homelab-docs_homelab-docs-network

# Test service reachability
docker exec homelab-docs-mkdocs curl -f http://localhost:8000
docker exec homelab-docs-ai-backend curl -f http://localhost:8000/health
```

## 📊 Success Criteria

### System Health Indicators
- ✅ All containers running without restart loops
- ✅ Health checks passing for all services
- ✅ Documentation accessible via web browser
- ✅ AI backend API responding to health checks
- ✅ Nginx reverse proxy functioning correctly
- ✅ No error messages in container logs

### Functionality Verification
- ✅ Documentation pages load correctly
- ✅ AI chat interface functional
- ✅ File uploads working
- ✅ Authentication system operational
- ✅ Navigation functioning properly

## 🚨 Rollback Plan

If fixes introduce new issues:

1. **Immediate Rollback**: Revert to last working git commit
2. **Configuration Rollback**: Restore docker-compose.yml from backup
3. **Partial Rollback**: Disable problematic services temporarily

### Rollback Commands
```bash
# Git rollback
git checkout 843b8198  # Last known good commit

# Docker rollback
docker-compose down
git checkout HEAD~1 -- docker-compose.yml
docker-compose up -d
```

## 📞 Emergency Contacts

- **System Administrator**: [Contact Information]
- **Development Team**: [Contact Information]
- **Infrastructure Support**: [Contact Information]

---

**Last Updated**: 2025-11-27  
**Version**: 1.0  
**Status**: Ready for Implementation

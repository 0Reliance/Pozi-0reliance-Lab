# Phase 2 Deployment Checklist

**Status**: ✅ Ready for Deployment  
**Date**: December 1, 2025  
**Risk Level**: VERY LOW

---

## Pre-Deployment Verification

- [x] Nginx configuration syntax valid
- [x] Authentication directives in place (HTTP + HTTPS)
- [x] htpasswd file exists and contains valid credentials
- [x] API endpoints remain unprotected
- [x] Admin panel still protected
- [x] Documentation updated with Phase 3 options
- [x] No breaking changes introduced
- [x] Rollback plan documented

---

## Deployment Steps

### Step 1: Backup Current Configuration
```bash
# Backup current nginx.conf
cp docker/nginx.conf docker/nginx.conf.backup-$(date +%Y%m%d-%H%M%S)

# Backup htpasswd
cp docker/htpasswd docker/htpasswd.backup-$(date +%Y%m%d-%H%M%S)
```

### Step 2: Verify Changes
```bash
# Show what's changed
git diff docker/nginx.conf

# Expected output: 4 new lines adding auth_basic directives
```

### Step 3: Deploy Changes
```bash
# Rebuild Nginx container with updated config
docker-compose build nginx

# Bring up the container
docker-compose up -d nginx

# Check container is running
docker-compose ps nginx
```

### Step 4: Verify Nginx Started Successfully
```bash
# Check logs for errors
docker-compose logs nginx | tail -20

# Should see: "nginx: master process /usr/sbin/nginx"
# Should NOT see: "error", "failed", "exit"
```

### Step 5: Test Authentication Gateway
```bash
# Test HTTP access (should prompt for login)
curl -v http://localhost/

# Expected response: 401 Unauthorized (Browser UI prompts for credentials)
# With credentials: HTTP 200 (Access granted)

# Test HTTPS access
curl -v https://localhost/docs/ --insecure

# Expected: Same behavior, with auth prompt
```

### Step 6: Test with Valid Credentials
```bash
# Get admin credentials from htpasswd file
cat docker/htpasswd

# Test with curl using Basic Auth
curl --basic --user admin:PASSWORD http://localhost/ -I

# Expected response: HTTP 200 OK
# (Replace PASSWORD with actual password from htpasswd)
```

### Step 7: Verify API Access (No Auth Required)
```bash
# Test API endpoints (should work without authentication)
curl http://localhost/api/health

# Expected: Success (no 401 Unauthorized)

# Test auth endpoints
curl http://localhost/auth/health

# Expected: Success (no 401 Unauthorized)
```

### Step 8: Verify Documentation Still Works
```bash
# After authentication, verify docs pages load
# Visit http://localhost/ in browser
# Enter credentials when prompted
# Should see homepage with parallax hero and stats

# Click around to verify:
# - Navigation works
# - Links work
# - Parallax animations still smooth
# - Stats section visible
```

### Step 9: Verify Admin Panel
```bash
# Admin panel should still be protected
curl --basic --user admin:PASSWORD http://localhost/admin/ -I

# Expected: HTTP 200 OK (with credentials)

# Without credentials:
curl http://localhost/admin/ -I

# Expected: HTTP 401 Unauthorized
```

### Step 10: Verify Other Pages Not Affected
```bash
# Check that non-homepage pages work correctly
curl --basic --user admin:PASSWORD http://localhost/coursework/cs/ -I
curl --basic --user admin:PASSWORD http://localhost/guides/ -I
curl --basic --user admin:PASSWORD http://localhost/homelab/ -I

# All should return HTTP 200 OK
```

---

## Smoke Test Checklist

After deployment, verify these key scenarios:

### Homepage
- [ ] Navigate to http://localhost/ without auth → sees login prompt
- [ ] Enter admin credentials → sees homepage
- [ ] Parallax hero visible and animating
- [ ] Stats numbers visible and animating when scrolled
- [ ] Navigation bar visible and interactive
- [ ] Admin Portal button visible (links to /admin)

### API Access
- [ ] GET http://localhost/api/health → 200 OK (no auth)
- [ ] GET http://localhost/auth/health → 200 OK (no auth)
- [ ] Third-party integrations still work

### Admin Panel
- [ ] Access http://localhost/admin/ with credentials → 200 OK
- [ ] Access http://localhost/admin/ without credentials → 401 Unauthorized

### Documentation Pages
- [ ] After login, all pages accessible
- [ ] Search functionality works
- [ ] Links between pages work
- [ ] Images and assets load
- [ ] No console errors in browser DevTools

### Browser Caching
- [ ] After first login, credentials cached
- [ ] Refreshing page doesn't re-prompt
- [ ] Closing/reopening browser may re-prompt (browser behavior)

---

## Rollback Plan (If Issues)

If authentication gateway causes problems:

### Quick Rollback (2 minutes)
```bash
# Restore backup configuration
cp docker/nginx.conf.backup-DATE docker/nginx.conf

# Rebuild Nginx container
docker-compose build nginx
docker-compose up -d nginx

# Verify no auth required
curl http://localhost/ -I
# Should get HTTP 200 (or 301 redirect, not 401)
```

### Or Full Revert
```bash
# Revert git changes
git checkout docker/nginx.conf

# Rebuild
docker-compose build nginx
docker-compose up -d nginx
```

---

## Issues & Resolution

### Issue: 401 Unauthorized on all requests
**Cause**: htpasswd file missing or invalid  
**Resolution**:
```bash
# Check file exists
ls -l docker/htpasswd

# Check file is readable
cat docker/htpasswd

# If missing, restore from backup
cp docker/htpasswd.backup docker/htpasswd
```

### Issue: Nginx won't start after change
**Cause**: Configuration syntax error  
**Resolution**:
```bash
# Check syntax
docker exec nginx nginx -t

# If error, revert config
git checkout docker/nginx.conf

# Rebuild
docker-compose build nginx
docker-compose up -d nginx
```

### Issue: API calls failing with 401
**Cause**: Auth applied to API endpoints by mistake  
**Resolution**:
```bash
# Verify nginx.conf has `/auth/` and `/api/` WITHOUT auth_basic
grep -A5 "location /auth/" docker/nginx.conf
grep -A5 "location /api/" docker/nginx.conf

# Should NOT show auth_basic directives in these locations
# If present, remove them (should be in / and /docs/ only)
```

### Issue: SSL certificate errors
**Cause**: HTTPS config references missing SSL files  
**Resolution**:
```bash
# Verify SSL files exist
ls -l docker/ssl/

# If missing, HTTPS block won't start
# Can comment out HTTPS block for testing with HTTP only
```

---

## Post-Deployment Checklist

After successful deployment:

- [ ] Update team documentation with new login requirement
- [ ] Notify users to expect authentication prompt
- [ ] Test on multiple browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile (iOS, Android)
- [ ] Monitor logs for auth-related errors
- [ ] Verify backup copies are safe
- [ ] Document any credential management changes
- [ ] Update runbooks with auth gateway info
- [ ] Brief team on new authentication flow

---

## Performance Monitoring

After deployment, monitor:

### Request Metrics
- Baseline response time should be similar to before
- No increase in 401 errors (except on first unauthenticated request)
- API calls still under 100ms average

### Log Monitoring
```bash
# Watch for auth failures
docker-compose logs nginx | grep "401"

# Watch for configuration errors
docker-compose logs nginx | grep "error"

# Normal operation shows auth logs:
# "nginx: ... auth accepted ..."
```

### Container Health
```bash
# Check container stability
docker-compose ps nginx

# Should show "healthy" or "Up" status
# Not "Restarting" or "Down"
```

---

## Success Criteria

✅ **Deployment Success if:**
- Users see login prompt before accessing docs
- Valid credentials grant access to all pages
- API endpoints remain accessible without auth
- Admin panel still protected
- Homepage parallax animations still smooth
- No errors in browser console
- Nginx container healthy and stable
- All documentation pages load and render correctly

---

## Timeline

| Step | Time | Cumulative |
|------|------|-----------|
| Backup & verify | 2 min | 2 min |
| Rebuild Nginx | 1 min | 3 min |
| Verify startup | 1 min | 4 min |
| Run smoke tests | 3 min | 7 min |
| Verify pages work | 2 min | 9 min |
| Monitor for issues | 1 min | 10 min |
| **Total** | | **~10 minutes** |

---

## Team Communication Template

**Subject**: Authentication Gateway Deployment - Homepage Access Update

**Body**:
```
The documentation site now requires authentication before accessing content.

Changes:
- Users will see a login prompt when visiting the homepage
- Enter your admin credentials to access documentation
- Credentials are cached by your browser for convenience
- This applies only to documentation (homepage and guides)
- API endpoints remain accessible for integrations

How to Access:
1. Visit http://homelab-docs.local/
2. When prompted, enter your username and password
3. Browser will remember credentials for future visits
4. You can clear browser cache to log out if needed

No action required - everything works automatically.

Questions? Contact: [support email]
```

---

## Sign-Off

**Deployed by**: [Your Name]  
**Date**: [Date]  
**Environment**: [Staging/Production]  
**Status**: ✅ All tests passed, deployment successful

---

**Ready to Deploy**: YES ✅

Proceed with: `docker-compose up -d nginx` after git pull

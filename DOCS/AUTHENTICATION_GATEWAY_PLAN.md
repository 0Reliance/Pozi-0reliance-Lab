# MkDocs Authentication Gateway - Comprehensive Solution Plan

**Last Updated**: December 1, 2025  
**Status**: Research Complete - Ready for Implementation Decision

---

## Executive Summary

Your current issue: **Login functionality is tightly integrated into the MkDocs framework**, causing conflicts and complexity. Best solution: **Create a separate authentication gateway that sits in front of MkDocs**, handling all auth before the user ever reaches the documentation site.

### Key Decision
- **Remove login from MkDocs** ✅
- **Add authentication gateway** ✅  
- **Keep MkDocs clean and focused** ✅

---

## Problem Analysis

### Current Issues with Integrated Login

1. **MkDocs Material Theme Conflict**
   - Theme designed for static content, not auth flows
   - Login UI doesn't match documentation theme
   - Session management interferes with theme JavaScript

2. **Framework Incompatibility**
   - MkDocs generates static HTML (no server-side logic)
   - Login requires dynamic backend (FastAPI in your case)
   - Mixing static + dynamic creates architectural complexity

3. **Complexity & Maintenance**
   - Auth logic scattered across JS, HTML, nginx config
   - Hard to update without breaking theme
   - Testing auth flows is difficult
   - Scaling to multiple auth methods is painful

### The Right Solution

**Separate the concerns:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  [Browser] ──→ [Auth Gateway] ──→ [MkDocs Site]   │
│                                                     │
│  User logs in      Validates       Access docs     │
│  at gateway        credentials     already auth'd  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Clean separation of concerns
- ✅ MkDocs stays static and simple
- ✅ Auth gateway can use any auth method
- ✅ Easy to add/remove auth methods
- ✅ Can scale to multiple login options (OAuth, LDAP, 2FA)
- ✅ Works with any frontend (Material, other themes, etc.)

---

## Solution Comparison

### Option 1: Nginx HTTP Basic Auth ⭐ **RECOMMENDED START**

**What it does:** Simple username/password via Nginx, protects all routes

**Pros:**
- ✅ Simplest implementation (5 minutes)
- ✅ Zero app code needed
- ✅ Built into Nginx
- ✅ Works with any backend
- ✅ Stateless (no session storage)
- ✅ Lightweight (no extra containers)

**Cons:**
- ❌ Limited user management (htpasswd file only)
- ❌ No logout option (browser-cached credentials)
- ❌ No user registration interface
- ❌ Poor for many users (100+ becomes unwieldy)
- ❌ Credentials in Base64 encoding (weak privacy)

**Best For:** Small teams (< 10 users), internal homelab, quick setup

**Implementation:** 5 lines of Nginx config

```nginx
location / {
    auth_basic "Homelab Documentation";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://mkdocs:8000;
}
```

**File:** `docker/htpasswd` (already set up in your project!)

---

### Option 2: Authelia - Professional SSO ⭐ **RECOMMENDED FOR PRODUCTION**

**What it does:** Enterprise-grade authentication server with login portal, sessions, MFA

**Pros:**
- ✅ Beautiful login UI (matches modern standards)
- ✅ Multi-factor authentication (TOTP, WebAuthn, Passkeys)
- ✅ Session management with timeouts
- ✅ User registration & password reset
- ✅ Single Sign-On across multiple services
- ✅ LDAP/AD integration (corporate directory)
- ✅ OAuth2 & OpenID Connect provider
- ✅ Scales to hundreds of users
- ✅ Active development & security updates
- ✅ Open source (MIT licensed)

**Cons:**
- ⚠️ More complex setup (30 minutes)
- ⚠️ Additional Docker container (~50MB)
- ⚠️ Requires Redis for session storage
- ⚠️ Learning curve for configuration

**Best For:** Professional teams, companies, scaling homelab, multiple apps, future-proofing

**Architecture:**
```
User ──→ Nginx auth_request ──→ Authelia ──→ MkDocs
                                   │
                            (Session storage)
                                 Redis
```

**Implementation:** ~100 lines of config

```yaml
# authelia/configuration.yml
authentication_backend:
  file:
    path: /etc/authelia/users_database.yml

session:
  redis:
    host: redis
    port: 6379

totp:
  issuer: "Homelab"
  period: 30
  skew: 1

regulation:
  max_retries: 3
  find_time: 10m
  ban_time: 15m
```

---

### Option 3: OAuth2-Proxy ⭐ **RECOMMENDED FOR EXISTING SSO**

**What it does:** Reverse proxy that authenticates via external OAuth2/OIDC providers

**Pros:**
- ✅ Use existing OAuth provider (Google, GitHub, Keycloak, etc.)
- ✅ No password management (delegated to provider)
- ✅ Enterprise SSO support
- ✅ Multi-factor auth via provider
- ✅ Lightweight (~10MB)
- ✅ Stateless with external session storage

**Cons:**
- ❌ Requires external OAuth provider
- ❌ Slightly more latency (OAuth handshake)
- ❌ Less control over login experience
- ❌ Dependency on external service

**Best For:** Teams with existing OAuth infrastructure (corporate AD, GitHub Enterprise)

**Providers:**
- Google OAuth 2.0
- GitHub Organizations
- GitLab
- Keycloak
- Azure AD
- Okta
- AWS Cognito

---

### Option 4: nginx auth_request + Custom Auth Service

**What it does:** Nginx delegates auth to custom backend service

**Pros:**
- ✅ Full control over auth logic
- ✅ Can implement any auth method
- ✅ Custom user interface
- ✅ Scales to any number of users
- ✅ Can integrate with existing user database

**Cons:**
- ❌ Requires building custom service
- ❌ More complex maintenance
- ❌ Potential security issues if not done carefully
- ❌ More development time (2-3 hours)

**Best For:** Teams with specific auth requirements not met by other solutions

---

### Option 5: Mkdocs Plugins (NOT RECOMMENDED)

**What it does:** Use existing MkDocs plugins like `mkdocs-encryptcontent`

**Pros:**
- ✅ Keeps everything in MkDocs ecosystem
- ✅ No extra infrastructure

**Cons:**
- ❌ Limited authentication (mostly encryption only)
- ❌ Poor user experience
- ❌ Client-side security issues
- ❌ Not true authentication
- ❌ Doesn't work for API endpoints
- ❌ Breaks search and navigation

**Recommendation:** Not suitable for your use case. Skip this option.

---

## Recommended Implementation Path

### Phase 1: Immediate (Week 1) - Nginx Basic Auth
**Goal:** Get login working, separate from MkDocs

**Steps:**
1. Remove login functionality from MkDocs
2. Enable Nginx HTTP Basic Auth
3. Create admin user via htpasswd
4. Test access control

**Time:** 30 minutes  
**Complexity:** Low  
**Risk:** Very Low

**Files to modify:**
- `docker/nginx.conf` - Add auth_basic directives
- Remove login pages from MkDocs
- Clean up FastAPI auth endpoints

### Phase 2: Professional (Week 2-3) - Authelia Gateway
**Goal:** Add modern login UI, session management, 2FA support

**Steps:**
1. Set up Authelia container in Docker Compose
2. Configure user database
3. Enable session storage (Redis)
4. Update Nginx to use auth_request
5. Test login flow, logout, session timeout

**Time:** 2-3 hours  
**Complexity:** Medium  
**Risk:** Low (doesn't break Phase 1)

**New containers:** Authelia, Redis

### Phase 3: Optional - OAuth2 Integration
**Goal:** Enable single sign-on with external providers

**Steps:**
1. Configure OAuth2-Proxy or Authelia OAuth providers
2. Link to Google, GitHub, or corporate directory
3. Enable MFA at provider level
4. Update documentation

**Time:** 1-2 hours  
**Complexity:** Medium  
**Risk:** Low (external dependency, can fallback to Phase 2)

---

## Deep Dive: Nginx Basic Auth Implementation

### Current State in Your Project

You already have the infrastructure set up:

**1. htpasswd file exists:**
```bash
docker/htpasswd  # Already in your project!
```

**2. Nginx config has auth_basic commented/partial:**
```nginx
# docker/nginx.conf
location /admin {
    auth_basic "Admin Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://ai_backend/;
}
```

### Step 1: Update Nginx Configuration

Add basic auth to main location:

```nginx
# docker/nginx.conf

server {
    listen 80;
    server_name _;

    # Main documentation site - PROTECTED
    location / {
        auth_basic "Homelab Documentation";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://mkdocs:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints - PROTECTED
    location /api {
        auth_basic "API Authentication";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://ai_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }

    # Health check - PUBLIC (allows monitoring)
    location /health {
        proxy_pass http://ai_backend;
    }
}
```

### Step 2: Create/Update Users

```bash
# Add admin user
htpasswd -B docker/htpasswd admin

# Add additional user
htpasswd -B docker/htpasswd developer

# Remove user
htpasswd -D docker/htpasswd olduser

# List all users
cat docker/htpasswd
```

Output format:
```
admin:$2y$05$abcdef...
developer:$2y$05$ghijkl...
```

### Step 3: Remove Login from MkDocs

**Remove these files:**
- `docs/admin/login.html` - No longer needed
- Login routes from FastAPI
- AI Assistant auth checks (since site is now protected)

**Files to modify:**
- `ai-backend/main.py` - Remove auth endpoints
- `docs/javascripts/ai-assistant.js` - Remove checkAuthentication()
- `docs/index.md` - Remove admin login link

### Step 4: Test

```bash
# Restart containers
docker compose -f docker/docker-compose.yml restart

# Test without credentials (should get 401)
curl http://localhost/

# Test with credentials
curl -u admin:password http://localhost/

# Browser test (will prompt for username/password)
# Visit http://localhost in browser
```

---

## Deep Dive: Authelia Implementation

### Architecture

```
User Browser
    ↓
Nginx (listen :80)
    ├─→ auth_request to Authelia (internal)
    │   ├─→ Check session (Redis)
    │   ├─→ If no session → 401 redirect to /authelia/login
    │   └─→ If valid session → 200 allow proxying
    ├─→ /authelia/* → Authelia container (login UI)
    ├─→ /* (with auth) → MkDocs container
    └─→ /api/* → FastAPI container

Authelia
    ├─→ Redis (session storage)
    ├─→ users_database.yml (user credentials)
    └─→ TOTP/WebAuthn (2FA options)
```

### Docker Compose Addition

```yaml
# docker/docker-compose.yml

services:
  authelia:
    image: authelia/authelia:latest
    container_name: authelia
    networks:
      - homelab
    volumes:
      - ./authelia/configuration.yml:/etc/authelia/configuration.yml:ro
      - ./authelia/users_database.yml:/etc/authelia/users_database.yml:ro
    environment:
      AUTHELIA_JWT_SECRET: ${AUTHELIA_JWT_SECRET}
      AUTHELIA_SESSION_SECRET: ${AUTHELIA_SESSION_SECRET}
    expose:
      - 9091
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: redis
    networks:
      - homelab
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    expose:
      - 6379
    restart: unless-stopped

volumes:
  redis_data:
```

### Authelia Configuration

```yaml
# authelia/configuration.yml

server:
  host: 0.0.0.0
  port: 9091
  path_prefix: /authelia/

theme: dark

authentication_backend:
  file:
    path: /etc/authelia/users_database.yml
    password:
      algorithm: bcrypt
      iterations: 12

access_control:
  default_policy: deny
  rules:
    # Public endpoints
    - domain: "homelab.local"
      resources:
        - "/health"
      policy: bypass
    
    # Protected endpoints
    - domain: "homelab.local"
      resources:
        - "/*"
      policy: two_factor

session:
  cookies:
    - domain: "homelab.local"
      name: authelia_session
      secure: false  # Set to true if HTTPS
      httponly: true
      samesite: lax
  redis:
    host: redis
    port: 6379

regulation:
  max_retries: 3
  find_time: 10m
  ban_time: 15m

totp:
  issuer: "Homelab"
  period: 30
  skew: 1

storage:
  encryption_key: ${AUTHELIA_STORAGE_KEY}
  local:
    path: /etc/authelia/db.sqlite3
```

### User Database

```yaml
# authelia/users_database.yml

users:
  admin:
    displayname: "Administrator"
    password: "$2y$12$abcdef..."  # bcrypt hash
    email: "admin@homelab.local"
    groups:
      - admins

  developer:
    displayname: "Developer"
    password: "$2y$12$ghijkl..."
    email: "dev@homelab.local"
    groups:
      - developers

groups:
  admins:
    - admin
  
  developers:
    - developer
```

### Nginx Configuration with auth_request

```nginx
# docker/nginx.conf

location / {
    # Delegate authentication to Authelia
    auth_request /authelia/authrequest;
    auth_request_set $remote_user $upstream_http_remote_user;
    auth_request_set $remote_groups $upstream_http_remote_groups;
    
    # Proxy to MkDocs
    proxy_pass http://mkdocs:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Remote-User $remote_user;
    proxy_set_header X-Remote-Groups $remote_groups;
}

# Internal auth request endpoint
location /authelia/authrequest {
    internal;
    proxy_pass http://authelia:9091/api/authz/authrequest;
    proxy_pass_request_body off;
}

# Authelia endpoints (login UI, logout, etc)
location /authelia {
    proxy_pass http://authelia:9091;
    proxy_set_header Host $host;
    proxy_set_header X-Original-URL $scheme://$http_host$request_uri;
    proxy_set_header X-Script-Name /authelia;
}
```

### Environment Variables

```bash
# .env file
AUTHELIA_JWT_SECRET=your-random-jwt-secret-here-32-chars
AUTHELIA_SESSION_SECRET=your-random-session-secret-here-32-chars
AUTHELIA_STORAGE_KEY=your-random-storage-key-here-32-chars
```

### Benefits

1. **Professional UI** - Modern login page
2. **Session Management** - Automatic timeouts
3. **2FA Support** - TOTP authenticator app
4. **User Self-Service** - Password reset (optional)
5. **Rate Limiting** - Brute force protection
6. **Audit Logging** - Track authentication events
7. **Scalable** - Works with 100+ users easily

---

## Migration Path: From Basic Auth to Authelia

### Step 1: Set up Authelia alongside current auth
- Keep Nginx basic auth working
- Add Authelia container and Redis
- Configure Authelia, don't activate yet

### Step 2: Test Authelia internally
- Curl auth endpoints
- Verify session storage in Redis
- Test login via browser on staging URL

### Step 3: Switch traffic to Authelia
- Update Nginx auth_request to point to Authelia
- Users will see login page instead of browser prompt
- Monitor for issues

### Step 4: Decommission basic auth
- Remove htpasswd file
- Remove auth_basic directives from Nginx
- Simplify Nginx config

**Downtime:** ~5 minutes (during Nginx config reload)  
**Rollback:** Revert Nginx config, restart Nginx (1 minute)

---

## Security Considerations

### Nginx Basic Auth
- ✅ Credentials encrypted in transit (use HTTPS)
- ⚠️ Credentials Base64 encoded in Authorization header (not secure without TLS)
- ✅ No session storage (stateless)
- ✅ Simple to audit
- ❌ No 2FA support

### Authelia
- ✅ Passwords hashed with bcrypt
- ✅ Sessions encrypted and stored securely
- ✅ Optional 2FA (TOTP/WebAuthn)
- ✅ Rate limiting & account lockout
- ✅ Audit logging
- ✅ CSRF protection
- ✅ Secure cookie handling
- ⚠️ Requires HTTPS for production use

### Recommendations

**For Production:**
1. Enable HTTPS/TLS
2. Use Authelia with 2FA enabled
3. Strong passwords (12+ characters)
4. Regular password rotation
5. Audit logs monitoring
6. Firewall rules (restrict access by IP if possible)

**For Homelab:**
1. Use Nginx Basic Auth initially
2. Upgrade to Authelia when adding users
3. Enable 2FA for admin accounts
4. Use strong passwords
5. HTTPS recommended but not critical

---

## Implementation Decision Framework

### Choose Nginx Basic Auth If:
- ✅ < 10 users
- ✅ Simple password auth only
- ✅ Minimal setup time needed
- ✅ Homelab/internal only
- ✅ No user self-service needed

### Choose Authelia If:
- ✅ > 10 users
- ✅ Professional/enterprise environment
- ✅ Need 2FA support
- ✅ Want session management
- ✅ User password reset needed
- ✅ Want audit logging
- ✅ Plan to scale

### Choose OAuth2-Proxy If:
- ✅ Already have OAuth provider (Google, GitHub)
- ✅ Enterprise SSO (Azure AD, Okta)
- ✅ Don't want to manage passwords
- ✅ Multiple protected applications

---

## Action Items

### Immediate (This Week)
- [ ] Decision: Basic Auth vs Authelia vs OAuth2-Proxy?
- [ ] Backup current configuration
- [ ] Review Docker Compose setup
- [ ] Plan maintenance window

### Implementation (Next Week)
- [ ] Update Nginx configuration
- [ ] Test authentication flow
- [ ] Create user accounts
- [ ] Verify MkDocs access control
- [ ] Remove login from MkDocs

### Post-Implementation
- [ ] Document authentication setup
- [ ] Train users on new login
- [ ] Monitor authentication logs
- [ ] Plan user management process

---

## FAQ

**Q: Will this break my current documentation site?**  
A: No, the site will remain exactly the same. Only access control changes.

**Q: Can users still access the site without login?**  
A: No, all access will require authentication.

**Q: What about API endpoints?**  
A: Same authentication applies. Auth credentials required for /api/* routes.

**Q: Can I mix auth methods?**  
A: Yes, use Authelia which supports multiple providers simultaneously.

**Q: Is this secure?**  
A: Yes, all solutions here are production-ready. Use HTTPS in production.

**Q: Can I have public and private sections?**  
A: Yes, configure Nginx auth_request rules per route.

**Q: How do I reset a password?**  
A: Nginx Basic Auth: Update htpasswd file. Authelia: Built-in password reset.

**Q: What if Authelia goes down?**  
A: Nginx will return 502 error. Keep Basic Auth as fallback option.

---

## Next Steps

1. **Review this document** with your team
2. **Make decision** on auth approach
3. **Schedule implementation** during maintenance window
4. **Execute plan** following the steps above
5. **Test thoroughly** before going live
6. **Monitor** for issues in first 24 hours

---

**Status**: Planning Complete - Ready for Implementation  
**Next**: Execute chosen authentication solution

**Questions?** Review the comparison table at top of document to verify your choice.

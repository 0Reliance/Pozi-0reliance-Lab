# MkDocs Authentication Solutions Research

**Date:** December 1, 2025  
**Research Focus:** Industry-standard approaches for adding authentication to MkDocs documentation sites

---

## Executive Summary

This document summarizes the top practical authentication solutions for MkDocs, with special consideration for Docker environments and Material theme compatibility. MkDocs itself is a static site generator, so authentication must be implemented at the reverse proxy layer or through post-build processing.

---

## Top 5 Authentication Solutions for MkDocs

### 1. **Nginx with HTTP Basic Auth (htpasswd) + Docker**

**Overview:**  
The simplest and most traditional approach. Uses Nginx reverse proxy with HTTP Basic Authentication configured via `.htpasswd` files.

**Implementation:**
- Deploy MkDocs site behind Nginx
- Configure Nginx with `auth_basic` directive
- Use `.htpasswd` file for credential management
- Everything runs in Docker containers

**Example Configuration:**
```nginx
location / {
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://mkdocs:8000;
}
```

**Pros:**
- ✅ Extremely simple to implement
- ✅ Very lightweight
- ✅ Works perfectly with Docker
- ✅ No additional services needed
- ✅ Well-supported by Nginx
- ✅ Compatible with all MkDocs themes including Material

**Cons:**
- ❌ Limited to basic username/password only
- ❌ No user interface for credential management
- ❌ Credentials sent in every request (Base64 encoded)
- ❌ No session management or logout functionality
- ❌ Difficult to manage multiple users at scale
- ❌ No multi-factor authentication
- ❌ Plain text password storage in `.htpasswd`

**Best For:**
- Small team documentation (< 20 users)
- Internal-only access
- Quick deployments
- Homelab environments
- Proof of concepts

**Docker Compose Example:**
```yaml
version: '3'
services:
  mkdocs:
    image: mkdocs:latest
    ports:
      - "8000:8000"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./.htpasswd:/etc/nginx/.htpasswd:ro
```

**Real-world example:** `lalebot/mkdocs-nginx` GitHub repository demonstrates this pattern.

---

### 2. **Authelia - Open Source Authentication & Authorization Server**

**Overview:**  
A full-featured, self-hosted Identity and Access Management (IAM) server that acts as an authentication gateway in front of any application, including MkDocs.

**Key Features:**
- OpenID Connect 1.0 Provider (OpenID Certified™)
- Multi-factor authentication (TOTP, WebAuthn, Passkeys, Push notifications)
- Single Sign-On (SSO)
- Session management with logout
- User interface for login/profile management
- Authorization policies with granular access control
- Password reset functionality
- Login regulation (brute force protection)
- Lightweight (~20MB container, <30MB memory)
- Written in Go for performance

**How It Works:**
1. User requests MkDocs site
2. Nginx `auth_request` module forwards request to Authelia
3. Authelia validates authentication/authorization
4. Returns 200 for authorized access or 401/403 for denied
5. User redirected to Authelia login portal if needed

**Example Nginx Configuration:**
```nginx
location / {
    auth_request /auth;
    proxy_pass http://mkdocs:8000;
}

location = /auth {
    proxy_pass http://authelia:9091/api/verify;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;
}

location /authelia {
    proxy_pass http://authelia:9091;
}
```

**Pros:**
- ✅ Enterprise-grade authentication
- ✅ Modern OAuth2/OpenID Connect support
- ✅ Built-in login UI
- ✅ Session management with logout
- ✅ Multi-factor authentication options
- ✅ Highly scalable (designed for Kubernetes)
- ✅ Granular authorization policies
- ✅ Password reset functionality
- ✅ Brute force protection
- ✅ Works with Material theme
- ✅ Integrates with reverse proxies (Nginx, Traefik)

**Cons:**
- ❌ More complex setup than basic auth
- ❌ Additional service to manage
- ❌ Requires configuration file
- ❌ Learning curve for advanced features
- ⚠️ Needs backend storage (Redis, SQLite, etc.)

**Best For:**
- Teams with multiple users (20-500+)
- Organizations requiring SSO
- Multi-application authentication
- Advanced security requirements
- Future scalability
- Self-hosted infrastructure

**Docker Compose Example:**
```yaml
version: '3'
services:
  mkdocs:
    image: mkdocs:latest
    expose:
      - "8000"
  
  authelia:
    image: authelia/authelia:latest
    ports:
      - "9091:9091"
    volumes:
      - ./authelia/configuration.yml:/etc/authelia/configuration.yml:ro
    environment:
      - AUTHELIA_JWT_SECRET=${JWT_SECRET}
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - mkdocs
      - authelia
```

**Official website:** https://www.authelia.com/

---

### 3. **Nginx auth_request Module + External Auth Service**

**Overview:**  
A hybrid approach using Nginx's `auth_request` module combined with a custom or third-party authentication service. This allows flexible authentication logic while maintaining Nginx's performance.

**Supported Authentication Methods:**
- JWT tokens
- OAuth2 / OpenID Connect
- LDAP/Active Directory
- Custom REST API

**How It Works:**
```
1. Client requests protected resource
2. Nginx intercepts request
3. Nginx makes subrequest to auth endpoint
4. Auth service validates credentials
5. Returns 200 (authorized) or 401/403 (denied)
6. Nginx either passes request through or redirects to login
```

**Example with OAuth2 (using oauth2-proxy):**
```nginx
location / {
    auth_request /oauth2/auth;
    auth_request_set $user $upstream_http_x_auth_request_user;
    proxy_set_header X-User $user;
    proxy_pass http://mkdocs:8000;
}

location = /oauth2/auth {
    proxy_pass http://oauth2-proxy:4180;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}
```

**Pros:**
- ✅ Highly flexible and customizable
- ✅ Can use any authentication backend
- ✅ Excellent performance (Nginx is fast)
- ✅ Integrates standard protocols (OAuth2, OIDC, JWT)
- ✅ Works with existing auth systems
- ✅ Minimal overhead
- ✅ Compatible with Material theme

**Cons:**
- ❌ Requires external auth service
- ❌ More complex configuration
- ❌ Need to manage auth service separately
- ❌ Debugging can be difficult

**Best For:**
- Existing auth infrastructure integration
- OAuth2/OIDC providers (Google, GitHub, Okta)
- Microservices architecture
- Organizations with existing identity systems

**Tools Used:**
- `oauth2-proxy` - OAuth2 reverse proxy
- `Authelia` - Full auth server
- Custom Python/Node.js service

---

### 4. **MkDocs Encryptcontent Plugin - Client-Side Encryption**

**Overview:**  
A MkDocs plugin that encrypts page content during build time and decrypts it in the browser. Users must know the password to view encrypted pages.

**Key Features:**
- AES-256 client-side encryption
- Password inventory with multiple credential levels
- Per-page or global password protection
- Session-based key storage
- Share links with optional partial password
- Content obfuscation
- Ed25519 file signing

**Implementation:**
```yaml
plugins:
  - encryptcontent:
      global_password: 'your_password'
      # Or use password inventory
      password_inventory:
        classified: 'password1'
        confidential:
          - 'password2'
          - 'password3'
        secret:
          user1: 'password1'
          user2: 'password2'
```

**Markdown Usage:**
```markdown
---
password: secret123
---
# This page is protected
Content here is encrypted with AES-256
```

**Pros:**
- ✅ No separate auth infrastructure needed
- ✅ Works with static site hosting (GitHub Pages, Netlify)
- ✅ Client-side encryption (content never exposed to server)
- ✅ Multiple password levels/users
- ✅ Share links with partial passwords
- ✅ Easy to implement
- ✅ Works with Material theme

**Cons:**
- ❌ Not true authentication (no user management)
- ❌ Passwords visible in HTML comments
- ❌ Requires browser support for crypto
- ❌ All users get same static site content
- ❌ Can't revoke access after deployment
- ❌ Poor UX for password management
- ❌ Search index challenges

**Best For:**
- Small team collaboration
- Open source projects with sensitive sections
- Static site hosting
- Additional layer of obfuscation (not primary auth)
- Sharing sensitive documentation
- Content that needs to remain accessible but private

**GitHub Repository:**  
https://github.com/unverbuggt/mkdocs-encryptcontent-plugin

---

### 5. **Mkauthdocs - Post-Build PHP Authentication**

**Overview:**  
A tool that post-processes the built MkDocs static site to add PHP-based authentication via session guards on every page.

**How It Works:**
1. Build MkDocs site normally: `mkdocs build`
2. Run mkauthdocs: `mkauthdocs username password site/`
3. Authentication layer injected into every HTML page
4. Generates login.php page
5. Session-based access control

**PHP Guard Example (auto-generated):**
```php
<?php
session_start();
if (! isset($_SESSION['login']) || ! $_SESSION['login']) {
    $dirname = $_SERVER['REQUEST_URI'] ?? '';
    $dirname = preg_replace('/index.php$/', '', $dirname);
    header("Location: ".$dirname."/login.php?redirect=" . urlencode($_SERVER['REQUEST_URI']));
    exit;
}
?>
```

**Pros:**
- ✅ Simple setup for single credential
- ✅ Works with any PHP-capable host
- ✅ Session-based authentication
- ✅ Logout functionality
- ✅ Redirect after login
- ✅ Minimal resource overhead

**Cons:**
- ❌ Requires PHP on server
- ❌ Plain text password in PHP code
- ❌ Only single username/password
- ❌ No user management
- ❌ Security concerns (plain text storage)
- ❌ Limited customization
- ❌ Dated technology (2018)
- ❌ Doesn't work with static hosting

**Best For:**
- Legacy PHP hosting environments
- Simple internal-only documentation
- Small teams with PHP servers
- Quick deployments without infrastructure

**GitHub Repository:**  
https://github.com/CTXz/mkauthdocs

---

## Comparison Matrix

| Feature | Nginx Basic Auth | Authelia | auth_request | Encryptcontent | Mkauthdocs |
|---------|------------------|----------|--------------|----------------|-----------|
| Setup Complexity | ⭐ Very Simple | ⭐⭐⭐⭐ Complex | ⭐⭐⭐ Moderate | ⭐⭐ Simple | ⭐⭐ Simple |
| Multi-Factor Auth | ❌ No | ✅ Yes | Depends | ❌ No | ❌ No |
| SSO Support | ❌ No | ✅ Yes (OIDC) | Depends | ❌ No | ❌ No |
| User Management | ❌ No | ✅ Yes | Depends | ❌ No | ❌ No |
| Logout Function | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Session Management | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Browser only | ✅ Yes |
| Docker Ready | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Static Hosting | ❌ No | ❌ No | ❌ No | ✅ Yes | ❌ No |
| Scalability | ⭐ Limited | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good | ⭐⭐ Limited | ⭐ Limited |
| Cost | Free | Free (OSS) | Free | Free | Free |
| Maintenance | ⭐ Minimal | ⭐⭐⭐ Moderate | ⭐⭐ Low | ⭐⭐ Low | ⭐⭐⭐⭐ High |
| Material Theme Support | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Recommended Solutions by Use Case

### Small Homelab / Single Team (< 5 users)
**Recommended:** Nginx Basic Auth
- Simplest implementation
- No additional services
- Works perfectly for internal use
- Single `docker-compose.yml` with two services

### Growing Team (5-50 users)
**Recommended:** Authelia
- Professional SSO capabilities
- Multi-factor authentication
- Future scalability
- Easy integration with multiple services

### Existing OAuth2 Infrastructure
**Recommended:** Nginx auth_request + oauth2-proxy
- Leverage existing identity systems
- Integrate with corporate directory (LDAP/AD)
- OAuth2 from Google, GitHub, etc.

### Public Site with Sensitive Sections
**Recommended:** Encryptcontent Plugin
- Deploy to static hosting (GitHub Pages, Netlify)
- No backend infrastructure needed
- Selective content protection

### Legacy PHP Environment
**Recommended:** Mkauthdocs
- Only option for pure PHP hosting
- Minimal requirements
- Quick deployment

---

## Implementation Recommendations for Your Setup

### For Homelab with Docker (Recommended: Nginx Basic Auth)

```yaml
version: '3.8'

services:
  mkdocs:
    build: .
    container_name: mkdocs
    expose:
      - "8000"
    volumes:
      - ./docs:/docs:ro

  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./.htpasswd:/etc/nginx/.htpasswd:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - mkdocs
```

### For Production with SSO (Recommended: Authelia)

```yaml
version: '3.8'

services:
  mkdocs:
    build: .
    expose:
      - "8000"

  authelia:
    image: authelia/authelia:latest
    volumes:
      - ./authelia/configuration.yml:/etc/authelia/configuration.yml:ro
    environment:
      - AUTHELIA_JWT_SECRET=${JWT_SECRET}
      - AUTHELIA_SESSION_SECRET=${SESSION_SECRET}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - mkdocs
      - authelia
```

---

## Security Considerations

### For All Methods:
1. **Use HTTPS/TLS** - Always encrypt credentials in transit
2. **Strong Passwords** - Enforce password policies
3. **Regular Updates** - Keep containers/services updated
4. **Backup Credentials** - Maintain secure backups of auth data
5. **Monitor Access** - Log and audit authentication events

### Specific Concerns:

**HTTP Basic Auth:**
- Credentials Base64 encoded (not encrypted!)
- Must use HTTPS only
- Credentials sent with every request

**Authelia:**
- Use strong JWT/Session secrets
- Integrate with Redis/database securely
- Implement brute force protection (built-in)

**Encryptcontent:**
- Passwords visible to anyone who views page source
- Not suitable for truly sensitive data
- Use for additional obfuscation layer only

---

## Migration Path

If you start with **Nginx Basic Auth** and need to upgrade:

1. Deploy Authelia alongside existing setup
2. Update Nginx configuration gradually
3. Test with subset of users
4. Migrate to full Authelia deployment
5. Remove basic auth configuration

Both Nginx Basic Auth and Authelia can coexist during transition.

---

## Additional Resources

- **Nginx auth_request module:** https://nginx.org/en/docs/http/ngx_http_auth_request_module.html
- **Authelia Documentation:** https://www.authelia.com/overview/authentication/introduction/
- **MkDocs Material Theme:** https://squidfunk.github.io/mkdocs-material/
- **oauth2-proxy:** https://oauth2-proxy.github.io/oauth2-proxy/
- **Encryptcontent Plugin:** https://github.com/unverbuggt/mkdocs-encryptcontent-plugin

---

## Conclusion

The **best solution depends on your specific requirements:**

- **Simplicity & Homelab:** Nginx Basic Auth
- **Enterprise & SSO:** Authelia  
- **Existing OAuth2:** nginx auth_request + oauth2-proxy
- **Static Hosting:** Encryptcontent Plugin
- **Legacy PHP:** Mkauthdocs

For most homelab scenarios with Docker, **Nginx Basic Auth offers the best balance of simplicity, security, and effectiveness** while maintaining full MkDocs Material theme compatibility.


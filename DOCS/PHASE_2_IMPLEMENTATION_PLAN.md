# Phase 2 Implementation Plan - Authentication Gateway & Video Parallax

**Date**: December 1, 2025  
**Status**: Ready for Implementation  
**Scope**: Two concurrent enhancements - authentication refactor + video parallax support

---

## Overview

This plan executes two research findings:
1. **Authentication Gateway** - Move login outside MkDocs using Nginx Basic Auth
2. **Video Parallax** - Update PARALLAX_AND_HERO_GUIDE.md with MP4/GIF implementation options

---

## Part 1: Authentication Gateway Implementation

### Current Problem
- Login UI integrated into MkDocs framework
- Auth logic scattered across FastAPI, Nginx, JavaScript
- Conflicts with Material theme
- Difficult to maintain and scale

### Solution Architecture
```
User Browser
    ↓
    ├─→ [Nginx Basic Auth Gate] ← checks credentials
    │         ↓
    │    [.htpasswd file]
    │
    └─→ [MkDocs Static Site] ← only authenticated users reach here
             ↓
         [Material Theme]
             ↓
          [No login UI]
```

### Implementation Tasks

#### Task 1A: Update Nginx Configuration
**File**: `docker/nginx.conf`

**Changes**:
1. Add authentication to main documentation location `/` and `/docs/`
2. Keep `/auth/`, `/api/`, `/admin` paths WITHOUT basic auth (for API access)
3. Keep admin panel (`/admin`) with existing htpasswd auth

**Current State**:
- Basic auth already exists for `/admin` location ✓
- Main docs location `/` has NO auth (needs to be added)
- API endpoints have no auth (intentional - separate concern)

**Action**:
```nginx
# For HTTP server block (port 80)
location / {
    auth_basic "Homelab Documentation - Login Required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Keep rate limiting
    limit_req zone=docs burst=50 nodelay;
    
    # Keep all existing proxy settings
    proxy_pass http://mkdocs;
    # ... rest of config
}

# For HTTPS server block (port 443)
location /docs/ {
    auth_basic "Homelab Documentation - Login Required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Keep rate limiting
    limit_req zone=docs burst=20 nodelay;
    
    # Keep all existing proxy settings
    proxy_pass http://mkdocs/;
    # ... rest of config
}
```

**Impact**:
- Nginx will now prompt for login before serving any MkDocs content
- Browser caches credentials
- No logout option (browser-managed)
- Works across all pages in `/docs/`

#### Task 1B: Remove Login UI from MkDocs
**File**: `docs/index.md`

**Changes**:
1. Remove or hide login form from homepage
2. Remove login-related JavaScript from extra.js
3. Update hero buttons if they reference login

**Current State**:
- Homepage has `/admin` link in hero buttons
- No visible login form (login is via FastAPI endpoints)

**Action**:
```markdown
# Keep the /admin link as-is (points to admin panel with htpasswd)
# It's still useful for administration
# But users won't reach it through normal doc flow
```

#### Task 1C: Clean Up FastAPI Auth Endpoints
**File**: `ai-backend/main.py` (or relevant auth module)

**Note**: Don't DELETE auth endpoints - they serve the API  
**Action**: Keep them but mark them as "API-only" for documentation

**Review Current**: 
- `/auth/login` - API endpoint (keep)
- `/auth/logout` - API endpoint (keep)
- `/auth/register` - API endpoint (keep, but may disable in config)
- `/admin/login` - If exists, can redirect to `/admin` (Nginx-protected)

---

### Part 1 Verification Checklist

- [ ] Update HTTP server block - add auth to `/` location
- [ ] Update HTTPS server block - add auth to `/docs/` location
- [ ] Keep `/auth/` endpoints unprotected (for API)
- [ ] Keep `/api/` endpoints unprotected (for API)
- [ ] Keep `/admin` with existing auth
- [ ] Test: Access homepage without credentials → prompt
- [ ] Test: Enter valid htpasswd credentials → access granted
- [ ] Test: API endpoints still work without auth
- [ ] Test: Admin panel still works with auth

---

## Part 2: Update PARALLAX_AND_HERO_GUIDE.md with Video/GIF Instructions

### Current State
- PARALLAX_AND_HERO_GUIDE.md exists with Phase 1 & Phase 2 SVG implementation ✓
- VIDEO_GIF_PARALLAX_GUIDE.md exists with detailed video/GIF research ✓

### Integration Task
**File**: `PARALLAX_AND_HERO_GUIDE.md`

**Action**: Add new section linking to video/GIF capabilities

**New Section to Add** (after Phase 2 implementation):

```markdown
## Phase 3: Enhanced Hero with Video/GIF Backgrounds (Optional)

For more immersive hero effects, video and GIF backgrounds are available:

### Video (MP4/WebM) - Recommended for Modern Look
- **Benefits**: Smooth 60fps animation, smaller files than GIF, better quality
- **File Size**: 2-3 MB for 10s 1080p MP4
- **Browser Support**: 97%+
- **Performance**: Hardware accelerated, excellent on mobile
- **Implementation**: See VIDEO_GIF_PARALLAX_GUIDE.md

**Example Video Implementation**:
```html
<video 
  class="parallax-layer parallax-video" 
  data-speed="0.5"
  autoplay 
  muted 
  loop 
  playsinline
  poster="/images/parallax/hero-poster.jpg">
  <source src="/images/parallax/hero-bg.mp4" type="video/mp4">
  <source src="/images/parallax/hero-bg.webm" type="video/webm">
</video>
```

### GIF - Simple & Retro
- **Benefits**: Simple to create, no encoding needed, 99%+ browser support
- **File Size**: 15-25 MB for 10s animation (larger than video)
- **Performance**: CPU intensive, can be choppy
- **Best For**: Pixel art, simple animations, retro effects
- **Implementation**: See VIDEO_GIF_PARALLAX_GUIDE.md

**Example GIF Implementation**:
```html
<div class="parallax-layer parallax-gif" 
     data-speed="0.5" 
     style="background-image: url('../images/parallax/hero-animation.gif');">
</div>
```

### CSS for Video Elements
```css
body.is-home .parallax-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}
```

### Next Steps
1. Create or obtain hero video/GIF file
2. Encode video to MP4 and WebM formats (see VIDEO_GIF_PARALLAX_GUIDE.md)
3. Replace SVG layer with video element
4. Test parallax effect with video background
5. Verify mobile performance

### Resources
- **Complete Guide**: VIDEO_GIF_PARALLAX_GUIDE.md (detailed instructions, FFmpeg commands)
- **Implementation Examples**: Full HTML/CSS/JS code snippets provided
- **Performance Tips**: Mobile optimization strategies
- **Troubleshooting**: Common issues and solutions
```

### Implementation Actions

1. **Read current PARALLAX_AND_HERO_GUIDE.md** to understand structure
2. **Integrate new "Phase 3" section** with video/GIF options
3. **Cross-reference VIDEO_GIF_PARALLAX_GUIDE.md** for detailed implementation
4. **Add decision framework**: SVG vs Video vs GIF comparison table

---

## Execution Order

### Step 1: Authentication Gateway (30 minutes)
1. Backup current nginx.conf
2. Update HTTP server block with auth on `/` location
3. Update HTTPS server block with auth on `/docs/` location
4. Test configuration syntax: `nginx -t`
5. Verify .htpasswd file exists and has valid entries
6. Test local access (should prompt for credentials)

### Step 2: Documentation Update (20 minutes)
1. Open PARALLAX_AND_HERO_GUIDE.md
2. Add Phase 3 section with video/GIF information
3. Link to VIDEO_GIF_PARALLAX_GUIDE.md
4. Add CSS examples for video elements
5. Provide decision framework

### Step 3: Verification (15 minutes)
1. Review all changes
2. Test documentation builds cleanly
3. Document any issues found
4. Create summary of implementation

**Total Time**: ~65 minutes

---

## Risk Assessment

### Authentication Changes
**Risk Level**: LOW
- **Why**: Nginx basic auth is built-in, well-tested
- **Mitigation**: Keep API endpoints unprotected for continued access
- **Fallback**: Can quickly remove `auth_basic` lines if issues arise
- **Test Plan**: Test locally before deploy

### Documentation Changes
**Risk Level**: VERY LOW
- **Why**: Adding information, not changing existing functionality
- **Impact**: No code changes, just documentation updates
- **Rollback**: Simple file revert if needed

---

## Success Criteria

### Authentication Gateway
- ✅ Nginx configuration syntax valid
- ✅ Accessing `/` prompts for login
- ✅ Valid credentials grant access to MkDocs
- ✅ API endpoints still accessible without auth
- ✅ Admin panel still works with htpasswd
- ✅ No 502/503 errors after auth

### Documentation Update
- ✅ PARALLAX_AND_HERO_GUIDE.md updated with Phase 3
- ✅ Cross-references to VIDEO_GIF_PARALLAX_GUIDE.md working
- ✅ Code examples provided for video/GIF
- ✅ Decision framework clear

---

## Files to Modify

1. **docker/nginx.conf** (2 sections: HTTP + HTTPS)
   - Add `auth_basic` to `/` and `/docs/` locations
   - Keep all other config unchanged

2. **PARALLAX_AND_HERO_GUIDE.md** (1 new section)
   - Add Phase 3 with video/GIF information
   - Link to detailed guide
   - Provide code examples

---

## Configuration Preview

### nginx.conf Changes (HTTP Block)
```diff
  location / {
+     auth_basic "Homelab Documentation - Login Required";
+     auth_basic_user_file /etc/nginx/.htpasswd;
      limit_req zone=docs burst=50 nodelay;
      
      proxy_pass http://mkdocs;
      # ... rest unchanged
  }
```

### nginx.conf Changes (HTTPS Block)
```diff
  location /docs/ {
+     auth_basic "Homelab Documentation - Login Required";
+     auth_basic_user_file /etc/nginx/.htpasswd;
      limit_req zone=docs burst=20 nodelay;
      
      proxy_pass http://mkdocs/;
      # ... rest unchanged
  }
```

---

## Phase 2 Future Enhancements (Optional)

If you want to scale beyond basic auth in the future:

### Option A: Authelia Gateway (2-3 hours)
- Professional login UI
- Session management with logout
- Multi-factor authentication (TOTP, WebAuthn)
- Better user management
- Replaces basic auth with modern system

### Option B: OAuth2 Integration (1-2 hours)
- Use existing Google/GitHub/corporate OAuth
- No local password management
- Enterprise SSO support

### Option C: Custom Auth Service (2-3 hours)
- Build custom authentication backend
- Full control over login experience
- Integration with existing FastAPI auth

**Recommendation**: Start with Phase 1 (basic auth now), upgrade to Phase 2 (Authelia) when scaling to teams.

---

## Next Steps After Implementation

1. **Deploy to staging**
2. **Test complete flow**: Access site → prompted for login → valid credentials → access granted
3. **Verify other pages**: Coursework, guides, API all work correctly
4. **Mobile test**: Login flow on mobile browsers
5. **Production deployment**
6. **Document credentials**: Update team access documentation

---

## Questions for You

Before proceeding, confirm:

1. **Authentication Scope**: Should all MkDocs content require login, or just certain sections?
   - Current plan: ALL docs require login (strict protection)
   - Alternative: Only `/admin` and `/api` sections require auth (open access to docs)
   - **Recommendation**: All docs require login (most secure)

2. **Video Parallax**: Ready to add Phase 3 to guide?
   - Just document the option? (no code changes)
   - Or also implement example video?
   - **Recommendation**: Document option now, implement example later if you have video

3. **Timeline**: Implement now or review first?
   - **Ready to proceed immediately?**

---

## Summary

**Phase 2 Plan**: 
- ✅ Separate authentication from MkDocs using Nginx gateway
- ✅ Update documentation with video/GIF parallax options  
- ✅ Maintain clean, maintainable architecture
- ✅ Keep API endpoints accessible for future use
- ✅ Zero impact on other pages

**Time to Complete**: ~1 hour  
**Risk Level**: Very Low  
**Ready to Execute**: Yes, awaiting confirmation

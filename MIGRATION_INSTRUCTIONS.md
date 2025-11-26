# 🚀 Repository Migration Instructions

## 📋 Overview

This document provides the exact steps to migrate the Homelab Documentation Hub from the current repository to the new public beta repository.

## 🎯 Target Repository

**New Repository**: https://github.com/0Reliance/Pozi-0reliance-Lab  
**Current Repository**: https://github.com/genpozi/homelab-docs.git  

## 📝 Migration Steps

### Step 1: Add New Remote
```bash
# Add the new repository as a remote
git remote add beta https://github.com/0Reliance/Pozi-0reliance-Lab.git

# Verify remotes
git remote -v
```

### Step 2: Push to New Repository
```bash
# Push all branches to the new repository
git push beta main

# Push all tags (if any)
git push beta --tags
```

### Step 3: Update Primary Remote (Optional)
```bash
# If you want to make the new repo the default origin
git remote set-url origin https://github.com/0Reliance/Pozi-0reliance-Lab.git

# Or remove the old remote
git remote remove origin
git remote rename beta origin
```

### Step 4: Verify Migration
```bash
# Verify the new repository
git fetch origin
git log --oneline

# Check that all files are present
git ls-files | wc -l
```

## 🔧 Post-Migration Setup

### GitHub Actions (if needed)
If you want to set up automated deployments:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Build site
      run: mkdocs build
      
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
```

### GitHub Pages Configuration
1. Go to repository Settings
2. Navigate to Pages
3. Source: Deploy from a branch
4. Branch: gh-pages
5. Save

## 📊 Migration Checklist

### Pre-Migration ✅
- [ ] All changes committed to current repository
- [ ] BETA_RELEASE_SUMMARY.md created and reviewed
- [ ] DEPLOYMENT_GUIDE.md created with complete instructions
- [ ] Site builds successfully: `mkdocs build`
- [ ] All tests pass: `python -m pytest`
- [ ] Docker configuration tested: `docker-compose up -d`

### Migration Process ✅
- [ ] New repository created at https://github.com/0Reliance/Pozi-0reliance-Lab
- [ ] Remote added: `git remote add beta https://github.com/0Reliance/Pozi-0reliance-Lab.git`
- [ ] Code pushed: `git push beta main`
- [ ] All files verified in new repository
- [ ] Build process tested in new repository

### Post-Migration ✅
- [ ] GitHub Actions configured (if desired)
- [ ] GitHub Pages enabled
- [ ] Site deployed successfully
- [ ] All features working (AI assistant, search, navigation)
- [ ] Mobile responsive design verified
- [ ] SSL/TLS configured (if custom domain)

## 🚀 Quick Deployment Commands

### Option 1: GitHub Pages (Recommended)
```bash
# Install gh-pages plugin
pip install mkdocs-gh-pages-plugin

# Deploy to GitHub Pages
mkdocs gh-deploy --force
```

### Option 2: Docker Deployment
```bash
# Build and run
docker-compose up -d

# Verify deployment
curl http://localhost:8000
```

### Option 3: Manual Build
```bash
# Build static files
mkdocs build

# Deploy site/ directory to your web server
rsync -av site/ user@server:/var/www/html/
```

## 🔍 Verification Steps

After migration, verify:

1. **Site Loads**: https://0reliance.github.io/Pozi-0reliance-Lab/
2. **All Pages Work**: Navigate through all sections
3. **AI Assistant**: Test the AI functionality
4. **Search**: Verify search works correctly
5. **Mobile**: Test on mobile devices
6. **Performance**: Check load times

## 📞 Support

If issues arise during migration:

1. Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions
2. Review the [BETA_RELEASE_SUMMARY.md](BETA_RELEASE_SUMMARY.md) for feature status
3. Check GitHub Actions logs (if configured)
4. Test locally first: `mkdocs serve`

---

## ✅ Migration Complete Checklist

- [ ] Repository migrated to https://github.com/0Reliance/Pozi-0reliance-Lab
- [ ] Site successfully deployed
- [ ] All functionality verified
- [ ] Documentation updated with new repository URL
- [ ] Team notified of new repository location
- [ ] Old repository archived (optional)

---

**Status**: 🚀 **READY FOR MIGRATION**  
**Target**: https://github.com/0Reliance/Pozi-0reliance-Lab  
**Timeline**: Execute immediately upon approval

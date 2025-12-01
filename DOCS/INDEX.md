# Homelab Documentation Hub - Documentation Index

**Last Updated**: December 1, 2025

---

## Quick Navigation

### 🚀 Getting Started (Root Directory)
- **[README.md](../README.md)** - Project overview and main documentation entry point
- **[INSTALLATION.md](../INSTALLATION.md)** - Setup and installation instructions
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines

### 🔒 Security & Operations (Root Directory)
- **[SECURITY.md](../SECURITY.md)** - Security policy and best practices
- **[TROUBLESHOOTING_PLAN.md](../TROUBLESHOOTING_PLAN.md)** - Troubleshooting guide

---

## Documentation Organization

### 📋 Release Documentation (`DOCS/`)

#### Latest Release
- **[RELEASE.md](./RELEASE.md)** - Latest release notes and version history
- **[BETA_RELEASE.md](./BETA_RELEASE.md)** - Beta release information
- **[BETA_RELEASE_SUMMARY.md](./BETA_RELEASE_SUMMARY.md)** - Beta release summary

#### Migration & Updates
- **[MIGRATION_INSTRUCTIONS.md](./MIGRATION_INSTRUCTIONS.md)** - Instructions for updating from previous versions

---

### 🎨 Phase 2 Implementation (Parallax & Auth)

#### Implementation Documents
- **[PHASE_2_INDEX.md](./PHASE_2_INDEX.md)** - Master index for Phase 2 work
- **[PHASE_2_IMPLEMENTATION_PLAN.md](./PHASE_2_IMPLEMENTATION_PLAN.md)** - Detailed implementation plan
- **[PHASE_2_EXECUTION_SUMMARY.md](./PHASE_2_EXECUTION_SUMMARY.md)** - Execution summary and results
- **[PHASE_2_QUICK_REFERENCE_GUIDE.md](./PHASE_2_QUICK_REFERENCE_GUIDE.md)** - Quick reference for Phase 2 features
- **[IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)** - Phase 2 completion status

#### Parallax & Hero Design
- **[PARALLAX_AND_HERO_GUIDE.md](./PARALLAX_AND_HERO_GUIDE.md)** - Complete parallax implementation guide
- **[VIDEO_GIF_PARALLAX_GUIDE.md](./VIDEO_GIF_PARALLAX_GUIDE.md)** - Video and GIF parallax alternatives
- **[PARALLAX_IMPLEMENTATION.md](./PARALLAX_IMPLEMENTATION.md)** - (Deprecated - see PARALLAX_AND_HERO_GUIDE.md)

#### Authentication Gateway
- **[AUTHENTICATION_GATEWAY_PLAN.md](./AUTHENTICATION_GATEWAY_PLAN.md)** - Complete authentication strategy
- **[MKDOCS_AUTH_RESEARCH.md](./MKDOCS_AUTH_RESEARCH.md)** - Research on MkDocs authentication solutions

#### Research & Planning
- **[RESEARCH_AND_DECISIONS_SUMMARY.md](./RESEARCH_AND_DECISIONS_SUMMARY.md)** - Summary of all research conducted

---

### 🚢 Deployment Documentation

#### Deployment Guides
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)** - Main deployment guide (root)
- **[DEPLOYMENT_READINESS_ANALYSIS.md](./DEPLOYMENT_READINESS_ANALYSIS.md)** - Pre-deployment verification checklist
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Deployment checklist and verification steps

---

### 🛠️ Tool Documentation

#### AI Tool Integration
- **[CLINE_CLI_README.md](./CLINE_CLI_README.md)** - Cline CLI documentation for AI-assisted development

---

## Directory Structure

```
homelab-docs/
├── README.md                          # Main project README
├── INSTALLATION.md                    # Setup instructions
├── CONTRIBUTING.md                    # Contribution guide
├── SECURITY.md                        # Security policy
├── TROUBLESHOOTING_PLAN.md            # Troubleshooting guide
├── DEPLOYMENT_GUIDE.md                # Main deployment guide
│
├── DOCS/                              # Organized documentation
│   ├── INDEX.md                       # This file
│   ├── Release/
│   │   ├── RELEASE.md
│   │   ├── BETA_RELEASE.md
│   │   ├── BETA_RELEASE_SUMMARY.md
│   │   └── MIGRATION_INSTRUCTIONS.md
│   ├── Phase2/
│   │   ├── PHASE_2_INDEX.md
│   │   ├── PHASE_2_IMPLEMENTATION_PLAN.md
│   │   ├── PHASE_2_EXECUTION_SUMMARY.md
│   │   ├── PHASE_2_QUICK_REFERENCE_GUIDE.md
│   │   ├── IMPLEMENTATION_COMPLETE.md
│   │   ├── PARALLAX_AND_HERO_GUIDE.md
│   │   ├── VIDEO_GIF_PARALLAX_GUIDE.md
│   │   ├── AUTHENTICATION_GATEWAY_PLAN.md
│   │   ├── MKDOCS_AUTH_RESEARCH.md
│   │   └── RESEARCH_AND_DECISIONS_SUMMARY.md
│   ├── Deployment/
│   │   ├── DEPLOYMENT_READINESS_ANALYSIS.md
│   │   └── DEPLOYMENT_CHECKLIST.md
│   └── Tools/
│       └── CLINE_CLI_README.md
│
├── docker/                            # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.mkdocs
│   ├── Dockerfile.ai-backend
│   ├── nginx.conf
│   └── htpasswd
│
├── docs/                              # MkDocs source files
│   ├── index.md
│   ├── javascripts/
│   ├── stylesheets/
│   └── [page content]
│
├── site/                              # Built static site (generated)
├── ai-backend/                        # FastAPI backend
├── scripts/                           # Deployment scripts
├── tests/                             # Unit and integration tests
├── uploads/                           # User uploads
├── logs/                              # Application logs
└── mkdocs.yml                         # MkDocs configuration
```

---

## Documentation by Topic

### Getting Started
Start here if you're new to the project:
1. Read [README.md](../README.md) for overview
2. Follow [INSTALLATION.md](../INSTALLATION.md) for setup
3. Review [SECURITY.md](../SECURITY.md) for security best practices

### Phase 2 Implementation (Parallax & Authentication)
If you're working on or understanding Phase 2:
1. Start with [PHASE_2_INDEX.md](./PHASE_2_INDEX.md) for overview
2. Read [PHASE_2_IMPLEMENTATION_PLAN.md](./PHASE_2_IMPLEMENTATION_PLAN.md) for details
3. Check [PARALLAX_AND_HERO_GUIDE.md](./PARALLAX_AND_HERO_GUIDE.md) for parallax system
4. Review [AUTHENTICATION_GATEWAY_PLAN.md](./AUTHENTICATION_GATEWAY_PLAN.md) for auth setup

### Video/GIF Parallax
For enhanced hero backgrounds:
- [VIDEO_GIF_PARALLAX_GUIDE.md](./VIDEO_GIF_PARALLAX_GUIDE.md) - Complete implementation guide

### Deployment
For production deployment:
1. Read [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) (root)
2. Run through [DEPLOYMENT_READINESS_ANALYSIS.md](./DEPLOYMENT_READINESS_ANALYSIS.md)
3. Follow [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

### Troubleshooting
- [TROUBLESHOOTING_PLAN.md](../TROUBLESHOOTING_PLAN.md) - Common issues and solutions

---

## Key Features Documented

### Authentication
- **Nginx HTTP Basic Auth** - Gateway-based authentication
- **Authelia Integration** - Professional SSO (Phase 2 optional)
- **OAuth2 Support** - External provider integration

### Hero Section
- **3-Layer Parallax System** - SVG-based visual depth
- **Full-Screen Immersive** - Viewport-filling hero experience
- **Video Background Support** - MP4/WebM animation alternatives
- **GIF Animation Support** - Simple animated background option

### Responsive Design
- **Mobile Optimized** - Works on 375px+ screens
- **Tablet Support** - Optimal layout on 768px+ screens
- **Desktop Excellence** - Full experience on 1920px+ screens

### Performance
- **RAF Throttling** - Smooth 60fps parallax
- **GPU Acceleration** - CSS transforms
- **Lazy Loading** - Images load on demand
- **Minified Assets** - Optimized CSS/JS

---

## File Organization Rules

### Root Directory (./)
**Keep only essential files:**
- Configuration files (mkdocs.yml, docker-compose.yml)
- Core README and setup guides
- Main license and security policy

### DOCS/ Directory
**All non-essential documentation:**
- Phase-specific implementation docs
- Release notes and changelogs
- Technical guides and research
- Tool documentation

### docs/ Directory (MkDocs)
**User-facing content:**
- Website pages and content
- Custom stylesheets and scripts
- Images and assets

### docker/ Directory
**Container and infrastructure:**
- Docker configuration
- Nginx setup
- Credentials (htpasswd)

### scripts/ Directory
**Automation and deployment:**
- Build scripts
- Deployment automation
- Health checks

---

## Cleanup Complete ✅

**Repository Streamlined:**
- ✅ Virtual environments removed (saved 440MB)
- ✅ Node modules removed (saved 26MB)
- ✅ Documentation organized (13 files → DOCS/)
- ✅ .gitignore updated
- ✅ Directory structure optimized
- ✅ Repository size: 131MB → optimized

**Repository Before**: 596MB  
**Repository After**: ~131MB  
**Saved**: ~465MB (78% reduction)

---

## Contributing

When adding new documentation:
1. **Core docs** (README, INSTALLATION, etc.) → Root directory
2. **Feature docs** (Phase 2, etc.) → DOCS/ subdirectory
3. **User content** (guides, pages) → docs/ directory
4. **Always update this INDEX.md** with new files

---

## Questions?

- 📖 Check the [README.md](../README.md)
- 🔧 Review [TROUBLESHOOTING_PLAN.md](../TROUBLESHOOTING_PLAN.md)
- 🚀 Follow [INSTALLATION.md](../INSTALLATION.md)
- 🔒 Review [SECURITY.md](../SECURITY.md)

---

**Last Updated**: December 1, 2025  
**Status**: ✅ Documentation Organized and Indexed

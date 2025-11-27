# Git Workflow Guide

## Overview

This guide covers the Git workflow for the Homelab Documentation Hub project, including branching strategies, commit conventions, and collaboration guidelines.

## Repository Structure

```
homelab-docs/
├── docs/                    # Documentation source files
│   ├── index.md           # Main documentation index
│   ├── getting-started.md # Getting started guide
│   ├── guides/            # User guides
│   ├── homelab/           # Homelab projects
│   ├── coursework/         # Educational content
│   └── about/             # Project information
├── ai-backend/             # AI backend service
│   ├── main.py            # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── app/               # Application modules
├── docker/                  # Docker configuration
│   ├── docker-compose.yml   # Development environment
│   ├── docker-compose.prod.yml # Production environment
│   ├── Dockerfile.mkdocs    # MkDocs container
│   ├── Dockerfile.ai-backend # AI backend container
│   ├── nginx.conf          # Nginx configuration
│   └── ssl/               # SSL certificates
├── scripts/                 # Utility scripts
│   ├── backup.sh           # Backup automation
│   ├── deploy.sh           # Deployment script
│   └── setup.sh            # Initial setup
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
├── .gitattributes         # Git attributes
├── mkdocs.yml             # MkDocs configuration
├── requirements.txt         # Python dependencies
├── README.md               # Project description
├── INSTALLATION.md         # Installation guide
└── LICENSE                 # Project license
```

## Branching Strategy

### Main Branches

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Individual feature branches
- **hotfix/***: Critical bug fixes
- **release/***: Release preparation

### Branch Naming Conventions

```bash
# Feature branches
feature/ai-content-generation
feature/docker-optimization
feature/search-enhancement

# Bugfix branches
hotfix/authentication-issue
hotfix/memory-leak
hotfix/docker-compose-errors

# Release branches
release/v1.0.0
release/v1.1.0
release/v2.0.0

# Development branches
develop/next-release
develop/staging
```

### Branch Protection Rules

```yaml
# main branch protection
- Require pull request reviews
- Require status checks to pass
- Require up-to-date branch
- Require conversation resolution
- Restrict force pushes

# develop branch protection
- Require status checks to pass
- Require up-to-date branch
- Allow force pushes with admin approval
```

## Commit Convention

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code formatting changes
- **refactor**: Code refactoring
- **test**: Test additions or changes
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: Continuous integration changes

### Examples

```bash
# Feature addition
feat(ai): Add OpenAI content generation
- Implement GPT-4 integration
- Add content generation endpoints
- Add rate limiting for AI features

# Bug fix
fix(auth): Resolve JWT token expiration issue
- Fix token validation logic
- Add proper error handling
- Update unit tests

# Documentation
docs(readme): Update installation instructions
- Add Docker deployment guide
- Update API documentation
- Add troubleshooting section

# Performance
perf(search): Optimize full-text search performance
- Implement search caching
- Add search result pagination
- Optimize database queries
```

## Pull Request Process

### Creating a Pull Request

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # Make your changes
   ```

2. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(your-feature): Add new functionality"
   ```

3. **Push to Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your feature branch
   - Target `develop` branch
   - Fill PR template

### Pull Request Template

```markdown
## Description
Brief description of changes and their purpose.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance tests conducted

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes introduced
- [ ] Performance impact considered
```

### Pull Request Review Process

1. **Automated Checks**
   - Code style validation
   - Unit test execution
   - Integration test execution
   - Security scan
   - Performance benchmark

2. **Code Review**
   - At least one maintainer approval
   - Check for potential issues
   - Verify code quality
   - Ensure tests are comprehensive

3. **Testing**
   - Manual testing on different platforms
   - Integration testing with other services
   - Performance testing
   - Security testing

## Release Process

### Version Management

```bash
# Version format: MAJOR.MINOR.PATCH
# Example: 1.0.0, 1.0.1, 1.1.0, 2.0.0
```

### Release Branch Creation

```bash
# Create release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update version files
echo "1.2.0" > VERSION
git add VERSION
git commit -m "chore: Bump version to 1.2.0"
```

### Release Tagging

```bash
# Tag the release
git tag -a v1.2.0 -m "Release version 1.2.0"

# Push tag to remote
git push origin v1.2.0

# Merge to main
git checkout main
git merge release/v1.2.0
git push origin main
```

### Release Notes Generation

```bash
# Generate release notes from commits
git log --since=v1.1.0 --oneline --format="%s" > release-notes.txt

# Create GitHub release with notes
gh release create v1.2.0 --title="Version 1.2.0" --notes-file=release-notes.txt
```

## Code Quality Standards

### Python Code Style

```bash
# Use Black for formatting
black --line-length 88 ai-backend/

# Use isort for imports
isort ai-backend/

# Use flake8 for linting
flake8 ai-backend/

# Use mypy for type checking
mypy ai-backend/
```

### Documentation Standards

- **Docstrings**: All functions and classes must have docstrings
- **Type Hints**: Use Python type hints for all functions
- **Examples**: Include usage examples in documentation
- **API Documentation**: Keep API documentation up to date
- **README Updates**: Update README for major changes

### Testing Standards

```python
# Unit tests using pytest
def test_ai_content_generation():
    """Test AI content generation functionality."""
    # Test implementation

# Integration tests
def test_ai_backend_integration():
    """Test AI backend integration."""
    # Test implementation

# Performance tests
def test_search_performance():
    """Test search performance benchmarks."""
    # Test implementation
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r ai-backend/requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=ai-backend --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker images
      run: |
        docker build -t homelab-docs-mkdocs -f docker/Dockerfile.mkdocs .
        docker build -t homelab-docs-ai-backend -f docker/Dockerfile.ai-backend .
        docker build -t homelab-docs-nginx -f docker/nginx.conf .
    
    - name: Push to registry
      run: |
        echo "Push to Docker registry"
```

### Quality Gates

```bash
# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Pre-push validation
npm test
python -m pytest tests/
black --check .
isort --check-only .
flake8 .
```

## Collaboration Guidelines

### Code Review Guidelines

1. **Be Constructive**: Focus on what can be improved, not just what's wrong
2. **Explain Why**: Provide reasoning for your suggestions
3. **Be Specific**: Give concrete examples and suggestions
4. **Ask Questions**: If you don't understand something, ask for clarification
5. **Be Respectful**: Maintain a professional and friendly tone

### Issue Reporting

```markdown
## Bug Report Template

### Environment
- OS: [e.g., Ubuntu 20.04, macOS 12.0, Windows 11]
- Docker version: [e.g., 20.10.8, 4.16.2]
- Browser: [e.g., Chrome 119, Firefox 119, Safari 16.2]
- Python version: [e.g., 3.10.6]

### Expected Behavior
[Describe what should happen]

### Actual Behavior
[Describe what actually happens]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Error Messages
[Include any error messages or logs]

### Additional Context
[Any additional information that might be helpful]
```

### Feature Request Template

```markdown
## Feature Request

### Problem Statement
[Describe the problem this feature would solve]

### Proposed Solution
[Describe your proposed solution]

### Alternatives Considered
[Describe any alternative solutions you've considered]

### Additional Context
[Any additional context or requirements]
```

## Troubleshooting

### Common Git Issues

#### Merge Conflicts

```bash
# Check for conflicts
git status
git diff --name-only

# Resolve conflicts
git merge feature-branch
# Edit conflicting files
git add .
git commit -m "resolve: Merge conflicts in feature-branch"
```

#### Push Issues

```bash
# Check remote URL
git remote -v

# Check branch tracking
git branch -vv

# Force push if necessary
git push --force-with-lease origin feature-branch
```

#### Submodule Issues

```bash
# Initialize submodules
git submodule update --init --recursive

# Update submodules
git submodule update --recursive

# Fix submodule issues
git submodule foreach git pull origin main
```

### Performance Issues

#### Large Repository Performance

```bash
# Use shallow clone for recent history
git clone --depth 1 https://github.com/0Reliance/Pozi-0reliance-Lab.git

# Use sparse checkout for specific directories
git sparse-checkout init --cone
git sparse-checkout set docs/ ai-backend/

# Optimize Git configuration
git config core.preloadindex true
git config core.fscache true
git config gc.auto 256
```

#### Binary File Issues

```bash
# Check for large files
git find . -type f -size +10M

# Configure Git LFS if needed
git lfs install
git lfs track "*.pdf"
git lfs track "*.zip"
git add .gitattributes
```

## Best Practices

### Daily Workflow

```bash
# Start with latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/new-feature

# Work in small, focused commits
git add .
git commit -m "feat(feature): Add initial implementation"

# Keep branch updated with main
git fetch origin
git rebase origin main
```

### Commit Hygiene

```bash
# Review changes before committing
git diff --staged
git status

# Write meaningful commit messages
git commit -m "type(scope): Clear and descriptive subject

# Keep commits atomic and focused
# One logical change per commit

# Review your own commits before pushing
git log --oneline -5
```

### Branch Management

```bash
# Delete merged feature branches
git branch -d feature/merged-feature

# Keep main clean and deployable
git checkout main
git pull origin main
git status

# Use develop for integration work
git checkout develop
git pull origin develop
```

## Git Hooks

### Pre-commit Hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# Check code formatting
python -m black --check ai-backend/
if [ $? -ne 0 ]; then
    echo "Code is not properly formatted"
    exit 1
fi

# Run tests
python -m pytest tests/
if [ $? -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi

echo "Pre-commit checks passed"
```

### Pre-push Hooks

```bash
#!/bin/sh
# .git/hooks/pre-push

echo "Running pre-push checks..."

# Run comprehensive tests
python -m pytest tests/ --cov=ai-backend

# Check code quality
flake8 ai-backend/
mypy ai-backend/

echo "Pre-push checks passed"
```

## Repository Maintenance

### Regular Cleanup

```bash
# Cleanup old branches
git branch -d feature/old-feature
git branch -d hotfix/old-fix

# Cleanup tags
git tag -d v1.0.0-old
git tag -d v1.1.0-beta

# Cleanup remote branches
git remote prune origin
```

### Repository Size Optimization

```bash
# Remove unnecessary files
echo "*.log" >> .gitignore
echo "*.tmp" >> .gitignore
echo "node_modules/" >> .gitignore

# Optimize Git history
git gc --prune=now --aggressive
git repack -a -d --depth=250 --window=250
```

### Backup Strategy

```bash
# Create backup script
cat > backup-repo.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups/homelab-docs"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup repository
git bundle create $BACKUP_DIR/homelab-docs-$DATE.bundle --all

# Backup configuration files
cp .env $BACKUP_DIR/env-$DATE.backup 2>/dev/null || true
cp mkdocs.yml $BACKUP_DIR/mkdocs-$DATE.backup

echo "Repository backed up to $BACKUP_DIR"
EOF

chmod +x backup-repo.sh
```

## Security Considerations

### Access Control

```bash
# Restrict access to sensitive branches
# Protect main and develop branches
# Require two-factor authentication for sensitive operations
# Use personal access tokens instead of passwords
```

### Commit Signing

```bash
# Configure GPG signing
git config commit.gpgsign true
git config user.signingkey your-email@example.com

# Sign commits
git commit -S -m "feat: Add new feature"

# Sign tags
git tag -s v1.0.0 -m "Release version 1.0.0"
```

### Credential Management

```bash
# Use credential helpers
git config --global credential.helper store
git config --global credential.helper 'cache --timeout=3600'

# Use SSH keys instead of passwords
# Add SSH key to GitHub/GitLab
git remote set-url origin git@github.com:your-org/homelab-docs.git
```

## Advanced Git Features

### Interactive Rebase

```bash
# Start interactive rebase
git rebase -i origin/feature-branch

# Common rebase actions:
# pick: Use commit
# reword: Edit commit message
# edit: Modify commit
# squash: Combine with previous commit
# fixup: Fix previous commit
# drop: Remove commit
```

### Bisect for Bug Finding

```bash
# Start bisect
git bisect start
git bisect bad HEAD
git bisect good v1.0.0

# Git will checkout commits, test, and narrow down the bad commit
# When bisect is done, you'll have the commit that introduced the bug
git bisect reset
```

### Cherry-picking Commits

```bash
# Cherry-pick specific commits
git cherry-pick <commit-hash>
git cherry-pick <start-hash>..<end-hash>

# Cherry-pick with modifications
git cherry-pick --edit <commit-hash>
```

## Migration and Upgrades

### Migrating from Other Systems

```bash
# Import from Subversion
git svn clone https://svn.example.com/repo trunk
git add .
git commit -m "Initial import from SVN"

# Import from Mercurial
git-hg clone https://hg.example.com/repo
cd repo
git remote add origin https://github.com/your-org/repo.git
git push origin master
```

### Upgrading Git Versions

```bash
# Check current Git version
git --version

# Upgrade Git (Linux)
sudo apt update
sudo apt install git

# Upgrade Git (macOS)
brew upgrade git

# Upgrade Git (Windows)
# Download from git-scm.com
```

## Glossary

- **Branch**: Independent line of development
- **Commit**: Snapshot of changes at a point in time
- **Merge**: Combine changes from different branches
- **Pull Request**: Proposed changes to be merged
- **Repository**: Complete project with all history
- **Tag**: Reference point in repository history
- **Upstream**: Original repository you forked from
- **Origin**: Your remote repository
- **Head**: Latest commit on a branch
- **Master/Main**: Primary development branch
- **Rebase**: Reapply commits on top of another branch

---

*This Git workflow guide provides comprehensive guidelines for collaborative development on the Homelab Documentation Hub project.*

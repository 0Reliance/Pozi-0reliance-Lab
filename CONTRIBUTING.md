# Contributing to Homelab Documentation Hub

Thank you for your interest in contributing to the Homelab Documentation Hub! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** for local development
- **Docker & Docker Compose** for containerized development
- **Git** for version control
- **GitHub account** for pull requests

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   git clone https://github.com/your-username/homelab-docs.git
   cd homelab-docs
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r ai-backend/requirements.txt
   
   # Install development dependencies
   pip install black flake8 isort mypy bandit safety pytest
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit with your configuration (use placeholder values for development)
   nano .env
   ```

4. **Start Development Services**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose -f docker/docker-compose.yml up --build
   
   # Or run services individually
   mkdocs serve --dev-addr=0.0.0.0:8000 &
   python ai-backend/main.py &
   ```

## 📝 Contribution Guidelines

### Code Style and Quality

We use automated tools to maintain code quality:

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy ai-backend/

# Security checks
bandit -r ai-backend/
safety check
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks:

```bash
pre-commit install
```

### Testing

Run tests before submitting:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai-backend --cov-report=html

# Run specific test categories
pytest tests/test_basic.py -v
pytest tests/integration/ -v -m integration
```

## 🎯 Types of Contributions

### 📚 Documentation

- **New content**: Add new documentation pages
- **Updates**: Improve existing documentation
- **Fixes**: Correct errors or outdated information
- **Translation**: Help translate documentation

#### Adding New Documentation

1. Create markdown files in appropriate `docs/` subdirectories
2. Update `mkdocs.yml` navigation
3. Test with `mkdocs serve`
4. Submit pull request

#### Documentation Structure

```
docs/
├── homelab/          # Homelab projects
├── coursework/       # Academic content
├── guides/          # How-to guides
├── development/     # Developer docs
└── about/           # Project info
```

### 🐛 Bug Reports

#### Before Creating Issues

- Check existing issues for duplicates
- Verify the issue still exists in the latest version
- Test with a clean environment

#### Creating Bug Reports

Use the provided bug report template:

```markdown
**Bug Description**
Brief description of the issue

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9]
- Browser: [e.g., Chrome 91]

**Additional Context**
Any other relevant information
```

### ✨ Feature Requests

#### Before Requesting Features

- Check existing issues and roadmap
- Consider if it fits the project scope
- Think about implementation complexity

#### Creating Feature Requests

```markdown
**Feature Description**
Clear description of the proposed feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should the feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

### 🔧 Code Contributions

#### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   pre-commit run --all-files
   
   # Test Docker build
   docker-compose build
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

#### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```bash
feat: add AI-powered content generation
fix: resolve navigation menu overlap
docs: update API documentation
test: add integration tests for Docker services
```

## 🔒 Security Considerations

### Handling Sensitive Information

- **Never commit** API keys, passwords, or secrets
- Use environment variables for sensitive configuration
- Follow security best practices in code

### Security Issues

For security vulnerabilities:
- **Do not** open public issues
- Email: security@homelab-docs.com
- Use GitHub's private security advisory feature

## 📊 Review Process

### Pull Request Review

All pull requests go through:

1. **Automated Checks**
   - Code quality (Black, flake8, mypy)
   - Security scans (Bandit, Safety)
   - Tests (pytest)
   - Docker build verification

2. **Code Review**
   - At least one maintainer approval
   - Focus on functionality, security, and maintainability
   - Discussion and iteration as needed

3. **Integration Testing**
   - Full integration test suite
   - Docker container verification
   - Documentation build validation

### Merge Requirements

- All automated checks must pass
- At least one maintainer approval
- Documentation updated (if applicable)
- Tests added (for new functionality)

## 🏗️ Project Structure

```
homelab-docs/
├── .github/                # GitHub workflows and templates
│   └── workflows/         # CI/CD pipelines
├── docs/                   # Documentation content
├── ai-backend/             # Python backend service
├── docker/                 # Docker configuration
├── scripts/                # Utility scripts
├── tests/                  # Test suites
├── requirements.txt        # Python dependencies
├── mkdocs.yml             # MkDocs configuration
├── .env.example           # Environment template
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

## 🎯 Areas of Contribution

### High Priority

1. **Documentation**
   - Homelab setup guides
   - Security best practices
   - Troubleshooting guides

2. **Testing**
   - Unit tests for AI backend
   - Integration tests
   - Performance tests

3. **Security**
   - Security audits
   - Vulnerability fixes
   - Security feature implementations

### Medium Priority

1. **Features**
   - AI-powered content suggestions
   - Advanced search capabilities
   - User authentication systems

2. **Performance**
   - Optimization improvements
   - Caching strategies
   - Load balancing

### Low Priority

1. **Enhancements**
   - UI/UX improvements
   - Additional themes
   - Plugin integrations

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Use inclusive language
- Focus on constructive feedback
- Help others learn and grow

### Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Documentation**: Check existing docs first
- **Community**: Join our [Discord server](https://discord.gg/homelab-docs)

## 📋 Development Resources

### Useful Tools

- **Development**: VS Code, PyCharm, vim
- **Testing**: pytest, coverage, tox
- **Code Quality**: Black, flake8, isort, mypy
- **Security**: Bandit, Safety, Trivy
- **Documentation**: MkDocs, Material theme

### Learning Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Testing Guide](https://docs.pytest.org/)

## 🎉 Recognition

### Contributors

All contributors are recognized:

- **Hall of Fame**: Listed in README
- **Release Notes**: Mentioned in changelog
- **Community Badges**: Special GitHub badges
- **Annual Awards**: Top contributors recognition

### Attribution

- Code contributions attributed in commit history
- Documentation contributions credited in footers
- Special thanks in release announcements

## 📞 Contact

### Project Maintainers

- **Lead Maintainer**: [GitHub Username](https://github.com/lead-maintainer)
- **Security Lead**: security@homelab-docs.com
- **Community Manager**: community@homelab-docs.com

### Communication Channels

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Discord**: [Community Server](https://discord.gg/homelab-docs)
- **Email**: info@homelab-docs.com

---

## 🙏 Thank You

Thank you for contributing to the Homelab Documentation Hub! Your contributions help make this project better for everyone.

Whether you're fixing a typo, adding a new feature, or helping someone in the community, your efforts are appreciated and make a real difference.

Happy contributing! 🚀

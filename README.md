# Homelab Documentation Hub

![Homelab Documentation Hub](docs/images/logo.png)

🏠 **A comprehensive AI-powered platform for managing homelab documentation with intelligent content generation, advanced search, and collaborative features.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-org/homelab-docs/blob/main/LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)](https://fastapi.tiangolo.com/)
[![MkDocs](https://img.shields.io/badge/MkDocs-Material-9F758.svg)](https://www.mkdocs.org/)

## 🌟 Features

### 🤖 AI-Powered Documentation
- **Intelligent Content Generation**: OpenAI integration for automated documentation creation
- **Smart Search**: AI-enhanced search with contextual understanding
- **Content Suggestions**: Automatic content recommendations and improvements
- **Code Generation**: AI-assisted code examples and configuration snippets

### 📚 Comprehensive Documentation Management
- **Multi-Format Support**: Markdown, code blocks, tables, and mathematical notation
- **Version Control**: Git integration with automatic history tracking
- **Live Preview**: Real-time documentation rendering and updates
- **Collaborative Editing**: Multi-user support with conflict resolution

### 🔍 Advanced Search & Navigation
- **Full-Text Search**: Instant search across all documentation
- **Category Filtering**: Browse by topic, category, or tag
- **Smart Suggestions**: AI-powered content recommendations
- **Bookmark System**: Save and organize important sections

### 🛠️ Homelab Integration
- **Network Documentation**: Complete network topology and configuration guides
- **Service Management**: Document and manage homelab services
- **Hardware Tracking**: Keep track of equipment and configurations
- **Automated Backups**: Regular documentation backup and versioning

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/homelab-docs.git
cd homelab-docs

# Copy environment configuration
cp .env.example .env

# Edit environment variables
nano .env  # Add your OpenAI API key and other settings

# Start all services
docker-compose -f docker/docker-compose.yml up --build -d

# Access the application
# Web Interface: http://localhost
# Admin Panel: http://localhost/admin
# API Documentation: http://localhost:8001/docs
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/your-org/homelab-docs.git
cd homelab-docs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
cd ai-backend
pip install -r requirements.txt
cd ..

# Start services
mkdocs serve --dev-addr=0.0.0.0:8000 &  # Documentation
python ai-backend/main.py &                     # AI Backend
```

## 📖 Documentation

### For Users
- [📚 Getting Started Guide](docs/guides/getting-started.md)
- [🔧 Installation Instructions](INSTALLATION.md)
- [🎯 Best Practices](docs/guides/best-practices.md)
- [❓ Troubleshooting](docs/guides/troubleshooting.md)
- [🔒 Security Guide](docs/guides/security.md)

### For Developers
- [🛠️ API Reference](docs/api.md)
- [🤖 AI Backend Guide](docs/ai-backend.md)
- [🔧 Development Setup](docs/development/setup.md)
- [📝 Contributing Guidelines](docs/about/contributing.md)
- [🚀 Deployment Guide](docs/development/deployment.md)

### For SysAdmins
- [🏠 Homelab Projects](docs/homelab/index.md)
- [🌐 Network Setup](docs/homelab/network/index.md)
- [💾 Storage Solutions](docs/homelab/storage/index.md)
- [🖥️ Virtualization](docs/homelab/virtualization/index.md)
- [📊 Monitoring](docs/homelab/monitoring/index.md)

### For Students
- [🎓 CS Coursework](docs/coursework/index.md)
- [📊 Data Structures](docs/coursework/cs/data-structures.md)
- [⚙️ Algorithms](docs/coursework/cs/algorithms.md)
- [🗄️ Databases](docs/coursework/cs/databases.md)
- [🌐 Networking](docs/coursework/networking/index.md)
- [🖥️ System Administration](docs/coursework/sysadmin/index.md)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser                     │
│               ┌───────────────────────┐           │
│               │    Nginx             │           │
│               │  (Reverse Proxy)      │           │
│               └─────────┬─────────────┘           │
│                         │                         │
│               ┌─────────┴─────────────┐           │
│               │   MkDocs               │   AI      │
│               │ (Documentation)         │ Backend  │
│               └─────────┬─────────────┘           │
│                         │                         │
│               ┌─────────┴─────────────┐           │
│               │     Redis               │           │
│               │  (Session/Caching)       │           │
│               └───────────────────────────┘           │
│                                                       │
┌───────────────────────┐              ┌─────────────────────────┐ │
│   File System       │              │   Docker Containers     │ │
│   (Documentation)  │              │   (Service Orchestration)│ │
└───────────────────────┘              └─────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
AZURE_OPENAI_API_KEY=your_azure_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Application Settings
SECRET_KEY=your_secret_key_here
DOMAIN=localhost
REQUIRE_AUTH=false

# Database
REDIS_URL=redis://localhost:6379/0

# File Storage
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760

# Security
JWT_SECRET_KEY=your_jwt_secret
FORCE_HTTPS=false
```

### AI Provider Configuration

The platform supports multiple AI providers:

```bash
# OpenAI (Default)
OPENAI_API_KEY=sk-...

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Hugging Face
HUGGINGFACE_API_KEY=your_key

# Custom API
CUSTOM_API_URL=https://your-api.com
CUSTOM_API_KEY=your_key
```

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 10GB+ disk space

### Quick Start
```bash
# Clone and setup
git clone https://github.com/your-org/homelab-docs.git
cd homelab-docs

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Deploy
docker-compose -f docker/docker-compose.yml up -d

# Verify deployment
curl http://localhost
```

### Services

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| nginx   | nginx | 80,443 | Reverse proxy and static serving |
| mkdocs  | python:3.11-slim | 8000 | Documentation server |
| ai-backend | python:3.11-slim | 8001 | AI and API services |
| redis   | redis:7-alpine | 6379 | Session and caching |

### Production Deployment

For production environments:

```bash
# 1. Generate SSL certificates
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/privkey.pem -out docker/ssl/fullchain.pem \
  -subj "/C=US/ST=State/L=City/O=Homelab/CN=yourdomain.com"

# 2. Configure production environment
cp .env.example .env
# Edit with production settings

# 3. Deploy with SSL
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 🤖 AI Features

### Content Generation
- **Documentation Creation**: Generate comprehensive guides and tutorials
- **Code Examples**: Create working code snippets and examples
- **Configuration Files**: Generate configuration templates and examples
- **Best Practices**: Suggest improvements and optimizations

### Smart Search
- **Natural Language**: Search using natural language queries
- **Context Awareness**: Understand user intent and context
- **Result Ranking**: Intelligent result ranking and filtering
- **Auto-Suggestions**: Provide relevant suggestions based on search

### Learning Assistant
- **Interactive Chat**: AI-powered chat for documentation help
- **Code Explanation**: Explain complex code and configurations
- **Troubleshooting**: AI-assisted problem diagnosis and resolution
- **Knowledge Base**: Build and maintain internal knowledge base

## 📊 API Documentation

### Core Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| GET    | `/api/health` | Health check | No |
| POST   | `/api/generate` | Generate content | Yes |
| GET    | `/api/search` | Search documentation | Yes |
| POST   | `/api/upload` | Upload file | Yes |
| GET    | `/api/files` | List files | Yes |

### Authentication
```bash
# JWT Token Authentication
curl -H "Authorization: Bearer <token>" http://localhost:8001/api/files

# API Key Authentication
curl -H "X-API-Key: <api_key>" http://localhost:8001/search
```

### Python Client
```python
import requests

# Initialize client
client = HomelabDocsAPI(
    base_url="http://localhost:8001",
    api_key="your_api_key"
)

# Generate content
result = client.generate_content(
    topic="network setup",
    content_type="guide",
    style="technical"
)

# Search documentation
results = client.search(
    query="docker networking",
    filters=["guides", "tutorials"]
)
```

## 🧪 Development

### Local Setup
```bash
# Clone repository
git clone https://github.com/your-org/homelab-docs.git
cd homelab-docs

# Setup Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r ai-backend/requirements.txt

# Setup pre-commit hooks
pre-commit install
```

### Project Structure
```
homelab-docs/
├── docs/                    # Documentation files
├── ai-backend/              # AI backend service
├── docker/                   # Docker configuration
├── scripts/                  # Utility scripts
├── tests/                    # Test files
├── .env.example             # Environment template
├── requirements.txt           # Python dependencies
└── mkdocs.yml              # MkDocs configuration
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_ai_backend.py

# Run with coverage
pytest --cov=ai-backend tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📦 System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.0GHz+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 10GB free space
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+

### Recommended Requirements
- **CPU**: 4 cores, 3.0GHz+
- **RAM**: 8GB (16GB for production)
- **Storage**: 20GB+ SSD
- **Network**: Stable internet connection

### Software Requirements
- **Docker**: 20.10+ (optional but recommended)
- **Python**: 3.8+ (for local development)
- **Git**: 2.0+ (for version control)
- **Node.js**: 16+ (for frontend development)

## 🔒 Security

### Authentication
- **Multi-factor Authentication**: Support for 2FA
- **JWT Tokens**: Secure token-based authentication
- **Session Management**: Secure session handling with Redis
- **Role-based Access**: Different access levels for different users

### Data Protection
- **Encryption**: Data encryption at rest and in transit
- **Access Control**: Fine-grained access control
- **Audit Logging**: Comprehensive audit trail
- **Backup Encryption**: Encrypted backups for data protection

### Network Security
- **SSL/TLS**: HTTPS for all communications
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive input validation
- **CSRF Protection**: Cross-site request forgery protection

## 📈 Monitoring and Analytics

### Health Monitoring
```bash
# Service health check
curl http://localhost:8001/health

# Docker container health
docker-compose -f docker/docker-compose.yml ps

# Resource usage monitoring
docker stats
```

### Logging
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: Debug, Info, Warning, Error levels
- **Log Rotation**: Automatic log rotation to prevent disk issues
- **Centralized Logging**: Centralized log management

### Performance Metrics
- **Response Time**: Track API response times
- **Throughput**: Monitor request throughput
- **Error Rates**: Track error rates and types
- **Resource Usage**: Monitor CPU, memory, and disk usage

## 🤝 Contributing

We welcome contributions of all types! Please see our [Contributing Guidelines](docs/about/contributing.md) for details.

### How to Contribute
1. **Report Issues**: Found a bug? [Report it here](https://github.com/your-org/homelab-docs/issues)
2. **Submit Pull Requests**: Fixed a bug or added a feature? [Submit a PR](https://github.com/your-org/homelab-docs/pulls)
3. **Improve Documentation**: Help us improve our documentation
4. **Share Ideas**: Have an idea for a new feature? [Let us know](https://github.com/your-org/homelab-docs/discussions)

### Development Areas
- 🤖 **AI Backend**: Python, FastAPI, OpenAI integration
- 📚 **Documentation**: MkDocs, Material theme
- 🐳 **DevOps**: Docker, CI/CD, monitoring
- 🎨 **Frontend**: HTML, CSS, JavaScript
- 🧪 **Testing**: Python, pytest, integration tests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MkDocs](https://www.mkdocs.org/) for the excellent documentation generator
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) for the beautiful theme
- [FastAPI](https://fastapi.tiangolo.com/) for the modern web framework
- [OpenAI](https://openai.com/) for the powerful AI capabilities
- [Docker](https://www.docker.com/) for containerization platform

## 📞 Support

### Getting Help
- 📖 [Documentation](https://homelab-docs.readthedocs.io/)
- 🐛 [Issues](https://github.com/your-org/homelab-docs/issues)
- 💬 [Discussions](https://github.com/your-org/homelab-docs/discussions)
- 📧 [Email](mailto:support@homelab-docs.com)

### Community
- [Discord Server](https://discord.gg/homelab-docs)
- [Reddit](https://reddit.com/r/homelab-docs)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/homelab-docs)

## 🗺️ Roadmap

### Upcoming Features
- [ ] **Multi-language Support**: Documentation in multiple languages
- [ ] **Mobile App**: Native mobile applications
- [ ] **Offline Mode**: Offline documentation access
- [ ] **Advanced AI**: More sophisticated AI features
- [ ] **Integration Hub**: Integration with more homelab tools

### Planned Enhancements
- [ ] **Performance Optimization**: Faster search and content generation
- [ ] **UI Improvements**: Enhanced user interface
- [ ] **Security Features**: Additional security measures
- [ ] **API Extensions**: More API endpoints and features

---

<div align="center">

**⭐ Star this repository if it helps you!**

Made with ❤️ by the Homelab Documentation Team

[![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-005571.svg)](https://fastapi.tiangolo.com/)
[![Powered by MkDocs](https://img.shields.io/badge/Powered%20by-MkDocs-1987d1.svg)](https://www.mkdocs.org/)

</div>

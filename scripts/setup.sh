#!/bin/bash

# Homelab Documentation Hub - Setup Script
# Automates environment validation and initial deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (not recommended)
check_root_user() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available memory (minimum 2GB recommended)
    TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
    if [[ $TOTAL_MEM -lt 2048 ]]; then
        log_warning "System has less than 2GB RAM. Performance may be limited."
    fi
    
    # Check available disk space (minimum 5GB)
    AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
    if [[ $AVAILABLE_SPACE -lt 5242880 ]]; then  # 5GB in KB
        log_error "Insufficient disk space. At least 5GB required."
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Validate environment variables
validate_environment() {
    log_info "Validating environment configuration..."
    
    local env_file=".env"
    local env_example=".env.example"
    local errors=0
    
    # Check if .env exists
    if [[ ! -f "$env_file" ]]; then
        if [[ -f "$env_example" ]]; then
            log_info "Creating .env from .env.example..."
            cp "$env_example" "$env_file"
            log_warning "Please edit .env file with your configuration before proceeding"
        else
            log_error "Neither .env nor .env.example found"
            exit 1
        fi
    fi
    
    # Source environment variables
    source "$env_file"
    
    # Check required variables
    local required_vars=(
        "OPENAI_API_KEY"
        "SECRET_KEY"
    )
    
    local optional_vars=(
        "GIT_REPO_URL"
        "GIT_BRANCH"
    )
    
    # Validate required variables
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            errors=$((errors + 1))
        fi
    done
    
    # Validate optional variables
    for var in "${optional_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_warning "Optional environment variable $var is not set"
        fi
    done
    
    # Validate OpenAI API key format
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        if [[ ! $OPENAI_API_KEY =~ ^sk- ]]; then
            log_error "Invalid OpenAI API key format"
            errors=$((errors + 1))
        fi
    fi
    
    # Validate secret key
    if [[ -n "${SECRET_KEY:-}" ]]; then
        if [[ ${#SECRET_KEY} -lt 16 ]]; then
            log_error "SECRET_KEY should be at least 16 characters long"
            errors=$((errors + 1))
        fi
    fi
    
    if [[ $errors -gt 0 ]]; then
        log_error "Environment validation failed with $errors errors"
        log_error "Please fix the above issues and run the script again"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Setup directory structure
setup_directories() {
    log_info "Setting up directory structure..."
    
    local directories=(
        "logs"
        "backups"
        "uploads"
        "data/redis"
        "data/mkdocs"
        "ssl"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done
    
    # Set proper permissions
    chmod 755 uploads logs backups
    chmod 700 ssl
    
    log_success "Directory structure setup completed"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    log_info "Setting up SSL certificates..."
    
    local ssl_dir="ssl"
    local cert_file="$ssl_dir/cert.pem"
    local key_file="$ssl_dir/key.pem"
    
    if [[ -f "$cert_file" && -f "$key_file" ]]; then
        log_info "SSL certificates already exist"
        return
    fi
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$key_file" \
        -out "$cert_file" \
        -subj "/C=US/ST=State/L=City/O=Homelab/CN=localhost" \
        2>/dev/null
    
    log_success "SSL certificates generated"
    log_warning "These are self-signed certificates. For production, use proper certificates"
}

# Build Docker images
build_docker_images() {
    log_info "Building Docker images..."
    
    cd docker
    
    # Build MkDocs image
    log_info "Building MkDocs image..."
    docker build -f Dockerfile.mkdocs -t homelab-docs-mkdocs:latest .. || {
        log_error "Failed to build MkDocs image"
        exit 1
    }
    
    # Build AI Backend image
    log_info "Building AI Backend image..."
    docker build -f Dockerfile.ai-backend -t homelab-docs-ai-backend:latest .. || {
        log_error "Failed to build AI Backend image"
        exit 1
    }
    
    cd ..
    log_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    cd docker
    
    # Stop existing services
    docker-compose down 2>/dev/null || true
    
    # Start services
    if ! docker-compose up -d; then
        log_error "Failed to start services"
        exit 1
    fi
    
    cd ..
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_service_health
    
    log_success "Services deployed successfully"
}

# Check service health
check_service_health() {
    log_info "Checking service health..."
    
    local services=(
        "mkdocs:8000"
        "ai-backend:8001"
        "nginx:80"
        "redis:6379"
    )
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        local all_healthy=true
        
        for service in "${services[@]}"; do
            local service_name=$(echo "$service" | cut -d: -f1)
            local port=$(echo "$service" | cut -d: -f2)
            
            if curl -f "http://localhost:$port/health" >/dev/null 2>&1 || \
               curl -f "http://localhost:$port/" >/dev/null 2>&1 || \
               nc -z localhost "$port" 2>/dev/null; then
                log_success "$service_name is healthy"
            else
                log_warning "$service_name is not ready yet"
                all_healthy=false
            fi
        done
        
        if [[ "$all_healthy" == "true" ]]; then
            log_success "All services are healthy"
            return
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    log_error "Some services failed to become healthy"
    docker-compose logs
    exit 1
}

# Setup backup automation
setup_backups() {
    log_info "Setting up backup automation..."
    
    local backup_script="scripts/backup.sh"
    
    if [[ ! -f "$backup_script" ]]; then
        log_error "Backup script not found at $backup_script"
        return
    fi
    
    # Make backup script executable
    chmod +x "$backup_script"
    
    # Add to crontab (if available)
    if command -v crontab &> /dev/null; then
        # Create cron entry for daily backup at 2 AM
        local cron_entry="0 2 * * * cd $(pwd) && ./scripts/backup.sh daily"
        
        # Add to crontab if not already present
        if ! crontab -l 2>/dev/null | grep -q "backup.sh"; then
            (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
            log_success "Backup automation added to crontab"
        else
            log_info "Backup automation already exists in crontab"
        fi
    else
        log_warning "crontab not available. Manual backup setup required"
    fi
}

# Display deployment summary
display_summary() {
    log_success "=== Deployment Summary ==="
    echo
    echo "🚀 Homelab Documentation Hub is now running!"
    echo
    echo "📚 Documentation Site: http://localhost"
    echo "🤖 AI Backend API: http://localhost:8001"
    echo "🔍 Health Check: http://localhost:8001/health"
    echo "📊 API Docs: http://localhost:8001/docs"
    echo
    echo "🔧 Management Commands:"
    echo "  View logs:       docker-compose logs -f"
    echo "  Stop services:   docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  Update services:  docker-compose pull && docker-compose up -d"
    echo
    echo "📁 Important Directories:"
    echo "  Documentation:   ./docs"
    echo "  Uploads:         ./uploads"
    echo "  Backups:         ./backups"
    echo "  Logs:            ./logs"
    echo
    echo "🔑 Environment Configuration:"
    echo "  Edit .env file to modify settings"
    echo "  Restart services after changes: docker-compose restart"
    echo
    log_success "Setup completed successfully!"
}

# Main execution
main() {
    echo "🚀 Homelab Documentation Hub - Setup Script"
    echo "=============================================="
    echo
    
    check_root_user
    check_system_requirements
    validate_environment
    setup_directories
    generate_ssl_certificates
    build_docker_images
    deploy_services
    setup_backups
    display_summary
}

# Handle script interruption
trap 'log_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@"

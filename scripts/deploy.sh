#!/bin/bash

# Homelab Documentation Hub - Deployment Script
# This script handles automated deployment for different environments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="development"
DOMAIN="localhost"
PORT="80"
SSL_PORT="443"
SKIP_TESTS=false
SKIP_BUILD=false
BACKUP=true
DRY_RUN=false

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Log file
LOG_FILE="$PROJECT_DIR/deployment.log"

# Functions
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}" | tee -a "$LOG_FILE"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV   Set environment (development|staging|production) [default: development]"
    echo "  -d, --domain DOMAIN     Set domain [default: localhost]"
    echo "  -p, --port PORT         Set HTTP port [default: 80]"
    echo "  -s, --ssl-port PORT     Set HTTPS port [default: 443]"
    echo "  -t, --skip-tests        Skip tests"
    echo "  -b, --skip-build       Skip Docker build"
    echo "  --no-backup            Skip backup"
    echo "  --dry-run               Show commands without executing"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Deploy to development"
    echo "  $0 -e production -d example.com  # Deploy to production with domain"
    echo "  $0 -e staging --no-backup       # Deploy to staging without backup"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -s|--ssl-port)
                SSL_PORT="$2"
                shift 2
                ;;
            -t|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -b|--skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --no-backup)
                BACKUP=false
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if running from project directory
    if [[ ! -f "$PROJECT_DIR/docker-compose.yml" ]]; then
        error "docker-compose.yml not found. Please run from project directory."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
    fi
    
    success "Prerequisites check passed"
}

# Create backup
create_backup() {
    if [[ "$BACKUP" == "false" ]]; then
        info "Skipping backup"
        return
    fi
    
    info "Creating backup..."
    
    BACKUP_DIR="$PROJECT_DIR/backups"
    BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="homelab-docs-backup-$BACKUP_DATE"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup Docker volumes
    docker run --rm \
        -v homelab-docs_ai_uploads:/data \
        -v "$BACKUP_DIR:/backup" \
        alpine tar czf "/backup/$BACKUP_NAME-uploads.tar.gz" -C /data . 2>/dev/null || true
    
    # Backup configuration files
    tar -czf "$BACKUP_DIR/$BACKUP_NAME-configs.tar.gz" \
        .env docker/ scripts/ mkdocs.yml 2>/dev/null || true
    
    # Backup database
    docker run --rm \
        -v homelab-docs_redis:/data \
        -v "$BACKUP_DIR:/backup" \
        alpine tar czf "/backup/$BACKUP_NAME-redis.tar.gz" -C /data . 2>/dev/null || true
    
    success "Backup created: $BACKUP_DIR/$BACKUP_NAME"
}

# Stop existing services
stop_services() {
    info "Stopping existing services..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would run: docker-compose -f docker/docker-compose.yml down"
        return
    fi
    
    cd "$PROJECT_DIR"
    docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
    docker-compose -f docker/docker-compose.prod.yml down 2>/dev/null || true
    
    success "Services stopped"
}

# Build Docker images
build_images() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        info "Skipping Docker build"
        return
    fi
    
    info "Building Docker images..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would run: docker-compose -f docker/docker-compose.yml build"
        return
    fi
    
    cd "$PROJECT_DIR"
    docker-compose -f docker/docker-compose.yml build
    
    success "Docker images built"
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        info "Skipping tests"
        return
    fi
    
    info "Running tests..."
    
    cd "$PROJECT_DIR"
    
    # Run Python tests
    if docker run --rm -v "$PROJECT_DIR":/app -w /app python:3.11-slim \
        python -m pip install -q pytest >/dev/null 2>&1; then
        docker run --rm -v "$PROJECT_DIR":/app -w /app python:3.11-slim \
            python -m pytest ai-backend/tests/ -v --color=yes
    else
        warning "pytest not available, skipping Python tests"
    fi
    
    # Test Docker containers
    docker-compose -f docker/docker-compose.yml config
    
    success "Tests completed"
}

# Deploy services
deploy_services() {
    info "Deploying to $ENVIRONMENT environment..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would deploy services"
        return
    fi
    
    cd "$PROJECT_DIR"
    
    # Set environment-specific variables
    if [[ "$ENVIRONMENT" == "production" ]]; then
        export COMPOSE_FILE="docker-compose.prod.yml"
        export DOMAIN="$DOMAIN"
    else
        export COMPOSE_FILE="docker-compose.yml"
    fi
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:$PORT/health >/dev/null 2>&1; then
            break
        fi
        
        if curl -f http://localhost:8001/health >/dev/null 2>&1; then
            break
        fi
        
        info "Attempt $attempt/$max_attempts: Waiting for services..."
        sleep 5
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        warning "Services may not be fully healthy"
    else
        success "Services are healthy and ready"
    fi
}

# Verify deployment
verify_deployment() {
    info "Verifying deployment..."
    
    # Check if services are running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        error "Services are not running"
    fi
    
    # Check main service
    if ! curl -f http://localhost:$PORT >/dev/null 2>&1; then
        error "Main service is not accessible"
    fi
    
    # Check AI backend
    if ! curl -f http://localhost:8001/health >/dev/null 2>&1; then
        warning "AI backend may not be accessible"
    fi
    
    success "Deployment verification completed"
}

# Show deployment info
show_deployment_info() {
    info "Deployment Information:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Domain: $DOMAIN"
    echo "  HTTP Port: $PORT"
    echo "  HTTPS Port: $SSL_PORT"
    echo "  Docker Compose File: $COMPOSE_FILE"
    echo ""
    
    info "Service URLs:"
    echo "  Main Site: http://$DOMAIN:$PORT"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo "  HTTPS Site: https://$DOMAIN:$SSL_PORT"
    fi
    echo "  AI Backend: http://$DOMAIN:8001"
    echo "  API Documentation: http://$DOMAIN:8001/docs"
    echo ""
    
    if [[ -f "$PROJECT_DIR/backups" ]]; then
        echo "Latest backup:"
        ls -lt "$PROJECT_DIR/backups" | head -1
    fi
}

# Cleanup function
cleanup() {
    info "Cleaning up..."
    
    # Remove unused Docker images
    docker image prune -f >/dev/null 2>&1 || true
    
    # Remove unused Docker volumes
    docker volume prune -f >/dev/null 2>&1 || true
    
    success "Cleanup completed"
}

# Main execution
main() {
    # Parse command line arguments
    parse_args "$@"
    
    # Log deployment start
    log "Starting deployment to $ENVIRONMENT environment"
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    create_backup
    
    # Stop existing services
    stop_services
    
    # Build images
    build_images
    
    # Run tests
    run_tests
    
    # Deploy services
    deploy_services
    
    # Verify deployment
    verify_deployment
    
    # Show deployment info
    show_deployment_info
    
    success "Deployment to $ENVIRONMENT completed successfully!"
}

# Trap signals for cleanup
trap cleanup EXIT

# Execute main function
main "$@"

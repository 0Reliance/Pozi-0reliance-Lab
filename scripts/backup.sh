#!/bin/bash

# Homelab Documentation Hub - Backup Script
# Automated backup solution for data and configuration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/logs/backup.log"
RETENTION_DAYS=30
COMPRESSION_LEVEL=6

# Logging functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Create backup directory
create_backup_dir() {
    local backup_type="${1:-daily}"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/$backup_type/$timestamp"
    
    mkdir -p "$backup_path"
    echo "$backup_path"
}

# Backup Docker volumes
backup_docker_volumes() {
    local backup_path="$1"
    log_info "Backing up Docker volumes..."
    
    cd "$PROJECT_DIR/docker"
    
    # Get list of volumes
    local volumes=$(docker-compose config --volumes 2>/dev/null || echo "")
    
    if [[ -z "$volumes" ]]; then
        # Fallback: backup common volume names
        volumes="homelab-docs_ai_uploads homelab-docs_redis_data mkdocs_site redis_data ai_uploads"
    fi
    
    for volume in $volumes; do
        if docker volume inspect "$volume" &>/dev/null; then
            log_info "Backing up volume: $volume"
            
            # Create backup using temporary container
            docker run --rm \
                -v "$volume":/data:ro \
                -v "$backup_path":/backup \
                alpine tar czf "/backup/volume_${volume}.tar.gz" -C /data . || {
                log_warning "Failed to backup volume: $volume"
            }
        else
            log_warning "Volume not found: $volume"
        fi
    done
    
    log_success "Docker volumes backup completed"
}

# Backup configuration files
backup_configuration() {
    local backup_path="$1"
    log_info "Backing up configuration files..."
    
    # Create configuration archive
    tar czf "$backup_path/config.tar.gz" \
        -C "$PROJECT_DIR" \
        .env \
        mkdocs.yml \
        requirements.txt \
        docker/ \
        scripts/ \
        --exclude='docker/ssl' \
        --exclude='scripts/__pycache__' 2>/dev/null || {
        log_warning "Failed to backup some configuration files"
    }
    
    log_success "Configuration backup completed"
}

# Backup documentation
backup_documentation() {
    local backup_path="$1"
    log_info "Backing up documentation..."
    
    tar czf "$backup_path/docs.tar.gz" \
        -C "$PROJECT_DIR" \
        docs/ \
        --exclude='docs/.git' 2>/dev/null || {
        log_warning "Failed to backup documentation"
    }
    
    log_success "Documentation backup completed"
}

# Backup uploads directory
backup_uploads() {
    local backup_path="$1"
    log_info "Backing up uploads directory..."
    
    if [[ -d "$PROJECT_DIR/uploads" ]]; then
        tar czf "$backup_path/uploads.tar.gz" \
            -C "$PROJECT_DIR" \
            uploads/ 2>/dev/null || {
            log_warning "Failed to backup uploads"
        }
    else
        log_warning "Uploads directory not found"
    fi
    
    log_success "Uploads backup completed"
}

# Backup SSL certificates
backup_ssl_certificates() {
    local backup_path="$1"
    log_info "Backing up SSL certificates..."
    
    if [[ -d "$PROJECT_DIR/docker/ssl" ]]; then
        tar czf "$backup_path/ssl.tar.gz" \
            -C "$PROJECT_DIR/docker" \
            ssl/ 2>/dev/null || {
            log_warning "Failed to backup SSL certificates"
        }
    else
        log_warning "SSL certificates directory not found"
    fi
    
    log_success "SSL certificates backup completed"
}

# Create backup manifest
create_manifest() {
    local backup_path="$1"
    local backup_type="${2:-daily}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    log_info "Creating backup manifest..."
    
    cat > "$backup_path/manifest.json" << EOF
{
    "backup_info": {
        "type": "$backup_type",
        "created_at": "$timestamp",
        "created_by": "backup.sh",
        "version": "1.0.0"
    },
    "system_info": {
        "hostname": "$(hostname)",
        "os": "$(uname -s)",
        "kernel": "$(uname -r)",
        "docker_version": "$(docker --version 2>/dev/null || echo 'unknown')",
        "docker_compose_version": "$(docker-compose --version 2>/dev/null || echo 'unknown')"
    },
    "backup_contents": {
        "files": [],
        "total_size": 0,
        "checksum": ""
    }
}
EOF

    # List all files in backup
    find "$backup_path" -type f -not -name "manifest.json" | while read -r file; do
        local relative_path="${file#$backup_path/}"
        local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        
        # Update manifest (simple approach - in production, use jq)
        echo "  - $relative_path ($file_size bytes)" >> "$backup_path/file_list.txt"
    done
    
    log_success "Backup manifest created"
}

# Verify backup integrity
verify_backup() {
    local backup_path="$1"
    log_info "Verifying backup integrity..."
    
    local errors=0
    
    # Check if essential files exist
    local required_files=(
        "config.tar.gz"
        "docs.tar.gz"
        "manifest.json"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$backup_path/$file" ]]; then
            log_error "Required backup file missing: $file"
            errors=$((errors + 1))
        fi
    done
    
    # Test archive integrity
    for archive in "$backup_path"/*.tar.gz; do
        if [[ -f "$archive" ]]; then
            if ! tar -tzf "$archive" >/dev/null 2>&1; then
                log_error "Archive integrity check failed: $(basename "$archive")"
                errors=$((errors + 1))
            fi
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        log_success "Backup integrity verification passed"
        return 0
    else
        log_error "Backup integrity verification failed with $errors errors"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    local backup_type="${1:-daily}"
    local retention_days="${2:-$RETENTION_DAYS}"
    
    log_info "Cleaning up old $backup_type backups (retention: $retention_DAYS days)..."
    
    local backup_type_dir="$BACKUP_DIR/$backup_type"
    local deleted_count=0
    
    if [[ -d "$backup_type_dir" ]]; then
        # Find and delete old backup directories
        while IFS= read -r -d '' backup_dir; do
            log_info "Deleting old backup: $(basename "$backup_dir")"
            rm -rf "$backup_dir"
            deleted_count=$((deleted_count + 1))
        done < <(find "$backup_type_dir" -maxdepth 1 -type d -mtime "+$retention_days" -not -path "$backup_type_dir" -print0)
    fi
    
    log_success "Cleanup completed. Deleted $deleted_count old $backup_type backup(s)"
}

# Generate backup report
generate_report() {
    local backup_path="$1"
    local backup_type="${2:-daily}"
    local start_time="${3:-$(date)}"
    local end_time="$(date)"
    
    local backup_size=$(du -sh "$backup_path" | cut -f1)
    local file_count=$(find "$backup_path" -type f | wc -l)
    
    log_info "Generating backup report..."
    
    cat > "$backup_path/backup_report.txt" << EOF
Homelab Documentation Hub - Backup Report
========================================

Backup Type: $backup_type
Backup Path: $backup_path
Started: $start_time
Completed: $end_time
Total Size: $backup_size
Files: $file_count

Backup Contents:
$(ls -la "$backup_path")

System Information:
- Hostname: $(hostname)
- OS: $(uname -s) $(uname -r)
- Docker: $(docker --version 2>/dev/null || echo 'Not available')
- Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Not available')

Next Scheduled Backup:
$(date -d "+1 day" '+%Y-%m-%d %H:%M:%S') (daily)

EOF

    log_success "Backup report generated"
}

# Send notification (placeholder)
send_notification() {
    local backup_type="${1:-daily}"
    local status="${2:-success}"
    local backup_path="${3:-}"
    
    # This is a placeholder for notification integration
    # You can integrate with:
    # - Email notifications
    # - Slack webhooks
    # - Discord webhooks
    # - Push notifications
    
    if [[ "$status" == "success" ]]; then
        log_success "Backup completed successfully: $backup_type"
    else
        log_error "Backup failed: $backup_type"
    fi
}

# Main backup function
perform_backup() {
    local backup_type="${1:-daily}"
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    log_info "Starting $backup_type backup..."
    
    # Create backup directory
    local backup_path
    backup_path=$(create_backup_dir "$backup_type")
    
    # Perform backup operations
    backup_docker_volumes "$backup_path"
    backup_configuration "$backup_path"
    backup_documentation "$backup_path"
    backup_uploads "$backup_path"
    backup_ssl_certificates "$backup_path"
    
    # Create manifest and verify
    create_manifest "$backup_path" "$backup_type"
    
    if verify_backup "$backup_path"; then
        # Cleanup old backups
        cleanup_old_backups "$backup_type"
        
        # Generate report
        generate_report "$backup_path" "$backup_type" "$start_time"
        
        # Send notification
        send_notification "$backup_type" "success" "$backup_path"
        
        log_success "$backup_type backup completed successfully"
        log_info "Backup location: $backup_path"
        log_info "Backup size: $(du -sh "$backup_path" | cut -f1)"
        
        return 0
    else
        # Remove failed backup
        rm -rf "$backup_path"
        
        # Send notification
        send_notification "$backup_type" "failed" ""
        
        log_error "$backup_type backup failed and was cleaned up"
        return 1
    fi
}

# List available backups
list_backups() {
    local backup_type="${1:-daily}"
    
    echo "Available $backup_type backups:"
    echo "=========================="
    
    local backup_type_dir="$BACKUP_DIR/$backup_type"
    
    if [[ -d "$backup_type_dir" ]]; then
        find "$backup_type_dir" -maxdepth 1 -type d -not -path "$backup_type_dir" | \
        sort -r | while read -r backup_dir; do
            local backup_name=$(basename "$backup_dir")
            local backup_size=$(du -sh "$backup_dir" 2>/dev/null | cut -f1 || echo "unknown")
            local backup_date=$(echo "$backup_name" | sed 's/_/ /' | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3/')
            
            echo "$backup_name - $backup_size - $backup_date"
        done
    else
        echo "No $backup_type backups found"
    fi
}

# Restore from backup
restore_backup() {
    local backup_timestamp="$1"
    local backup_type="${2:-daily}"
    
    log_info "Starting restore from backup: $backup_timestamp"
    
    local backup_path="$BACKUP_DIR/$backup_type/$backup_timestamp"
    
    if [[ ! -d "$backup_path" ]]; then
        log_error "Backup not found: $backup_path"
        return 1
    fi
    
    # Verify backup before restore
    if ! verify_backup "$backup_path"; then
        log_error "Backup integrity verification failed. Aborting restore."
        return 1
    fi
    
    log_warning "This will overwrite current configuration and data!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled by user"
        return 0
    fi
    
    # Stop services
    cd "$PROJECT_DIR/docker"
    docker-compose down
    
    # Restore configuration
    if [[ -f "$backup_path/config.tar.gz" ]]; then
        log_info "Restoring configuration..."
        tar xzf "$backup_path/config.tar.gz" -C "$PROJECT_DIR"
    fi
    
    # Restore documentation
    if [[ -f "$backup_path/docs.tar.gz" ]]; then
        log_info "Restoring documentation..."
        tar xzf "$backup_path/docs.tar.gz" -C "$PROJECT_DIR"
    fi
    
    # Restore uploads
    if [[ -f "$backup_path/uploads.tar.gz" ]]; then
        log_info "Restoring uploads..."
        tar xzf "$backup_path/uploads.tar.gz" -C "$PROJECT_DIR"
    fi
    
    # Restore Docker volumes
    for volume_file in "$backup_path"/volume_*.tar.gz; do
        if [[ -f "$volume_file" ]]; then
            local volume_name=$(basename "$volume_file" | sed 's/^volume_//' | sed 's/\.tar.gz$//')
            log_info "Restoring volume: $volume_name"
            
            docker run --rm \
                -v "$volume_name":/data \
                -v "$backup_path":/backup:ro \
                alpine tar xzf "/backup/volume_${volume_name}.tar.gz" -C /data || {
                log_warning "Failed to restore volume: $volume_name"
            }
        fi
    done
    
    # Start services
    docker-compose up -d
    
    log_success "Restore completed successfully"
    log_info "Services are being started..."
}

# Show usage
show_usage() {
    cat << EOF
Homelab Documentation Hub - Backup Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    daily               Perform daily backup (default)
    weekly              Perform weekly backup
    monthly             Perform monthly backup
    list [TYPE]         List available backups (default: daily)
    restore TIMESTAMP   Restore from backup
    help                Show this help message

Backup Types:
    daily               Daily backups (retention: 30 days)
    weekly              Weekly backups (retention: 90 days)
    monthly             Monthly backups (retention: 365 days)

Examples:
    $0 daily                    # Perform daily backup
    $0 list weekly              # List weekly backups
    $0 restore 20240101_120000  # Restore from backup
    $0 weekly                   # Perform weekly backup

Environment Variables:
    BACKUP_DIR                 Backup directory (default: ./backups)
    RETENTION_DAYS             Retention period for daily backups
    LOG_FILE                  Log file location
EOF
}

# Main execution
main() {
    # Create necessary directories
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$BACKUP_DIR"/{daily,weekly,monthly}
    
    # Parse command line arguments
    case "${1:-daily}" in
        "daily")
            perform_backup "daily"
            ;;
        "weekly")
            perform_backup "weekly"
            ;;
        "monthly")
            perform_backup "monthly"
            ;;
        "list")
            list_backups "${2:-daily}"
            ;;
        "restore")
            if [[ -z "${2:-}" ]]; then
                log_error "Backup timestamp required for restore"
                show_usage
                exit 1
            fi
            restore_backup "$2" "${3:-daily}"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'log_error "Backup interrupted"; exit 1' INT TERM

# Run main function
main "$@"

#!/bin/bash

# Health Check Script for Homelab Documentation System
# This script checks the health of all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-homelab-docs}
HEALTH_CHECK_TIMEOUT=30
LOG_FILE="logs/health-check.log"

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check service health
check_service() {
    local service_name=$1
    local health_check_url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -f -s -o /dev/null -w "%{http_code}" --max-time "$HEALTH_CHECK_TIMEOUT" "$health_check_url" | grep -q "$expected_status"; then
        echo -e "${GREEN}OK${NC}"
        log_message "SUCCESS: $service_name is healthy"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        log_message "ERROR: $service_name health check failed"
        return 1
    fi
}

# Function to check Docker container status
check_container() {
    local container_name=$1
    local expected_status=${2:-running}
    
    echo -n "Checking container $container_name... "
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name.*$expected_status"; then
        echo -e "${GREEN}OK${NC}"
        log_message "SUCCESS: Container $container_name is $expected_status"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        log_message "ERROR: Container $container_name is not $expected_status"
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    echo -n "Checking Redis connectivity... "
    
    if docker exec homelab-docs-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        log_message "SUCCESS: Redis is responding"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        log_message "ERROR: Redis is not responding"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    echo -n "Checking disk space... "
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 85 ]; then
        echo -e "${GREEN}OK (${usage}%)${NC}"
        log_message "SUCCESS: Disk usage is ${usage}%"
        return 0
    else
        echo -e "${YELLOW}WARNING (${usage}%)${NC}"
        log_message "WARNING: Disk usage is high at ${usage}%"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    echo -n "Checking memory usage... "
    
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$memory_usage" -lt 80 ]; then
        echo -e "${GREEN}OK (${memory_usage}%)${NC}"
        log_message "SUCCESS: Memory usage is ${memory_usage}%"
        return 0
    else
        echo -e "${YELLOW}WARNING (${memory_usage}%)${NC}"
        log_message "WARNING: Memory usage is high at ${memory_usage}%"
        return 1
    fi
}

# Main health check function
main() {
    echo -e "${YELLOW}Starting health checks for Homelab Documentation System...${NC}"
    log_message "=== Starting health check ==="
    
    local failed_checks=0
    
    # Check Docker containers
    check_container "homelab-docs-mkdocs" || ((failed_checks++))
    check_container "homelab-docs-ai-backend" || ((failed_checks++))
    check_container "homelab-docs-nginx" || ((failed_checks++))
    check_container "homelab-docs-redis" || ((failed_checks++))
    
    # Check service health endpoints
    check_service "MkDocs" "http://localhost:8000" || ((failed_checks++))
    check_service "AI Backend" "http://localhost:8001/health" || ((failed_checks++))
    check_service "Nginx" "http://localhost" || ((failed_checks++))
    
    # Check Redis connectivity
    check_redis || ((failed_checks++))
    
    # Check system resources
    check_disk_space || ((failed_checks++))
    check_memory || ((failed_checks++))
    
    # Summary
    echo -e "\n${YELLOW}Health Check Summary:${NC}"
    if [ $failed_checks -eq 0 ]; then
        echo -e "${GREEN}All checks passed!${NC}"
        log_message "=== Health check completed successfully ==="
        return 0
    else
        echo -e "${RED}$failed_checks check(s) failed${NC}"
        log_message "=== Health check completed with $failed_checks failures ==="
        return 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

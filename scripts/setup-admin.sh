#!/bin/bash

# Admin Authentication Setup Script for Homelab Documentation System
# This script creates secure admin credentials and configures authentication

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
USERNAME=${1:-admin}
PASSWORD=${2:-}
HTPASSWD_FILE="docker/htpasswd"
MIN_PASSWORD_LENGTH=12

echo -e "${GREEN}🔧 Setting up admin authentication for Homelab Documentation System${NC}"
echo

# Check if htpasswd is available
if ! command -v htpasswd &> /dev/null; then
    echo -e "${RED}❌ Error: htpasswd command not found${NC}"
    echo "Please install apache2-utils (Ubuntu/Debian) or httpd-tools (CentOS/RHEL)"
    echo "Ubuntu/Debian: sudo apt-get install apache2-utils"
    echo "CentOS/RHEL: sudo yum install httpd-tools"
    exit 1
fi

# Generate secure password if not provided
if [ -z "$PASSWORD" ]; then
    echo -e "${YELLOW}🔑 Generating secure password...${NC}"
    
    # Generate random password with special characters
    PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-${MIN_PASSWORD_LENGTH})
    
    # Ensure password meets complexity requirements
    if [[ ${#PASSWORD} -lt ${MIN_PASSWORD_LENGTH} ]]; then
        # Fallback to simpler password generation
        PASSWORD=$(openssl rand -hex 16)
    fi
    
    echo -e "${GREEN}✅ Generated password: ${PASSWORD}${NC}"
    echo -e "${YELLOW}⚠️  Please store this password securely!${NC}"
    echo
fi

# Validate password complexity
validate_password() {
    local pass="$1"
    
    # Check minimum length
    if [[ ${#pass} -lt 8 ]]; then
        echo -e "${RED}❌ Password must be at least 8 characters long${NC}"
        return 1
    fi
    
    # Check for at least one uppercase letter
    if [[ ! "$pass" =~ [A-Z] ]]; then
        echo -e "${RED}❌ Password must contain at least one uppercase letter${NC}"
        return 1
    fi
    
    # Check for at least one lowercase letter
    if [[ ! "$pass" =~ [a-z] ]]; then
        echo -e "${RED}❌ Password must contain at least one lowercase letter${NC}"
        return 1
    fi
    
    # Check for at least one number
    if [[ ! "$pass" =~ [0-9] ]]; then
        echo -e "${RED}❌ Password must contain at least one number${NC}"
        return 1
    fi
    
    # Check for at least one special character
    if [[ ! "$pass" =~ [!@#$%^&*()] ]]; then
        echo -e "${RED}❌ Password must contain at least one special character (!@#$%^&*())${NC}"
        return 1
    fi
    
    return 0
}

# Validate the password
if ! validate_password "$PASSWORD"; then
    echo -e "${RED}❌ Password validation failed. Please choose a stronger password.${NC}"
    echo "Password requirements:"
    echo "- At least 8 characters long"
    echo "- Contains uppercase and lowercase letters"
    echo "- Contains at least one number"
    echo "- Contains at least one special character (!@#$%^&*())"
    exit 1
fi

# Create docker directory if it doesn't exist
mkdir -p docker

# Create htpasswd file
echo -e "${YELLOW}📝 Creating htpasswd file...${NC}"

if [ -f "$HTPASSWD_FILE" ]; then
    echo -e "${YELLOW}⚠️  Existing htpasswd file found. Creating backup...${NC}"
    cp "$HTPASSWD_FILE" "${HTPASSWD_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create the password file
echo "$PASSWORD" | htpasswd -i -c "$HTPASSWD_FILE" "$USERNAME"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Admin user created successfully!${NC}"
    echo
    echo -e "${GREEN}👤 Username: ${USERNAME}${NC}"
    echo -e "${GREEN}🔑 Password: ${PASSWORD}${NC}"
    echo
    echo -e "${GREEN}📁 Credentials file: ${HTPASSWD_FILE}${NC}"
    echo
else
    echo -e "${RED}❌ Failed to create admin user${NC}"
    exit 1
fi

# Set appropriate permissions
chmod 640 "$HTPASSWD_FILE"

# Verify the file was created correctly
if [ -f "$HTPASSWD_FILE" ] && [ -s "$HTPASSWD_FILE" ]; then
    echo -e "${GREEN}✅ Authentication setup completed successfully!${NC}"
    echo
    echo -e "${YELLOW}📋 Next steps:${NC}"
    echo "1. Restart the Docker containers: docker-compose -f docker/docker-compose.yml restart"
    echo "2. Access the admin interface at: http://localhost/admin"
    echo "3. Login with the credentials above"
    echo
    echo -e "${YELLOW}🔒 Security notes:${NC}"
    echo "- Store the password in a secure password manager"
    echo "- The htpasswd file contains bcrypt hashes, not plain text"
    echo "- Regularly rotate admin passwords"
    echo "- Consider implementing 2FA for additional security"
else
    echo -e "${RED}❌ Authentication setup failed${NC}"
    exit 1
fi

# Show file permissions
echo -e "${YELLOW}📊 File information:${NC}"
echo "File: $HTPASSWD_FILE"
echo "Size: $(stat -c%s "$HTPASSWD_FILE" 2>/dev/null || stat -f%z "$HTPASSWD_FILE" 2>/dev/null) bytes"
echo "Permissions: $(ls -la "$HTPASSWD_FILE" | awk '{print $1}')"
echo "Owner: $(ls -la "$HTPASSWD_FILE" | awk '{print $3}')"

echo -e "${GREEN}🎉 Admin authentication setup complete!${NC}"

---
title: API Reference
description: Complete API documentation for the AI Content Management System
---

# API Reference

This document provides comprehensive documentation for the AI Content Management API that powers the homelab documentation hub.

## Base URL

```
http://localhost:8001
```

## Authentication

The API uses JWT (JSON Web Token) based authentication. All endpoints (except authentication endpoints and health checks) require a valid Bearer token.

### Authentication Flow

1. **Register** a new user account
2. **Login** to receive access and refresh tokens
3. **Use** the access token for API requests
4. **Refresh** the access token when it expires
5. **Logout** to invalidate tokens

```http
Authorization: Bearer your-access-token-here
```

### Authentication Endpoints

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "username": "johndoe",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Logout
```http
POST /auth/logout
```

**Headers:**
```http
Authorization: Bearer your-access-token-here
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

#### Admin Login Page
```http
GET /admin/login
```

Returns an HTML login page for administrative access.

### Token Management

- **Access Token**: Valid for 30 minutes
- **Refresh Token**: Valid for 7 days
- **Token Storage**: Refresh tokens are stored in Redis for validation

## Protected Endpoints

All endpoints below require valid JWT authentication unless otherwise noted.

### Content Management

#### Generate Content
```http
POST /api/generate
```

**Request Body:**
```json
{
  "topic": "Docker container networking",
  "content_type": "guide",
  "target_audience": "intermediate",
  "length": "medium",
  "additional_context": "Focus on homelab environments"
}
```

**Response:**
```json
{
  "content": "# Docker Container Networking\n\n## Overview\n...",
  "metadata": {
    "topic": "Docker container networking",
    "content_type": "guide",
    "target_audience": "intermediate",
    "generated_at": "2024-01-01T00:00:00Z",
    "word_count": 850,
    "reading_time_minutes": 4
  },
  "suggestions": [
    "Expand on Docker networking advanced topics",
    "Create practical Docker networking examples",
    "Add troubleshooting section for Docker networks"
  ]
}
```

#### AI Chat
```http
POST /api/ai/chat
```

**Request Body:**
```json
{
  "message": "How do I set up a reverse proxy with Nginx?",
  "context": {
    "page_title": "Network Configuration",
    "page_url": "/homelab/network/",
    "headings": ["Nginx", "Reverse Proxy", "SSL"]
  }
}
```

**Response:**
```json
{
  "response": "To set up a reverse proxy with Nginx, you'll need to...",
  "timestamp": "2024-01-01T12:00:00Z",
  "user": "johndoe"
}
```

### File Management

#### List Files
```http
GET /api/files?path=homelab/network
```

**Response:**
```json
{
  "files": [
    {
      "name": "router.md",
      "path": "homelab/network/router.md",
      "type": "file",
      "size": 2048,
      "modified": 1704067200
    },
    {
      "name": "firewall",
      "path": "homelab/network/firewall",
      "type": "directory",
      "children": 3
    }
  ],
  "path": "homelab/network"
}
```

#### Manage Files
```http
POST /api/files
```

**Request Body:**
```json
{
  "action": "create",
  "path": "guides/new-guide.md",
  "content": "# New Guide\n\nThis is a new guide document.",
  "metadata": {
    "title": "New Guide",
    "description": "A comprehensive guide"
  }
}
```

**Actions:**
- `create` - Create new file
- `update` - Update existing file
- `delete` - Delete file

#### Upload File
```http
POST /api/upload
```

**Multipart Form Data:**
- `file`: File to upload
- `path`: Target directory (optional)

**Response:**
```json
{
  "message": "Successfully uploaded document.pdf",
  "path": "uploads/document.pdf"
}
```

### Navigation Management

#### Get Navigation
```http
GET /api/navigation
```

**Response:**
```json
{
  "navigation": {
    "index": {"title": "Home", "path": "/"},
    "homelab": {
      "title": "Homelab Projects",
      "children": {
        "network": {"title": "Network", "path": "/homelab/network/"},
        "storage": {"title": "Storage", "path": "/homelab/storage/"},
        "virtualization": {"title": "Virtualization", "path": "/homelab/virtualization/"},
        "monitoring": {"title": "Monitoring", "path": "/homelab/monitoring/"}
      }
    }
  }
}
```

#### Update Navigation
```http
POST /api/navigation
```

**Request Body:**
```json
{
  "section": "homelab",
  "action": "add",
  "item": {
    "title": "New Section",
    "path": "/homelab/new-section/"
  }
}
```

### Statistics

#### Get Documentation Statistics
```http
GET /api/stats
```

**Response:**
```json
{
  "total_files": 45,
  "total_size": 1048576,
  "content_types": {
    "homelab": 15,
    "guides": 12,
    "coursework": 8,
    "development": 6,
    "about": 4
  },
  "last_updated": 1704067200
}
```

### Health Checks

#### System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "ai": "operational",
    "file_system": "operational"
  }
}
```

#### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Homelab Documentation AI Backend",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "generate": "/api/generate",
    "files": "/api/files",
    "navigation": "/api/navigation"
  }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid or expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

**Authentication Errors:**
```json
{
  "detail": "Could not validate credentials",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **General Endpoints**: 100 requests per hour per IP
- **Auth Endpoints**: 20 requests per burst
- **API Endpoints**: 20 requests per burst
- **Admin Endpoints**: 10 requests per burst

Rate limiting is implemented using Redis and includes:
- Per-IP tracking
- Endpoint-specific limits
- Burst allowance
- Graceful degradation when Redis is unavailable

## Security Features

### JWT Security
- **Algorithm**: HS256
- **Secret Key**: Configurable via `SECRET_KEY` environment variable
- **Token Expiration**: Access tokens (30 min), Refresh tokens (7 days)
- **Token Type**: Access and refresh tokens with different purposes

### Password Security
- **Hashing**: bcrypt with automatic salt generation
- **Deprecated Schemes**: Auto-migration from legacy hashes
- **Minimum Length**: 8 characters
- **Validation**: Strong password requirements

### CORS Configuration
- **Allowed Origins**: Configurable via `ALLOWED_ORIGINS`
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Standard headers including Authorization
- **Credentialed Requests**: Supported for authentication

## SDK Examples

### Python Client
```python
import requests
import json

class HomelabDocsAPI:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url.rstrip('/')
        self.access_token = None
        self.refresh_token = None
        
        if username and password:
            self.login(username, password)
    
    def login(self, username, password):
        """Authenticate and store tokens"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return True
        return False
    
    def _get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def generate_content(self, topic, content_type="guide", target_audience="beginner"):
        """Generate AI content"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "topic": topic,
                "content_type": content_type,
                "target_audience": target_audience
            },
            headers=self._get_headers()
        )
        return response.json()
    
    def list_files(self, path=""):
        """List files in documentation"""
        response = requests.get(
            f"{self.base_url}/api/files",
            params={"path": path},
            headers=self._get_headers()
        )
        return response.json()

# Usage example
api = HomelabDocsAPI("http://localhost:8001", "johndoe", "password123")

# Generate content
result = api.generate_content(
    topic="Setting up a home network",
    content_type="guide",
    target_audience="beginner"
)
print(result['content'])

# List files
files = api.list_files("homelab")
print(files)
```

### JavaScript Client
```javascript
class HomelabDocsAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.accessToken = null;
        this.refreshToken = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            this.accessToken = data.access_token;
            this.refreshToken = data.refresh_token;
            return true;
        }
        return false;
    }
    
    getHeaders() {
        return {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async generateContent(topic, contentType = 'guide', targetAudience = 'beginner') {
        const response = await fetch(`${this.baseUrl}/api/generate`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
                topic,
                content_type: contentType,
                target_audience: targetAudience
            })
        });
        return response.json();
    }
    
    async listFiles(path = '') {
        const response = await fetch(`${this.baseUrl}/api/files?path=${encodeURIComponent(path)}`, {
            headers: this.getHeaders()
        });
        return response.json();
    }
}

// Usage example
const api = new HomelabDocsAPI('http://localhost:8001');
await api.login('johndoe', 'password123');

// Generate content
const result = await api.generateContent(
    'Docker container setup',
    'guide',
    'beginner'
);
console.log(result.content);
```

## Integration Examples

### GitHub Actions
```yaml
name: Update Documentation
on:
  push:
    branches: [main]

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to API
        run: |
          TOKEN=$(curl -X POST http://your-domain.com/auth/login \
            -H "Content-Type: application/json" \
            -d '{"username":"${{ secrets.API_USERNAME }}","password":"${{ secrets.API_PASSWORD }}"}' | \
            jq -r '.access_token')
          echo "TOKEN=$TOKEN" >> $GITHUB_ENV
      
      - name: Generate content
        run: |
          curl -X POST http://your-domain.com/api/generate \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
              "topic": "Latest updates for changelog",
              "content_type": "changelog",
              "target_audience": "all"
            }'
```

### WordPress Plugin
```php
<?php
class Homelab_Docs_Sync {
    private $api_url;
    private $username;
    private $password;
    private $access_token = null;
    
    public function __construct() {
        $this->api_url = get_option('homelab_api_url');
        $this->username = get_option('homelab_api_username');
        $this->password = get_option('homelab_api_password');
    }
    
    private function login() {
        $response = wp_remote_post($this->api_url . '/auth/login', [
            'headers' => ['Content-Type' => 'application/json'],
            'body' => json_encode([
                'username' => $this->username,
                'password' => $this->password
            ])
        ]);
        
        if (!is_wp_error($response)) {
            $data = json_decode(wp_remote_retrieve_body($response), true);
            $this->access_token = $data['access_token'];
            return true;
        }
        return false;
    }
    
    public function sync_post($post_id) {
        if (!$this->access_token && !$this->login()) {
            return false;
        }
        
        $post = get_post($post_id);
        
        $response = wp_remote_post($this->api_url . '/api/files', [
            'headers' => [
                'Authorization' => 'Bearer ' . $this->access_token,
                'Content-Type' => 'application/json'
            ],
            'body' => json_encode([
                'action' => 'create',
                'path' => 'wordpress/sync-' . $post_id . '.md',
                'content' => $post->post_content
            ])
        ]);
        
        return !is_wp_error($response);
    }
}

// Usage
$sync = new Homelab_Docs_Sync();
add_action('publish_post', [$sync, 'sync_post']);
?>
```

## Troubleshooting

### Authentication Issues

1. **Token Expired**
   ```bash
   # Check token expiration
   curl -H "Authorization: Bearer <token>" http://localhost:8001/api/files
   
   # Refresh token
   curl -X POST http://localhost:8001/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<refresh_token>"}'
   ```

2. **Invalid Credentials**
   ```bash
   # Verify user exists and password is correct
   curl -X POST http://localhost:8001/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}'
   ```

3. **Redis Connection Issues**
   ```bash
   # Check Redis connection
   redis-cli ping
   
   # Check Redis logs
   docker logs redis-container
   ```

### Common Errors

1. **401 Unauthorized**
   - Check that your access token is valid
   - Verify the token hasn't expired
   - Ensure you're using the correct token type (access, not refresh)

2. **429 Too Many Requests**
   - You've hit the rate limit
   - Wait before making more requests
   - Consider implementing exponential backoff

3. **500 Internal Server Error**
   - Check server logs for details
   - Verify OpenAI API key is valid
   - Ensure Redis is accessible

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export LOG_LEVEL=DEBUG
export REDIS_URL=redis://localhost:6379/0
```

This will provide detailed logs for troubleshooting API issues.

---

**Note**: This API documentation reflects the latest version with JWT authentication. Ensure your client implementations are updated accordingly.

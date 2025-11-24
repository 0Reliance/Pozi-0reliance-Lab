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

All API endpoints (except the root endpoint) require Bearer token authentication.

```http
Authorization: Bearer your-secret-key-change-in-production
```

## Endpoints

### Content Management

#### Create Content

Generates new documentation content using AI.

```http
POST /api/content/create
```

**Request Body:**
```json
{
  "prompt": "Create a guide for setting up a home NAS",
  "content_type": "markdown",
  "target_path": "homelab/storage/nas-setup.md",
  "section": "homelab",
  "auto_nav": true
}
```

**Response:**
```json
{
  "message": "Content created successfully",
  "file_path": "homelab/storage/nas-setup.md",
  "content": "# Home NAS Setup Guide\n...",
  "navigation_updated": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Update Content

Modifies existing documentation files.

```http
POST /api/content/update
```

**Request Body:**
```json
{
  "file_path": "homelab/network/router.md",
  "operation": "append",
  "content": "\n## Troubleshooting\nCommon issues and solutions...",
  "target_section": "Troubleshooting"
}
```

**Operations:**
- `append` - Add content to the end of the file
- `prepend` - Add content to the beginning of the file
- `replace` - Replace entire file or specific section

### Navigation Management

#### Update Navigation

Modifies the MkDocs navigation structure.

```http
POST /api/navigation/update
```

**Request Body:**
```json
{
  "additions": [
    {
      "title": "New Guide",
      "path": "guides/new-guide.md",
      "section": "guides"
    }
  ],
  "removals": ["old-guide.md"],
  "reorder": {
    "guides": ["getting-started", "best-practices", "new-guide"]
  }
}
```

### AI Chat Interface

#### Chat with AI Assistant

Interactive chat interface for content assistance.

```http
POST /api/ai/chat
```

**Request Body:**
```json
{
  "message": "How should I structure a technical tutorial?",
  "context": {
    "current_section": "guides"
  },
  "conversation_history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
  ]
}
```

**Response:**
```json
{
  "response": "For technical tutorials, I recommend starting with clear objectives...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### File Operations

#### List Files

Browse documentation directory structure.

```http
GET /api/files/list?path=homelab/network
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
      "modified": "2024-01-01T12:00:00Z"
    }
  ],
  "path": "homelab/network"
}
```

#### Get File Content

Retrieve content of a specific file.

```http
GET /api/files/content?file_path=homelab/network/router.md
```

**Response:**
```json
{
  "file_path": "homelab/network/router.md",
  "frontmatter": {
    "title": "Router Configuration",
    "description": "Complete router setup guide"
  },
  "content": "# Router Configuration\n...",
  "raw_content": "---\ntitle: Router Configuration\n---\n# Router Configuration..."
}
```

#### File Operations

Perform file operations (create, update, delete, move).

```http
POST /api/files/operation
```

**Request Body:**
```json
{
  "operation": "create",
  "file_path": "guides/new-guide.md",
  "content": "# New Guide\nContent here..."
}
```

**Operations:**
- `create` - Create new file
- `update` - Update existing file
- `delete` - Delete file
- `move` - Move/rename file

### Statistics

#### Get Documentation Statistics

Retrieve statistics about the documentation site.

```http
GET /api/stats
```

**Response:**
```json
{
  "total_files": 45,
  "total_size": 1048576,
  "file_types": {
    ".md": 40,
    ".js": 3,
    ".css": 2
  },
  "last_updated": "2024-01-01T12:00:00Z"
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
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per minute per IP address
- 10 content generation requests per minute
- 50 file operations per minute

## Webhooks

The system supports webhooks for integration with external services:

### Content Created Webhook

Triggered when new content is created:

```json
{
  "event": "content.created",
  "data": {
    "file_path": "homelab/storage/nas.md",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Navigation Updated Webhook

Triggered when navigation structure changes:

```json
{
  "event": "navigation.updated",
  "data": {
    "changes": ["additions", "removals"],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## SDK Examples

### Python

```python
import requests

# Initialize client
base_url = "http://localhost:8001"
headers = {
    "Authorization": "Bearer your-secret-key-change-in-production",
    "Content-Type": "application/json"
}

# Create content
response = requests.post(
    f"{base_url}/api/content/create",
    json={
        "prompt": "Create a Docker setup guide",
        "section": "homelab",
        "auto_nav": True
    },
    headers=headers
)

result = response.json()
print(f"Created: {result['file_path']}")
```

### JavaScript

```javascript
// Initialize client
const baseURL = 'http://localhost:8001';
const headers = {
  'Authorization': 'Bearer your-secret-key-change-in-production',
  'Content-Type': 'application/json'
};

// Create content
const response = await fetch(`${baseURL}/api/content/create`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    prompt: 'Create a Kubernetes guide',
    section: 'homelab',
    auto_nav: true
  })
});

const result = await response.json();
console.log(`Created: ${result.file_path}`);
```

### cURL

```bash
# Create content
curl -X POST http://localhost:8001/api/content/create \
  -H "Authorization: Bearer your-secret-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a monitoring setup guide",
    "section": "homelab",
    "auto_nav": true
  }'
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
      
      - name: Generate content
        run: |
          curl -X POST http://localhost:8001/api/content/create \
            -H "Authorization: Bearer ${{ secrets.API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{"prompt": "Update changelog for latest release", "section": "about"}'
```

### WordPress Integration

```php
<?php
function sync_to_homelab_docs($post_id) {
    $post = get_post($post_id);
    $api_url = 'http://localhost:8001/api/content/create';
    
    $response = wp_remote_post($api_url, [
        'headers' => [
            'Authorization' => 'Bearer ' . get_option('homelab_api_key'),
            'Content-Type' => 'application/json'
        ],
        'body' => json_encode([
            'prompt' => $post->post_content,
            'target_path' => "guides/wp-sync-{$post_id}.md",
            'auto_nav' => true
        ])
    ]);
}

add_action('publish_post', 'sync_to_homelab_docs');
?>
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your Bearer token is correct
   - Check that the token hasn't expired

2. **Content Generation Fails**
   - Ensure OpenAI API key is valid
   - Check available credits in your OpenAI account

3. **File Operation Errors**
   - Verify file paths are correct
   - Check directory permissions

4. **Navigation Update Issues**
   - Ensure MkDocs config is writable
   - Check YAML syntax validity

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

This will provide detailed logs for troubleshooting API issues.

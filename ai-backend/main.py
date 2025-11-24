"""
Homelab Documentation AI Backend
FastAPI service for AI-powered content generation and management
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Homelab Docs AI Backend",
    description="AI-powered content management for homelab documentation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DOCS_ROOT = Path(__file__).parent.parent / "docs"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

# Pydantic models
class ContentRequest(BaseModel):
    topic: str = Field(..., description="Topic for content generation")
    content_type: str = Field(default="guide", description="Type of content to generate")
    target_audience: str = Field(default="beginner", description="Target audience level")
    length: Optional[str] = Field(default="medium", description="Content length")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")

class ContentResponse(BaseModel):
    content: str
    metadata: Dict[str, Any]
    suggestions: List[str]

class FileOperation(BaseModel):
    action: str  # create, update, delete
    path: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class NavigationUpdate(BaseModel):
    section: str
    action: str  # add, remove, update
    item: Dict[str, Any]

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "ai": "operational" if Config.OPENAI_API_KEY else "limited",
            "file_system": "operational"
        }
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Homelab Documentation AI Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate",
            "files": "/api/files",
            "navigation": "/api/navigation"
        }
    }

# Content generation endpoints
@app.post("/api/generate", response_model=ContentResponse, tags=["Content Generation"])
async def generate_content(request: ContentRequest):
    """Generate AI-powered content"""
    try:
        if not Config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured"
            )
        
        # TODO: Implement actual AI content generation
        # This is a placeholder implementation
        content = f"""# {request.topic.title()}

## Overview
This is a comprehensive guide about {request.topic}.

## Key Concepts
- Concept 1: Description of key concept 1
- Concept 2: Description of key concept 2

## Implementation
```python
# Example implementation
def {request.topic.lower().replace(' ', '_')}():
    # Implementation details
    pass
```

## Best Practices
1. Practice 1
2. Practice 2
3. Practice 3

## See Also
- [Related Guide 1](related-guide-1.md)
- [Related Guide 2](related-guide-2.md)

---

*This guide is part of the Homelab Documentation series.*
"""
        
        metadata = {
            "topic": request.topic,
            "content_type": request.content_type,
            "target_audience": request.target_audience,
            "generated_at": "2024-01-01T00:00:00Z",
            "word_count": len(content.split()),
            "reading_time_minutes": max(1, len(content.split()) // 200)
        }
        
        suggestions = [
            f"Expand on {request.topic} advanced topics",
            f"Create practical examples for {request.topic}",
            f"Add troubleshooting section for {request.topic}"
        ]
        
        return ContentResponse(
            content=content,
            metadata=metadata,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File management endpoints
@app.get("/api/files", tags=["File Management"])
async def list_files(path: str = ""):
    """List files in the documentation directory"""
    try:
        target_path = Config.DOCS_ROOT / path if path else Config.DOCS_ROOT
        
        if not target_path.exists() or not target_path.is_dir():
            raise HTTPException(status_code=404, detail="Path not found")
        
        files = []
        for item in target_path.iterdir():
            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(Config.DOCS_ROOT)),
                    "type": "file",
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime
                })
            elif item.is_dir():
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(Config.DOCS_ROOT)),
                    "type": "directory",
                    "children": len(list(item.iterdir()))
                })
        
        return {"files": files, "path": path}
        
    except Exception as e:
        logger.error(f"File listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files", tags=["File Management"])
async def manage_file(operation: FileOperation):
    """Create, update, or delete files"""
    try:
        if operation.action not in ["create", "update", "delete"]:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        target_path = Config.DOCS_ROOT / operation.path
        
        if operation.action == "delete":
            if target_path.exists():
                target_path.unlink()
                return {"message": f"Deleted {operation.path}"}
            else:
                raise HTTPException(status_code=404, detail="File not found")
        
        elif operation.action in ["create", "update"]:
            # Ensure directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if operation.content is None:
                raise HTTPException(status_code=400, detail="Content required for create/update")
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(operation.content)
            
            action_name = "created" if operation.action == "create" else "updated"
            return {"message": f"Successfully {action_name} {operation.path}"}
        
    except Exception as e:
        logger.error(f"File operation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload", tags=["File Management"])
async def upload_file(file: UploadFile = File(...), path: str = ""):
    """Upload a file to the documentation"""
    try:
        target_path = Config.DOCS_ROOT / path if path else Config.DOCS_ROOT
        target_path.mkdir(parents=True, exist_ok=True)
        
        file_path = target_path / file.filename
        
        if file_path.exists():
            raise HTTPException(status_code=409, detail="File already exists")
        
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "message": f"Successfully uploaded {file.filename}",
            "path": str(file_path.relative_to(Config.DOCS_ROOT))
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Navigation management endpoints
@app.post("/api/navigation", tags=["Navigation"])
async def update_navigation(update: NavigationUpdate):
    """Update navigation structure"""
    try:
        # TODO: Implement navigation updates
        # This would involve updating mkdocs.yml or similar
        return {
            "message": f"Navigation {update.action} for {update.section}",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Navigation update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/navigation", tags=["Navigation"])
async def get_navigation():
    """Get current navigation structure"""
    try:
        # TODO: Implement navigation retrieval from mkdocs.yml
        return {
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
                },
                "coursework": {
                    "title": "Coursework",
                    "children": {
                        "cs": {"title": "Computer Science", "path": "/coursework/cs/"}
                    }
                },
                "guides": {
                    "title": "Guides",
                    "children": {
                        "getting-started": {"title": "Getting Started", "path": "/guides/getting-started/"},
                        "best-practices": {"title": "Best Practices", "path": "/guides/best-practices/"},
                        "troubleshooting": {"title": "Troubleshooting", "path": "/guides/troubleshooting/"},
                        "security": {"title": "Security", "path": "/guides/security/"}
                    }
                },
                "about": {
                    "title": "About",
                    "children": {
                        "index": {"title": "About", "path": "/about/"},
                        "contributing": {"title": "Contributing", "path": "/about/contributing/"},
                        "changelog": {"title": "Changelog", "path": "/about/changelog/"}
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Navigation retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics endpoint
@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """Get documentation statistics"""
    try:
        stats = {
            "total_files": 0,
            "total_size": 0,
            "content_types": {},
            "last_updated": None
        }
        
        # Walk through documentation directory
        for file_path in Config.DOCS_ROOT.rglob("*.md"):
            stats["total_files"] += 1
            stats["total_size"] += file_path.stat().st_size
            
            # Categorize by directory
            category = file_path.parent.name
            stats["content_types"][category] = stats["content_types"].get(category, 0) + 1
            
            # Track last modified
            if stats["last_updated"] is None or file_path.stat().st_mtime > stats["last_updated"]:
                stats["last_updated"] = file_path.stat().st_mtime
        
        return stats
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Resource not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

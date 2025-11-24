"""
AI-Powered Content Management Backend for Homelab Documentation Hub

This FastAPI application provides AI-powered content creation, management,
and organization for MkDocs-based documentation sites.
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
import json
import asyncio
import aiofiles
from pathlib import Path
import re
from datetime import datetime
import git
from openai import AsyncOpenAI
import yaml
from jinja2 import Template, Environment, FileSystemLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
class Settings(BaseSettings):
    openai_api_key: str = ""
    secret_key: str = "your-secret-key-change-in-production"
    docs_path: str = "../docs"
    admin_path: str = "../admin"
    mkdocs_config: str = "../mkdocs.yml"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Initialize FastAPI
app = FastAPI(
    title="AI Content Management API",
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

# Security
security = HTTPBearer()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

# Jinja2 environment for templates
template_env = Environment(loader=FileSystemLoader("templates"))

# Data models
class ContentRequest(BaseModel):
    prompt: str = Field(..., description="Natural language description of content to create")
    content_type: str = Field("markdown", description="Type of content to create")
    target_path: Optional[str] = Field(None, description="Target file path for the content")
    section: Optional[str] = Field(None, description="Documentation section (homelab, coursework, guides)")
    auto_nav: bool = Field(True, description="Automatically update navigation")

class ContentUpdate(BaseModel):
    file_path: str = Field(..., description="Path to the file to update")
    operation: str = Field(..., description="Operation: append, prepend, replace")
    content: str = Field(..., description="Content to add/replace")
    target_section: Optional[str] = Field(None, description="Specific section to target")

class NavigationUpdate(BaseModel):
    additions: List[Dict[str, Any]] = Field(default_factory=list)
    removals: List[str] = Field(default_factory=list)
    reorder: Optional[Dict[str, List[str]]] = Field(None)

class AIChatMessage(BaseModel):
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class FileOperation(BaseModel):
    operation: str = Field(..., description="create, update, delete, move")
    file_path: str = Field(..., description="File path")
    content: Optional[str] = Field(None, description="File content for create/update")
    new_path: Optional[str] = Field(None, description="New path for move operation")

# Authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials.credentials

# Helper functions
def get_mkdocs_config():
    """Load MkDocs configuration"""
    try:
        with open(settings.mkdocs_config, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading MkDocs config: {e}")
        return {}

def update_mkdocs_config(config_updates: Dict):
    """Update MkDocs configuration"""
    try:
        config = get_mkdocs_config()
        
        # Deep update the config
        for key, value in config_updates.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
        
        with open(settings.mkdocs_config, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return True
    except Exception as e:
        logger.error(f"Error updating MkDocs config: {e}")
        return False

async def read_file_safe(file_path: str) -> str:
    """Safely read file content"""
    try:
        full_path = Path(settings.docs_path) / file_path
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            return await f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

async def write_file_safe(file_path: str, content: str):
    """Safely write file content"""
    try:
        full_path = Path(settings.docs_path) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False

def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extract frontmatter from markdown content"""
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if frontmatter_match:
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            body = frontmatter_match.group(2)
            return frontmatter, body
        except:
            return {}, content
    return {}, content

def generate_filename(title: str, content_type: str = "markdown") -> str:
    """Generate appropriate filename from title"""
    # Convert title to lowercase, replace spaces with dashes, remove special chars
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    
    # Add extension
    ext = '.md' if content_type == 'markdown' else '.txt'
    return filename + ext

async def call_openai_api(prompt: str, system_prompt: str = None) -> str:
    """Call OpenAI API for content generation"""
    try:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=4000,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

def git_commit(message: str):
    """Commit changes to git"""
    try:
        repo = git.Repo('.')
        repo.add(all=True)
        repo.index.commit(message)
        logger.info(f"Git commit: {message}")
    except Exception as e:
        logger.error(f"Git commit failed: {e}")

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve admin interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Content Management Admin</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }
            .card { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1rem; }
            .btn { background: #667eea; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #5a6fd8; }
            textarea { width: 100%; height: 100px; border: 1px solid #ddd; border-radius: 5px; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Content Management</h1>
                <p>Intelligent documentation creation and management</p>
            </div>
            
            <div class="card">
                <h2>Create New Content</h2>
                <textarea id="prompt" placeholder="Describe the content you want to create..."></textarea>
                <br><br>
                <button class="btn" onclick="createContent()">Generate Content</button>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function createContent() {
                const prompt = document.getElementById('prompt').value;
                const result = document.getElementById('result');
                
                if (!prompt) {
                    alert('Please enter a prompt');
                    return;
                }
                
                result.innerHTML = '<div class="card"><p>Generating content...</p></div>';
                
                try {
                    const response = await fetch('/api/content/create', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer your-secret-key-change-in-production'
                        },
                        body: JSON.stringify({
                            prompt: prompt,
                            content_type: 'markdown',
                            auto_nav: true
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        result.innerHTML = `
                            <div class="card">
                                <h3>✅ Content Created Successfully</h3>
                                <p><strong>File:</strong> ${data.file_path}</p>
                                <p><strong>Navigation Updated:</strong> ${data.navigation_updated ? 'Yes' : 'No'}</p>
                                <details>
                                    <summary>Preview Content</summary>
                                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">${data.content}</pre>
                                </details>
                            </div>
                        `;
                    } else {
                        result.innerHTML = `<div class="card"><h3>❌ Error</h3><p>${data.detail}</p></div>`;
                    }
                } catch (error) {
                    result.innerHTML = `<div class="card"><h3>❌ Error</h3><p>${error.message}</p></div>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/content/create")
async def create_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Create new content using AI"""
    try:
        # System prompt for content generation
        system_prompt = f"""
        You are an expert technical documentation writer. Create comprehensive, well-structured markdown content based on the user's request.
        
        Guidelines:
        - Use proper markdown formatting with headers, lists, code blocks, and tables
        - Include practical examples and code snippets where relevant
        - Add frontmatter with title, description, and appropriate metadata
        - Structure content logically with clear sections
        - Use emojis sparingly for visual interest
        - Include "See also" sections for related topics
        - Add troubleshooting sections where applicable
        
        Content type: {request.content_type}
        Section: {request.section or 'general'}
        """
        
        # Generate content
        content = await call_openai_api(request.prompt, system_prompt)
        
        # Determine file path
        if request.target_path:
            file_path = request.target_path
        else:
            # Generate filename from prompt
            title = request.prompt.split('.')[0] if '.' in request.prompt else request.prompt[:50]
            file_path = generate_filename(title)
            
            # Add section prefix if specified
            if request.section:
                file_path = f"{request.section}/{file_path}"
        
        # Write content to file
        success = await write_file_safe(file_path, content)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to write content file")
        
        # Update navigation if requested
        nav_updated = False
        if request.auto_nav:
            # Extract title from frontmatter or first header
            frontmatter, body = extract_frontmatter(content)
            title = frontmatter.get('title', '')
            
            if not title:
                # Extract first H1 header
                header_match = re.search(r'^# (.+)$', body, re.MULTILINE)
                if header_match:
                    title = header_match.group(1)
            
            if title:
                nav_update = {
                    "additions": [{
                        "title": title,
                        "path": file_path,
                        "section": request.section or "guides"
                    }]
                }
                nav_updated = update_navigation(nav_update)
        
        # Git commit in background
        background_tasks.add_task(
            git_commit, 
            f"AI generated content: {file_path}"
        )
        
        return {
            "message": "Content created successfully",
            "file_path": file_path,
            "content": content,
            "navigation_updated": nav_updated,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/update")
async def update_content(
    request: ContentUpdate,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Update existing content"""
    try:
        # Read existing content
        existing_content = await read_file_safe(request.file_path)
        if not existing_content:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Apply operation
        if request.operation == "append":
            updated_content = existing_content + "\n\n" + request.content
        elif request.operation == "prepend":
            updated_content = request.content + "\n\n" + existing_content
        elif request.operation == "replace":
            if request.target_section:
                # Replace specific section
                section_pattern = f"#+ {request.target_section}.*?(?=#+ |\\Z)"
                updated_content = re.sub(section_pattern, request.content, existing_content, flags=re.DOTALL)
            else:
                updated_content = request.content
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        # Write updated content
        success = await write_file_safe(request.file_path, updated_content)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update file")
        
        # Git commit
        background_tasks.add_task(
            git_commit,
            f"AI updated content: {request.file_path} ({request.operation})"
        )
        
        return {
            "message": "Content updated successfully",
            "file_path": request.file_path,
            "operation": request.operation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/navigation/update")
async def update_navigation(
    request: NavigationUpdate,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Update MkDocs navigation"""
    try:
        config = get_mkdocs_config()
        current_nav = config.get('nav', [])
        
        # Apply additions
        for addition in request.additions:
            section = addition.get('section', 'guides')
            title = addition.get('title')
            path = addition.get('path')
            
            # Find or create section
            section_found = False
            for nav_item in current_nav:
                if isinstance(nav_item, dict) and section in nav_item:
                    if isinstance(nav_item[section], list):
                        nav_item[section].append({title: path})
                    else:
                        nav_item[section] = [nav_item[section], {title: path}]
                    section_found = True
                    break
            
            if not section_found:
                current_nav.append({section: {title: path}})
        
        # Apply removals
        current_nav = [
            item for item in current_nav
            if not any(removal in str(item) for removal in request.removals)
        ]
        
        # Apply reordering
        if request.reorder:
            for section, order in request.reorder.items():
                for nav_item in current_nav:
                    if isinstance(nav_item, dict) and section in nav_item:
                        if isinstance(nav_item[section], list):
                            # Reorder based on order list
                            ordered_items = []
                            for title in order:
                                for item in nav_item[section]:
                                    if isinstance(item, dict) and title in item:
                                        ordered_items.append(item)
                            nav_item[section] = ordered_items
        
        # Update config
        config['nav'] = current_nav
        success = update_mkdocs_config({"nav": current_nav})
        
        if success:
            background_tasks.add_task(git_commit, "Updated navigation structure")
            return {"message": "Navigation updated successfully", "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=500, detail="Failed to update navigation")
            
    except Exception as e:
        logger.error(f"Error updating navigation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/chat")
async def ai_chat(
    request: AIChatMessage,
    token: str = Depends(verify_token)
):
    """AI chat interface for content assistance"""
    try:
        # Build conversation history
        messages = []
        
        if request.conversation_history:
            messages.extend(request.conversation_history)
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # System prompt
        system_prompt = """
        You are an AI assistant for managing technical documentation. Help users create, organize, and improve their documentation.
        Be helpful, concise, and provide practical suggestions.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/list")
async def list_files(
    path: str = "",
    token: str = Depends(verify_token)
):
    """List files in documentation directory"""
    try:
        docs_path = Path(settings.docs_path)
        target_path = docs_path / path if path else docs_path
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        files = []
        
        if target_path.is_dir():
            for item in target_path.iterdir():
                relative_path = item.relative_to(docs_path)
                files.append({
                    "name": item.name,
                    "path": str(relative_path),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
        
        return {"files": files, "path": path}
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/content")
async def get_file_content(
    file_path: str,
    token: str = Depends(verify_token)
):
    """Get content of a specific file"""
    try:
        content = await read_file_safe(file_path)
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        frontmatter, body = extract_frontmatter(content)
        
        return {
            "file_path": file_path,
            "frontmatter": frontmatter,
            "content": body,
            "raw_content": content
        }
        
    except Exception as e:
        logger.error(f"Error getting file content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/operation")
async def file_operation(
    request: FileOperation,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Perform file operations (create, update, delete, move)"""
    try:
        if request.operation == "create":
            success = await write_file_safe(request.file_path, request.content or "")
            message = f"Created file: {request.file_path}"
            
        elif request.operation == "update":
            success = await write_file_safe(request.file_path, request.content or "")
            message = f"Updated file: {request.file_path}"
            
        elif request.operation == "delete":
            full_path = Path(settings.docs_path) / request.file_path
            if full_path.exists():
                full_path.unlink()
                success = True
                message = f"Deleted file: {request.file_path}"
            else:
                success = False
                message = "File not found"
                
        elif request.operation == "move":
            old_path = Path(settings.docs_path) / request.file_path
            new_path = Path(settings.docs_path) / request.new_path
            
            if old_path.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
                success = True
                message = f"Moved file: {request.file_path} -> {request.new_path}"
            else:
                success = False
                message = "Source file not found"
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        if success:
            background_tasks.add_task(git_commit, message)
            return {"message": message, "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        logger.error(f"Error in file operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get documentation statistics"""
    try:
        docs_path = Path(settings.docs_path)
        
        total_files = 0
        total_size = 0
        file_types = {}
        
        for file_path in docs_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "file_types": file_types,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

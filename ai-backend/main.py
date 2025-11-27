"""
Homelab Documentation AI Backend
FastAPI service for AI-powered content generation and management
"""

import os
import logging
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
import uvicorn
import redis
import aioredis
import jwt
from passlib.context import CryptContext
import openai
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Homelab Docs AI Backend",
    description="AI-powered content management for homelab documentation",
    version="1.0.0"
)

# Security Configuration
class SecurityConfig:
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost").split(",")
    
    @classmethod
    def validate_config(cls):
        if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return True

# Validate security configuration on startup
SecurityConfig.validate_config()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Redis connection for rate limiting and session storage
redis_client: Optional[aioredis.Redis] = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = await aioredis.from_url(redis_url, decode_responses=True)
    return redis_client

# Rate Limiting Middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        endpoint = str(request.url.path)
        
        # Skip rate limiting for health checks
        if endpoint in ["/health", "/"]:
            return await call_next(request)
        
        try:
            redis_conn = await get_redis()
            key = f"rate_limit:{client_ip}:{endpoint}"
            
            # Check current count
            current = await redis_conn.get(key)
            if current is None:
                await redis_conn.setex(key, SecurityConfig.RATE_LIMIT_WINDOW, 1)
            else:
                count = int(current)
                if count >= SecurityConfig.RATE_LIMIT_REQUESTS:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"error": "Rate limit exceeded. Please try again later."}
                    )
                await redis_conn.incr(key)
                
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if Redis is unavailable
        
        response = await call_next(request)
        return response

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=SecurityConfig.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin"
    ],
)

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SECRET_KEY = SecurityConfig.SECRET_KEY
    DOCS_ROOT = Path(__file__).parent.parent / "docs"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

# Pydantic models
class ContentRequest(BaseModel):
    topic: str = Field(..., description="Topic for content generation")
    content_type: str = Field(default="guide", description="Type of content to generate")
    target_audience: str = Field(default="beginner", description="Target audience level")
    length: Optional[str] = Field(default="medium", description="Content length")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")

class AIChatRequest(BaseModel):
    message: str = Field(..., description="User message to AI")
    context: Optional[Dict[str, Any]] = Field(None, description="Context from current page")

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

# Authentication Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Management (in production, use a proper database)
users_db = {}
users_sessions = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user."""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoints
@app.post("/auth/register", response_model=dict, tags=["Authentication"])
async def register_user(user: UserCreate):
    """Register a new user."""
    try:
        # Check if user already exists
        if user.username in users_db:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Store user (in production, use proper database)
        users_db[user.username] = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        # Store refresh token
        redis_conn = await get_redis()
        await redis_conn.setex(
            f"refresh_token:{user.username}", 
            SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600, 
            refresh_token
        )
        
        return {
            "message": "User registered successfully",
            "username": user.username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login_user(user_credentials: UserLogin):
    """Authenticate user and return tokens."""
    try:
        # Verify user exists
        user = users_db.get(user_credentials.username)
        if not user or not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user["username"]})
        refresh_token = create_refresh_token(data={"sub": user["username"]})
        
        # Store refresh token
        redis_conn = await get_redis()
        await redis_conn.setex(
            f"refresh_token:{user_credentials.username}", 
            SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600, 
            refresh_token
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/refresh", response_model=dict, tags=["Authentication"])
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Check if refresh token exists in Redis
        redis_conn = await get_redis()
        stored_token = await redis_conn.get(f"refresh_token:{username}")
        
        if stored_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Generate new access token
        access_token = create_access_token(data={"sub": username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/logout", tags=["Authentication"])
async def logout_user(current_user: dict = Depends(get_current_active_user)):
    """Logout user and invalidate tokens."""
    try:
        # Remove refresh token from Redis
        redis_conn = await get_redis()
        await redis_conn.delete(f"refresh_token:{current_user['username']}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
async def generate_content(request: ContentRequest, current_user: dict = Depends(get_current_active_user)):
    """Generate AI-powered content"""
    try:
        if not Config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured"
            )
        
        # Configure OpenAI client
        openai.api_key = Config.OPENAI_API_KEY
        
        # Build prompt based on request parameters
        prompt = f"""Create a comprehensive technical documentation guide about "{request.topic}" for a {request.target_audience} audience.
        
Content type: {request.content_type}
Desired length: {request.length}

{f"Additional context: {request.additional_context}" if request.additional_context else ""}

Please create well-structured markdown content that includes:
1. Clear overview and objectives
2. Key concepts and terminology
3. Step-by-step implementation instructions
4. Code examples where appropriate
5. Best practices and common pitfalls
6. Related topics and further reading

Format the response in clean markdown with proper headers, code blocks, and formatting."""
        
        # Call OpenAI API with retry logic
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10)
        )
        async def call_openai():
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical documentation writer. Create clear, accurate, and well-structured documentation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            return response.choices[0].message.content
        
        # Generate content
        content = await call_openai()
        
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

@app.post("/api/ai/chat", tags=["AI Chat"])
async def ai_chat(request: AIChatRequest, current_user: dict = Depends(get_current_active_user)):
    """AI chat endpoint for real-time assistance"""
    try:
        if not Config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured"
            )
        
        # Configure OpenAI client
        openai.api_key = Config.OPENAI_API_KEY
        
        # Build context-aware prompt
        context_info = ""
        if request.context:
            context_info = f"""
Current Page Context:
- Page: {request.context.get('page_title', 'Unknown')}
- URL: {request.context.get('page_url', '/')}
- Section Headings: {request.context.get('headings', 'None')}

"""
        
        # Build system message for homelab assistance
        system_message = """You are an expert homelab assistant specializing in:
- Docker containerization and orchestration
- Network configuration and security
- Storage solutions (ZFS, NAS, RAID)
- Virtualization (KVM, VMware, LXC)
- Monitoring and logging (Prometheus, Grafana, ELK)
- Security best practices
- System administration
- Cloud services integration

Provide concise, practical, and accurate advice. Include specific commands, configurations, or step-by-step instructions when relevant. Focus on homelab and self-hosted solutions."""

        # Build conversation history (simplified for now)
        messages = [
            {"role": "system", "content": system_message},
        ]
        
        # Add context if available
        if context_info:
            messages.append({
                "role": "system", 
                "content": context_info + "\nUser is asking about something related to the above context."
            })
        
        # Add user message
        messages.append({
            "role": "user", 
            "content": request.message
        })
        
        # Call OpenAI API with retry logic
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10)
        )
        async def call_openai():
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,  # Shorter responses for chat
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            return response.choices[0].message.content
        
        # Generate response
        response_content = await call_openai()
        
        # Log the interaction for monitoring
        logger.info(f"AI Chat - User: {current_user['username']}, Message: {request.message[:100]}...")
        
        return {
            "response": response_content,
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user['username']
        }
        
    except Exception as e:
        logger.error(f"AI Chat error: {e}")
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

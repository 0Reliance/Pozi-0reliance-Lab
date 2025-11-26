"""
Comprehensive Test Suite for AI Backend
Tests authentication, content generation, file management, and security
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import jwt
import time
from datetime import datetime, timedelta

# Import the main application
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-backend'))
from main import app, SecurityConfig, users_db, get_password_hash

# Test client
client = TestClient(app)

class TestAuthentication:
    """Test authentication endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Clear users database before each test
        users_db.clear()
    
    def test_register_user_success(self):
        """Test successful user registration"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_user(self):
        """Test registration with duplicate username"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # Register first user
        client.post("/auth/register", json=user_data)
        
        # Try to register same username again
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login"""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.post("/api/generate", json={
            "topic": "test",
            "content_type": "guide"
        })
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        
        # Access protected endpoint with token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/files", headers=headers)
        assert response.status_code == 200

class TestContentGeneration:
    """Test content generation endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/auth/register", json=user_data)
        self.auth_headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    
    @patch('main.openai.ChatCompletion.acreate')
    async def test_generate_content_success(self, mock_openai):
        """Test successful content generation"""
        # Mock OpenAI response
        mock_response = AsyncMock()
        mock_response.choices = [
            type('Choice', (), {'message': type('Message', (), {'content': '# Test Guide\n\nThis is a test guide.'})()})
        ]
        mock_openai.return_value = mock_response
        
        request_data = {
            "topic": "Docker Basics",
            "content_type": "guide",
            "target_audience": "beginner"
        }
        
        response = client.post("/api/generate", json=request_data, headers=self.auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        assert "metadata" in data
        assert "suggestions" in data
        assert data["metadata"]["topic"] == "Docker Basics"
    
    def test_generate_content_without_api_key(self):
        """Test content generation without OpenAI API key"""
        # Temporarily unset API key
        original_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        
        try:
            request_data = {
                "topic": "Docker Basics",
                "content_type": "guide"
            }
            
            response = client.post("/api/generate", json=request_data, headers=self.auth_headers)
            assert response.status_code == 503
            assert "OpenAI API key not configured" in response.json()["detail"]
        finally:
            # Restore original key
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

class TestFileManagement:
    """Test file management endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/auth/register", json=user_data)
        self.auth_headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    
    def test_list_files_success(self):
        """Test successful file listing"""
        response = client.get("/api/files", headers=self.auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert "path" in data
        assert isinstance(data["files"], list)
    
    def test_list_files_invalid_path(self):
        """Test file listing with invalid path"""
        response = client.get("/api/files?path=nonexistent", headers=self.auth_headers)
        assert response.status_code == 404
    
    def test_create_file_success(self):
        """Test successful file creation"""
        file_data = {
            "action": "create",
            "path": "test-document.md",
            "content": "# Test Document\n\nThis is a test document."
        }
        
        response = client.post("/api/files", json=file_data, headers=self.auth_headers)
        assert response.status_code == 200
        assert "Successfully created" in response.json()["message"]
    
    def test_delete_file_success(self):
        """Test successful file deletion"""
        # First create a file
        file_data = {
            "action": "create",
            "path": "test-delete.md",
            "content": "# Test Document\n\nThis will be deleted."
        }
        client.post("/api/files", json=file_data, headers=self.auth_headers)
        
        # Now delete it
        delete_data = {
            "action": "delete",
            "path": "test-delete.md"
        }
        
        response = client.post("/api/files", json=delete_data, headers=self.auth_headers)
        assert response.status_code == 200
        assert "Deleted test-delete.md" in response.json()["message"]

class TestSecurity:
    """Test security features"""
    
    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        # Create an invalid token
        invalid_token = "invalid.jwt.token"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        response = client.get("/api/files", headers=headers)
        assert response.status_code == 401
    
    def test_expired_token(self):
        """Test expired JWT token"""
        # Create an expired token
        expired_payload = {
            "sub": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            "type": "access"
        }
        expired_token = jwt.encode(
            expired_payload, 
            SecurityConfig.SECRET_KEY, 
            algorithm=SecurityConfig.ALGORITHM
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/files", headers=headers)
        assert response.status_code == 401
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/auth/register", json=user_data)
        headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
        
        # Make multiple rapid requests
        responses = []
        for _ in range(105):  # Above the rate limit
            response = client.get("/api/files", headers=headers)
            responses.append(response.status_code)
        
        # Should eventually get rate limited
        assert 429 in responses

class TestNavigation:
    """Test navigation management endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/auth/register", json=user_data)
        self.auth_headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    
    def test_get_navigation(self):
        """Test getting navigation structure"""
        response = client.get("/api/navigation", headers=self.auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "navigation" in data
        assert "index" in data["navigation"]
        assert "homelab" in data["navigation"]
    
    def test_update_navigation(self):
        """Test updating navigation structure"""
        nav_update = {
            "section": "homelab",
            "action": "add",
            "item": {
                "title": "New Section",
                "path": "/homelab/new-section/"
            }
        }
        
        response = client.post("/api/navigation", json=nav_update, headers=self.auth_headers)
        assert response.status_code == 200
        assert "Navigation add for homelab" in response.json()["message"]

class TestStatistics:
    """Test statistics endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = client.post("/auth/register", json=user_data)
        self.auth_headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
    
    def test_get_statistics(self):
        """Test getting documentation statistics"""
        response = client.get("/api/stats", headers=self.auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_files" in data
        assert "total_size" in data
        assert "content_types" in data
        assert isinstance(data["total_files"], int)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

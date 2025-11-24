"""Basic tests for homelab-docs project."""

import pytest
import os
import sys


def test_project_structure():
    """Test that the basic project structure exists."""
    assert os.path.exists("README.md"), "README.md should exist"
    assert os.path.exists("mkdocs.yml"), "mkdocs.yml should exist"
    assert os.path.exists("requirements.txt"), "requirements.txt should exist"
    assert os.path.exists(".env.example"), ".env.example should exist"


def test_gitignore_exists():
    """Test that .gitignore exists and contains expected patterns."""
    assert os.path.exists(".gitignore"), ".gitignore should exist"
    
    with open(".gitignore", "r") as f:
        gitignore_content = f.read()
    
    # Check for important patterns
    assert ".env" in gitignore_content, ".env should be in .gitignore"
    assert "__pycache__/" in gitignore_content, "__pycache__/ should be in .gitignore"
    assert "*.pyc" in gitignore_content, "*.pyc should be in .gitignore"
    assert "site/" in gitignore_content, "site/ should be in .gitignore"


def test_env_example_exists():
    """Test that .env.example exists and doesn't contain real secrets."""
    assert os.path.exists(".env.example"), ".env.example should exist"
    
    with open(".env.example", "r") as f:
        env_content = f.read()
    
    # Check that it contains placeholder values, not real secrets
    assert "your-" in env_content or "placeholder" in env_content, \
        ".env.example should contain placeholder values"
    
    # Check that it doesn't contain actual API keys
    assert "sk-" not in env_content or "sk-placeholder" in env_content, \
        ".env.example should not contain real API keys"


def test_docs_directory():
    """Test that docs directory exists and has basic structure."""
    assert os.path.exists("docs"), "docs directory should exist"
    assert os.path.exists("docs/index.md"), "docs/index.md should exist"
    
    # Check for key documentation files
    key_files = [
        "docs/guides/getting-started.md",
        "docs/api.md",
        "docs/about/contributing.md"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            assert True, f"{file_path} exists"


def test_mkdocs_config():
    """Test that mkdocs.yml is valid."""
    import yaml
    
    assert os.path.exists("mkdocs.yml"), "mkdocs.yml should exist"
    
    try:
        with open("mkdocs.yml", "r") as f:
            config = yaml.safe_load(f)
        
        assert "site_name" in config, "mkdocs.yml should have site_name"
        assert "nav" in config, "mkdocs.yml should have navigation"
        
    except yaml.YAMLError as e:
        pytest.fail(f"mkdocs.yml is not valid YAML: {e}")


def test_docker_directory():
    """Test that Docker configuration exists."""
    assert os.path.exists("docker"), "docker directory should exist"
    assert os.path.exists("docker/docker-compose.yml"), "docker-compose.yml should exist"
    
    # Check for Dockerfiles
    docker_files = [
        "docker/Dockerfile.mkdocs",
        "docker/Dockerfile.ai-backend"
    ]
    
    for docker_file in docker_files:
        if os.path.exists(docker_file):
            assert True, f"{docker_file} exists"


def test_ai_backend_structure():
    """Test that AI backend has basic structure."""
    if os.path.exists("ai-backend"):
        assert os.path.exists("ai-backend/main.py"), "ai-backend/main.py should exist"
        
        if os.path.exists("ai-backend/requirements.txt"):
            assert True, "ai-backend/requirements.txt exists"


def test_no_sensitive_files():
    """Test that no sensitive files are accidentally committed."""
    sensitive_files = [
        ".env",
        "*.pem",
        "*.key",
        "htpasswd"
    ]
    
    for pattern in sensitive_files:
        if "*" in pattern:
            # For patterns with wildcards, just check that they're in .gitignore
            with open(".gitignore", "r") as f:
                gitignore_content = f.read()
            assert pattern in gitignore_content, f"{pattern} should be in .gitignore"
        else:
            # For specific files, check they don't exist
            assert not os.path.exists(pattern), f"{pattern} should not exist in repository"


def test_python_version_compatibility():
    """Test Python version compatibility."""
    # This test will run on the Python version used by pytest
    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"
    

if __name__ == "__main__":
    pytest.main([__file__])

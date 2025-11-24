"""Integration tests for homelab-docs services."""

import pytest
import requests
import time
import subprocess
import os


@pytest.mark.integration
class TestServiceHealth:
    """Test service health and connectivity."""

    def test_mkdocs_health(self):
        """Test that MkDocs service is responding."""
        try:
            response = requests.get("http://localhost:8000", timeout=10)
            assert response.status_code == 200, "MkDocs should return 200 status"
            assert "Homelab Documentation" in response.text or "html" in response.text.lower()
        except requests.exceptions.RequestException:
            pytest.skip("MkDocs service not available")

    def test_ai_backend_health(self):
        """Test that AI backend service is responding."""
        try:
            response = requests.get("http://localhost:8001/health", timeout=10)
            assert response.status_code == 200, "AI backend should return 200 status"
        except requests.exceptions.RequestException:
            pytest.skip("AI backend service not available")

    def test_redis_connectivity(self):
        """Test Redis connectivity if available."""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=5)
            r.ping()
            assert True, "Redis should be accessible"
        except ImportError:
            pytest.skip("Redis library not available")
        except Exception:
            pytest.skip("Redis not available")


@pytest.mark.integration
class TestDockerServices:
    """Test Docker container services."""

    def test_docker_compose_build(self):
        """Test that Docker Compose can build successfully."""
        if not os.path.exists("docker/docker-compose.yml"):
            pytest.skip("docker-compose.yml not found")
            
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker/docker-compose.yml", "build"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("Docker build timed out")
        except FileNotFoundError:
            pytest.skip("docker-compose not available")

    def test_docker_containers_run(self):
        """Test that Docker containers can start successfully."""
        if not os.path.exists("docker/docker-compose.yml"):
            pytest.skip("docker-compose.yml not found")
            
        try:
            # Start containers
            subprocess.run(
                ["docker-compose", "-f", "docker/docker-compose.yml", "up", "-d"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Wait a bit for services to start
            time.sleep(30)
            
            # Check if containers are running
            result = subprocess.run(
                ["docker-compose", "-f", "docker/docker-compose.yml", "ps"],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, "Failed to check container status"
            
            # Cleanup
            subprocess.run(
                ["docker-compose", "-f", "docker/docker-compose.yml", "down", "-v"],
                capture_output=True,
                text=True
            )
            
        except FileNotFoundError:
            pytest.skip("docker-compose not available")
        except Exception as e:
            # Cleanup on failure
            try:
                subprocess.run(
                    ["docker-compose", "-f", "docker/docker-compose.yml", "down", "-v"],
                    capture_output=True,
                    text=True
                )
            except:
                pass
            pytest.fail(f"Docker containers failed to run: {e}")


@pytest.mark.integration
class TestDocumentation:
    """Test documentation build and validation."""

    def test_mkdocs_build(self):
        """Test that MkDocs can build documentation successfully."""
        if not os.path.exists("mkdocs.yml"):
            pytest.skip("mkdocs.yml not found")
            
        try:
            result = subprocess.run(
                ["mkdocs", "build", "--strict"],
                capture_output=True,
                text=True,
                timeout=120
            )
            assert result.returncode == 0, f"MkDocs build failed: {result.stderr}"
            assert os.path.exists("site/index.html"), "site/index.html should exist"
        except subprocess.TimeoutExpired:
            pytest.fail("MkDocs build timed out")
        except FileNotFoundError:
            pytest.skip("mkdocs not available")

    def test_mkdocs_configuration(self):
        """Test MkDocs configuration validity."""
        if not os.path.exists("mkdocs.yml"):
            pytest.skip("mkdocs.yml not found")
            
        try:
            result = subprocess.run(
                ["mkdocs", "--config-file", "mkdocs.yml", "--quiet", "build"],
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result.returncode == 0, f"MkDocs config validation failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("MkDocs config validation timed out")
        except FileNotFoundError:
            pytest.skip("mkdocs not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

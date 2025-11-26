"""
AI Backend Connection Manager
Handles connection pooling and optimization for external API calls
"""

import aiohttp
import asyncio
import logging
import os
from typing import Optional, Dict, Any
import time

logger = logging.getLogger(__name__)

class OpenAIConnectionPool:
    """
    Manages HTTP connections to OpenAI API with connection pooling and optimization
    """
    
    def __init__(self, max_connections: int = 10, timeout: int = 30):
        self.max_connections = max_connections
        self.timeout = timeout
        self.connector = None
        self.session = None
        self._stats = {
            'requests_made': 0,
            'connection_reuses': 0,
            'connection_creates': 0,
            'total_response_time': 0.0
        }
    
    async def initialize(self):
        """Initialize the connection pool"""
        self.connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=self.max_connections,
            ttl_dns_cache=300,  # 5 minutes DNS cache
            use_dns_cache=True,
            keepalive_timeout=30,  # 30 seconds keepalive
            enable_cleanup_closed=True,
            force_close=False,  # Allow connection reuse
            ssl=False  # Let aiohttp handle SSL
        )
        
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Homelab-Docs/1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
        )
        
        logger.info(f"Connection pool initialized with max {self.max_connections} connections")
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create a session"""
        if self.session is None or self.session.closed:
            await self.initialize()
            self._stats['connection_creates'] += 1
        else:
            self._stats['connection_reuses'] += 1
        
        return self.session
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with timing and error handling
        """
        start_time = time.time()
        session = await self.get_session()
        
        try:
            self._stats['requests_made'] += 1
            
            async with session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                self._stats['total_response_time'] += response_time
                
                # Log slow requests
                if response_time > 5.0:
                    logger.warning(f"Slow request detected: {response_time:.2f}s to {url}")
                
                # Handle response
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'data': result,
                        'status_code': response.status,
                        'response_time': response_time,
                        'headers': dict(response.headers)
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    return {
                        'success': False,
                        'error': error_text,
                        'status_code': response.status,
                        'response_time': response_time
                    }
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout to {url}")
            return {
                'success': False,
                'error': 'Request timeout',
                'status_code': 408,
                'response_time': time.time() - start_time
            }
        
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 500,
                'response_time': time.time() - start_time
            }
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 500,
                'response_time': time.time() - start_time
            }
    
    async def close(self):
        """Close all connections and cleanup"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        if self.connector:
            await self.connector.close()
        
        logger.info("Connection pool closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        avg_response_time = (
            self._stats['total_response_time'] / self._stats['requests_made']
            if self._stats['requests_made'] > 0 else 0
        )
        
        return {
            'requests_made': self._stats['requests_made'],
            'connection_reuses': self._stats['connection_reuses'],
            'connection_creates': self._stats['connection_creates'],
            'average_response_time': avg_response_time,
            'total_response_time': self._stats['total_response_time'],
            'reuse_ratio': (
                self._stats['connection_reuses'] / max(1, self._stats['requests_made'])
            )
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self._stats = {
            'requests_made': 0,
            'connection_reuses': 0,
            'connection_creates': 0,
            'total_response_time': 0.0
        }

# Global connection pool instance
_connection_pool: Optional[OpenAIConnectionPool] = None

async def get_connection_pool() -> OpenAIConnectionPool:
    """Get or create the global connection pool"""
    global _connection_pool
    
    if _connection_pool is None:
        _connection_pool = OpenAIConnectionPool(
            max_connections=int(os.getenv('MAX_CONNECTIONS', '10')),
            timeout=int(os.getenv('REQUEST_TIMEOUT', '30'))
        )
        await _connection_pool.initialize()
    
    return _connection_pool

async def close_connection_pool():
    """Close the global connection pool"""
    global _connection_pool
    
    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None

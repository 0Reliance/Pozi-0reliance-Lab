"""
AI Backend Request Deduplicator
Prevents duplicate AI requests by batching identical requests
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from typing import Dict, Any, Optional, List
logger = logging.getLogger(__name__)

class RequestDeduplicator:
    """
    Deduplicates identical AI requests to prevent redundant API calls
    """
    
    def __init__(self, request_timeout: int = 300, max_pending: int = 100):
        self.request_timeout = request_timeout  # 5 minutes default
        self.max_pending = max_pending
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.request_stats: Dict[str, Dict[str, Any]] = {}
        self._cleanup_task = None
        self._cleanup_interval = 60  # Cleanup every minute
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_requests())
    
    async def _cleanup_expired_requests(self):
        """Clean up expired requests"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                current_time = time.time()
                expired_keys = []
                
                for key, future in self.pending_requests.items():
                    # Check if request has timed out
                    request_age = current_time - self.request_stats.get(key, {}).get('start_time', current_time)
                    if request_age > self.request_timeout or future.done():
                        expired_keys.append(key)
                
                # Clean up expired requests
                for key in expired_keys:
                    if key in self.pending_requests:
                        future = self.pending_requests.pop(key)
                        
                        # Cancel if not done
                        if not future.done():
                            future.cancel()
                            logger.debug(f"Cancelled expired request: {key}")
                        
                        # Clean up stats
                        self.request_stats.pop(key, None)
                
                # Warn if too many pending requests
                if len(self.pending_requests) > self.max_pending * 0.8:
                    logger.warning(f"High number of pending requests: {len(self.pending_requests)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
    
    def _get_request_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate unique key for request deduplication"""
        # Normalize prompt for better deduplication
        normalized_prompt = prompt.strip().lower()
        
        # Include relevant parameters in key
        params = {
            'prompt': normalized_prompt,
            'model': model,
            'max_tokens': kwargs.get('max_tokens', 1000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        # Create deterministic key
        key_data = json.dumps(params, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def execute_or_wait(self, prompt: str, model: str, coro, **kwargs) -> Any:
        """
        Execute coroutine or wait for existing identical request
        """
        key = self._get_request_key(prompt, model, **kwargs)
        
        # Check if identical request is already pending
        if key in self.pending_requests:
            stats = self.request_stats.get(key, {})
            stats['wait_count'] = stats.get('wait_count', 0) + 1
            self.request_stats[key] = stats
            
            logger.debug(f"Waiting for existing request: {key[:16]}...")
            try:
                result = await self.pending_requests[key]
                logger.debug(f"Received result from existing request: {key[:16]}...")
                return result
            except Exception as e:
                # If existing request failed, remove it and retry
                logger.warning(f"Existing request failed, retrying: {key[:16]}... - {e}")
                self.pending_requests.pop(key, None)
                self.request_stats.pop(key, None)
                return await self.execute_or_wait(prompt, model, coro, **kwargs)
        
        # Create new request
        if len(self.pending_requests) >= self.max_pending:
            logger.error(f"Too many pending requests: {len(self.pending_requests)}")
            raise Exception("Too many pending requests")
        
        # Create future and store it
        future = asyncio.create_task(self._execute_with_tracking(key, coro))
        self.pending_requests[key] = future
        self.request_stats[key] = {
            'start_time': time.time(),
            'prompt_preview': prompt[:50] + "..." if len(prompt) > 50 else prompt,
            'model': model,
            'wait_count': 0
        }
        
        try:
            result = await future
            return result
        finally:
            # Clean up
            self.pending_requests.pop(key, None)
            stats = self.request_stats.pop(key, {})
            duration = time.time() - stats.get('start_time', time.time())
            logger.debug(f"Request completed: {key[:16]}... in {duration:.2f}s")
    
    async def _execute_with_tracking(self, key: str, coro) -> Any:
        """Execute coroutine with tracking"""
        try:
            result = await coro
            return result
        except Exception as e:
            logger.error(f"Request execution failed: {key[:16]}... - {e}")
            raise
    
    async def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get information about pending requests"""
        current_time = time.time()
        pending_info = []
        
        for key, future in self.pending_requests.items():
            stats = self.request_stats.get(key, {})
            age = current_time - stats.get('start_time', current_time)
            
            pending_info.append({
                'key': key[:16] + "...",  # Truncated for security
                'age_seconds': age,
                'prompt_preview': stats.get('prompt_preview', 'Unknown'),
                'model': stats.get('model', 'Unknown'),
                'wait_count': stats.get('wait_count', 0),
                'is_done': future.done()
            })
        
        return pending_info
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        total_requests = sum(stats.get('wait_count', 0) for stats in self.request_stats.values())
        unique_requests = len(self.request_stats)
        duplicates_prevented = total_requests - unique_requests
        
        return {
            'pending_requests': len(self.pending_requests),
            'unique_requests': unique_requests,
            'total_duplicates_prevented': duplicates_prevented,
            'duplicate_prevention_rate': (
                duplicates_prevented / max(1, total_requests)
            ),
            'max_pending_reached': len(self.pending_requests) >= self.max_pending
        }
    
    async def cancel_request(self, prompt: str, model: str, **kwargs) -> bool:
        """Cancel a specific request"""
        key = self._get_request_key(prompt, model, **kwargs)
        
        if key in self.pending_requests:
            future = self.pending_requests.pop(key)
            self.request_stats.pop(key, None)
            
            if not future.done():
                future.cancel()
                logger.info(f"Cancelled request: {key[:16]}...")
                return True
        
        return False
    
    async def cancel_all_requests(self):
        """Cancel all pending requests"""
        cancelled_count = 0
        
        for key, future in list(self.pending_requests.items()):
            if not future.done():
                future.cancel()
                cancelled_count += 1
        
        self.pending_requests.clear()
        self.request_stats.clear()
        
        logger.info(f"Cancelled {cancelled_count} pending requests")
        return cancelled_count
    
    async def shutdown(self):
        """Shutdown the deduplicator"""
        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all pending requests
        await self.cancel_all_requests()
        
        logger.info("Request deduplicator shutdown complete")

# Global deduplicator instance
_deduplicator: Optional[RequestDeduplicator] = None

async def get_deduplicator() -> RequestDeduplicator:
    """Get or create global deduplicator instance"""
    global _deduplicator
    
    if _deduplicator is None:
        _deduplicator = RequestDeduplicator(
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '300')),
            max_pending=int(os.getenv('MAX_PENDING_REQUESTS', '100'))
        )
    
    return _deduplicator

async def close_deduplicator():
    """Close global deduplicator instance"""
    global _deduplicator
    
    if _deduplicator:
        await _deduplicator.shutdown()
        _deduplicator = None

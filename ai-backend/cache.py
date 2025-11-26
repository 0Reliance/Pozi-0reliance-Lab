"""
AI Backend Response Cache
Implements intelligent caching for AI responses to improve performance and reduce costs
"""

import redis
import json
import hashlib
import logging
from typing import Optional, Dict, Any, List
import time
import os

logger = logging.getLogger(__name__)

class AIResponseCache:
    """
    Intelligent caching system for AI responses with TTL and similarity matching
    """
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis = None
        self.default_ttl = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour default
        self.similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', '0.85'))
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_sets': 0,
            'cache_errors': 0
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            import aioredis
            self.redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("AI Response Cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            self.redis = None
    
    def _get_cache_key(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Generate cache key for prompt and model"""
        # Create a normalized prompt for better caching
        normalized_prompt = prompt.strip().lower()
        content = f"{normalized_prompt}:{model}"
        return f"ai_response:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _get_similarity_key(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Generate key for similarity search"""
        normalized_prompt = prompt.strip().lower()
        content = f"similarity:{normalized_prompt}:{model}"
        return f"ai_similarity:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def get(self, prompt: str, model: str = "gpt-3.5-turbo") -> Optional[str]:
        """
        Get cached response for exact match
        """
        if not self.redis:
            return None
        
        try:
            key = self._get_cache_key(prompt, model)
            cached = await self.redis.get(key)
            
            if cached:
                self._stats['cache_hits'] += 1
                logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
                return json.loads(cached)
            else:
                self._stats['cache_misses'] += 1
                return None
                
        except Exception as e:
            self._stats['cache_errors'] += 1
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, prompt: str, response: str, model: str = "gpt-3.5-turbo", ttl: int = None):
        """
        Cache response with TTL
        """
        if not self.redis:
            return
        
        try:
            key = self._get_cache_key(prompt, model)
            ttl = ttl or self.default_ttl
            
            # Store the response
            await self.redis.setex(key, ttl, json.dumps(response))
            
            # Also store for similarity matching
            similarity_key = self._get_similarity_key(prompt, model)
            similarity_data = {
                'prompt': prompt,
                'response': response,
                'timestamp': time.time()
            }
            await self.redis.setex(similarity_key, ttl * 2, json.dumps(similarity_data))  # Longer TTL for similarity
            
            self._stats['cache_sets'] += 1
            logger.debug(f"Cached response for prompt: {prompt[:50]}...")
            
        except Exception as e:
            self._stats['cache_errors'] += 1
            logger.error(f"Cache set error: {e}")
    
    async def get_similar(self, prompt: str, model: str = "gpt-3.5-turbo", max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Get similar cached responses using simple keyword matching
        """
        if not self.redis:
            return []
        
        try:
            # Get all similarity keys for this model
            pattern = f"ai_similarity:*:{model}"
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return []
            
            similar_responses = []
            prompt_words = set(prompt.lower().split())
            
            for key in keys[:100]:  # Limit to prevent excessive processing
                try:
                    cached_data = await self.redis.get(key)
                    if cached_data:
                        data = json.loads(cached_data)
                        cached_prompt = data.get('prompt', '').lower()
                        
                        # Simple keyword similarity
                        cached_words = set(cached_prompt.split())
                        
                        # Calculate Jaccard similarity
                        intersection = len(prompt_words.intersection(cached_words))
                        union = len(prompt_words.union(cached_words))
                        similarity = intersection / union if union > 0 else 0
                        
                        if similarity >= self.similarity_threshold:
                            similar_responses.append({
                                'response': data.get('response'),
                                'similarity': similarity,
                                'prompt': data.get('prompt'),
                                'timestamp': data.get('timestamp')
                            })
                
                except Exception as e:
                    logger.debug(f"Error processing similarity key {key}: {e}")
                    continue
            
            # Sort by similarity and return top results
            similar_responses.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_responses[:max_results]
            
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    async def invalidate(self, prompt: str, model: str = "gpt-3.5-turbo"):
        """
        Invalidate cached response for a prompt
        """
        if not self.redis:
            return
        
        try:
            key = self._get_cache_key(prompt, model)
            similarity_key = self._get_similarity_key(prompt, model)
            
            await self.redis.delete(key)
            await self.redis.delete(similarity_key)
            
            logger.debug(f"Invalidated cache for prompt: {prompt[:50]}...")
            
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
    
    async def clear_all(self):
        """
        Clear all cached responses
        """
        if not self.redis:
            return
        
        try:
            # Delete all AI response keys
            patterns = ["ai_response:*", "ai_similarity:*"]
            
            for pattern in patterns:
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            
            logger.info("Cleared all cached AI responses")
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        stats = self._stats.copy()
        
        if self.redis:
            try:
                # Get Redis info
                info = await self.redis.info()
                stats.update({
                    'redis_memory_used': info.get('used_memory_human', 'unknown'),
                    'redis_connected_clients': info.get('connected_clients', 0),
                    'redis_total_commands': info.get('total_commands_processed', 0)
                })
                
                # Get cache size
                response_keys = await self.redis.keys("ai_response:*")
                similarity_keys = await self.redis.keys("ai_similarity:*")
                stats.update({
                    'cached_responses': len(response_keys),
                    'cached_similarities': len(similarity_keys),
                    'total_cached_items': len(response_keys) + len(similarity_keys)
                })
                
                # Calculate hit rate
                total_requests = stats['cache_hits'] + stats['cache_misses']
                stats['hit_rate'] = (
                    stats['cache_hits'] / total_requests
                    if total_requests > 0 else 0
                )
                
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")
        
        return stats
    
    def reset_stats(self):
        """Reset statistics"""
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_sets': 0,
            'cache_errors': 0
        }
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("AI Response Cache closed")

# Global cache instance
_cache: Optional[AIResponseCache] = None

async def get_cache() -> AIResponseCache:
    """Get or create global cache instance"""
    global _cache
    
    if _cache is None:
        _cache = AIResponseCache()
        await _cache.initialize()
    
    return _cache

async def close_cache():
    """Close global cache instance"""
    global _cache
    
    if _cache:
        await _cache.close()
        _cache = None

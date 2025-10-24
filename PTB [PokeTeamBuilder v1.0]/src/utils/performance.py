"""
Performance optimization utilities for Pokemon Team Builder.
Provides caching, memory management, and performance monitoring.
"""

import functools
import logging
import time
import gc
from typing import Any, Callable, Dict, Optional
from collections import OrderedDict
import weakref

logger = logging.getLogger(__name__)

class PerformanceCache:
    """Advanced caching system with size limits and TTL."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        current_time = time.time()
        
        if key in self.cache:
            # Check if item has expired
            if current_time - self.timestamps[key] > self.ttl:
                self._remove(key)
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            logger.debug(f"Cache hit for key: {key}")
            return self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        current_time = time.time()
        
        if key in self.cache:
            # Update existing item
            self.cache[key] = value
            self.timestamps[key] = current_time
            self.cache.move_to_end(key)
        else:
            # Add new item
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = next(iter(self.cache))
                self._remove(oldest_key)
            
            self.cache[key] = value
            self.timestamps[key] = current_time
    
    def _remove(self, key: str) -> None:
        """Remove item from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Performance cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl': self.ttl
        }

class WeakValueCache:
    """Cache that allows garbage collection of unused objects."""
    
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
        self.access_count = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from weak cache."""
        if key in self._cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in weak cache."""
        self._cache[key] = value
        self.access_count[key] = 1
    
    def cleanup(self) -> int:
        """Clean up stale access counts."""
        # Remove access counts for objects that have been garbage collected
        current_keys = set(self._cache.keys())
        stale_keys = set(self.access_count.keys()) - current_keys
        
        for key in stale_keys:
            del self.access_count[key]
        
        return len(stale_keys)

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        memory_before = gc.get_count()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 0.1:  # Log slow operations
                logger.warning(f"Slow operation: {func.__name__} took {execution_time:.3f}s")
            else:
                logger.debug(f"Function {func.__name__} executed in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def memory_efficient_batch_process(items, batch_size: int = 100, process_func: Callable = None):
    """Process items in batches to reduce memory usage."""
    if not process_func:
        return items
    
    results = []
    total_items = len(items)
    
    logger.info(f"Processing {total_items} items in batches of {batch_size}")
    
    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        batch_results = [process_func(item) for item in batch]
        results.extend(batch_results)
        
        # Force garbage collection after each batch
        if i % (batch_size * 5) == 0:  # Every 5 batches
            gc.collect()
            logger.debug(f"Processed {i + len(batch)}/{total_items} items")
    
    logger.info(f"Batch processing completed: {total_items} items processed")
    return results

class MemoryManager:
    """Memory management utilities."""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, int]:
        """Get current memory usage statistics."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def force_cleanup():
        """Force garbage collection and cleanup."""
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")
        return collected
    
    @staticmethod
    def log_memory_usage(operation: str = ""):
        """Log current memory usage."""
        try:
            usage = MemoryManager.get_memory_usage()
            logger.info(f"Memory usage {operation}: {usage['rss'] // 1024 // 1024}MB RSS, {usage['percent']:.1f}%")
        except ImportError:
            logger.debug("psutil not available for memory monitoring")

# Global cache instances
pokemon_cache = PerformanceCache(max_size=500, ttl=1800)  # 30 minutes
move_cache = PerformanceCache(max_size=1000, ttl=3600)    # 1 hour
type_cache = PerformanceCache(max_size=200, ttl=7200)     # 2 hours
team_cache = WeakValueCache()

def cached_pokemon_lookup(species_id: int):
    """Cached Pokemon species lookup."""
    cache_key = f"pokemon_{species_id}"
    
    # Try cache first
    cached_result = pokemon_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Load from database
    try:
        from config.game_config import GameConfig
        import json
        
        if GameConfig.POKEMON_DATABASE.exists():
            with open(GameConfig.POKEMON_DATABASE, 'r') as f:
                pokemon_data = json.load(f)
            
            if str(species_id) in pokemon_data:
                result = pokemon_data[str(species_id)]
                pokemon_cache.set(cache_key, result)
                return result
    
    except Exception as e:
        logger.error(f"Failed to load Pokemon {species_id}: {e}")
    
    return None

def cached_move_lookup(move_name: str):
    """Cached move lookup."""
    cache_key = f"move_{move_name.lower()}"
    
    # Try cache first
    cached_result = move_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Load from database
    try:
        from config.game_config import GameConfig
        import json
        
        if GameConfig.MOVES_DATABASE.exists():
            with open(GameConfig.MOVES_DATABASE, 'r') as f:
                moves_data = json.load(f)
            
            if move_name in moves_data:
                result = moves_data[move_name]
                move_cache.set(cache_key, result)
                return result
    
    except Exception as e:
        logger.error(f"Failed to load move {move_name}: {e}")
    
    return None

def get_cache_statistics() -> Dict[str, Any]:
    """Get statistics for all caches."""
    return {
        'pokemon_cache': pokemon_cache.get_stats(),
        'move_cache': move_cache.get_stats(),
        'type_cache': type_cache.get_stats(),
        'team_cache_size': len(team_cache._cache),
        'team_cache_access_count': len(team_cache.access_count)
    }

def clear_all_caches():
    """Clear all performance caches."""
    pokemon_cache.clear()
    move_cache.clear()
    type_cache.clear()
    team_cache.cleanup()
    logger.info("All performance caches cleared")

def optimize_startup():
    """Perform startup optimizations."""
    logger.info("Performing startup optimizations...")
    
    # Pre-warm critical caches
    try:
        # Pre-load common Pokemon
        for species_id in [1, 4, 7, 25]:  # Starter Pokemon + Pikachu
            cached_pokemon_lookup(species_id)
        
        # Pre-load common moves
        common_moves = ['Tackle', 'Thunder Shock', 'Fire Blast', 'Surf']
        for move in common_moves:
            cached_move_lookup(move)
        
        logger.info("Startup optimization completed")
        
    except Exception as e:
        logger.error(f"Startup optimization failed: {e}")
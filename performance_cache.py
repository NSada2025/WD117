#!/usr/bin/env python3
"""
Performance Cache System
Implements caching for analysis results to improve re-analysis speed
Created as part of workspace optimization (Phase 2)
"""

import os
import pickle
import hashlib
import time
from pathlib import Path
import json

class PerformanceCache:
    """Cache system for analysis results"""
    
    def __init__(self, cache_dir="/mnt/d/multiagent-system/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache configuration
        self.cache_config = {
            'max_age_hours': 24,        # Cache expires after 24 hours
            'max_cache_size_mb': 100,   # Maximum cache size
            'compression': True,        # Use compression for cache files
            'verify_checksums': True    # Verify data integrity
        }
        
        # Initialize cache index
        self.index_file = self.cache_dir / 'cache_index.json'
        self.cache_index = self.load_cache_index()
        
    def load_cache_index(self):
        """Load cache index from file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_cache_index(self):
        """Save cache index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(self.cache_index, f, indent=2)
    
    def generate_cache_key(self, analysis_type, data_file_path, parameters=None):
        """Generate unique cache key for analysis"""
        
        # Include file modification time to invalidate cache if data changes
        try:
            mtime = os.path.getmtime(data_file_path)
        except:
            mtime = time.time()
        
        # Create hash from analysis parameters
        key_data = {
            'analysis_type': analysis_type,
            'data_file': str(data_file_path),
            'mtime': mtime,
            'parameters': parameters or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def is_cache_valid(self, cache_key):
        """Check if cached result is still valid"""
        
        if cache_key not in self.cache_index:
            return False
        
        cache_info = self.cache_index[cache_key]
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Check if cache file exists
        if not cache_file.exists():
            return False
        
        # Check cache age
        cache_age_hours = (time.time() - cache_info['timestamp']) / 3600
        if cache_age_hours > self.cache_config['max_age_hours']:
            return False
        
        return True
    
    def get_cached_result(self, analysis_type, data_file_path, parameters=None):
        """Retrieve cached analysis result"""
        
        cache_key = self.generate_cache_key(analysis_type, data_file_path, parameters)
        
        if not self.is_cache_valid(cache_key):
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Verify checksum if enabled
            if self.cache_config['verify_checksums']:
                if not self.verify_cache_integrity(cached_data, cache_key):
                    return None
            
            print(f"✓ Cache hit for {analysis_type}")
            return cached_data['result']
            
        except Exception as e:
            print(f"Cache read error for {cache_key}: {e}")
            return None
    
    def cache_result(self, analysis_type, data_file_path, result, parameters=None):
        """Cache analysis result"""
        
        cache_key = self.generate_cache_key(analysis_type, data_file_path, parameters)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Prepare cache data
        cache_data = {
            'analysis_type': analysis_type,
            'data_file': str(data_file_path),
            'parameters': parameters,
            'result': result,
            'timestamp': time.time(),
            'cache_key': cache_key
        }
        
        # Add checksum for integrity verification
        if self.cache_config['verify_checksums']:
            cache_data['checksum'] = self.calculate_checksum(cache_data)
        
        try:
            # Save cache file
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Update cache index
            self.cache_index[cache_key] = {
                'analysis_type': analysis_type,
                'data_file': str(data_file_path),
                'timestamp': time.time(),
                'file_size': cache_file.stat().st_size
            }
            
            self.save_cache_index()
            print(f"✓ Cached result for {analysis_type}")
            
            # Clean up old cache if needed
            self.cleanup_cache()
            
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def calculate_checksum(self, data):
        """Calculate checksum for cache integrity"""
        # Create checksum from result data only (excluding timestamp and checksum itself)
        checksum_data = {
            'analysis_type': data['analysis_type'],
            'data_file': data['data_file'],
            'parameters': data['parameters'],
            'result': str(data['result'])  # Convert to string for consistent hashing
        }
        checksum_string = json.dumps(checksum_data, sort_keys=True)
        return hashlib.sha256(checksum_string.encode()).hexdigest()
    
    def verify_cache_integrity(self, cached_data, cache_key):
        """Verify cached data integrity"""
        if 'checksum' not in cached_data:
            return False
        
        expected_checksum = self.calculate_checksum(cached_data)
        return cached_data['checksum'] == expected_checksum
    
    def cleanup_cache(self):
        """Clean up old or oversized cache"""
        
        # Get cache size
        total_size = sum(info['file_size'] for info in self.cache_index.values())
        max_size_bytes = self.cache_config['max_cache_size_mb'] * 1024 * 1024
        
        if total_size > max_size_bytes:
            print("Cache size limit exceeded, cleaning up...")
            
            # Sort by timestamp (oldest first)
            sorted_cache = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            # Remove oldest entries until under limit
            for cache_key, info in sorted_cache:
                cache_file = self.cache_dir / f"{cache_key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                
                del self.cache_index[cache_key]
                total_size -= info['file_size']
                
                if total_size <= max_size_bytes:
                    break
            
            self.save_cache_index()
    
    def clear_cache(self, analysis_type=None):
        """Clear cache (all or specific analysis type)"""
        
        if analysis_type:
            # Clear specific analysis type
            keys_to_remove = [
                key for key, info in self.cache_index.items()
                if info['analysis_type'] == analysis_type
            ]
        else:
            # Clear all cache
            keys_to_remove = list(self.cache_index.keys())
        
        for cache_key in keys_to_remove:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                cache_file.unlink()
            
            if cache_key in self.cache_index:
                del self.cache_index[cache_key]
        
        self.save_cache_index()
        print(f"Cleared {len(keys_to_remove)} cache entries")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        
        total_entries = len(self.cache_index)
        total_size = sum(info['file_size'] for info in self.cache_index.values())
        
        # Count by analysis type
        type_counts = {}
        for info in self.cache_index.values():
            analysis_type = info['analysis_type']
            type_counts[analysis_type] = type_counts.get(analysis_type, 0) + 1
        
        stats = {
            'total_entries': total_entries,
            'total_size_mb': total_size / (1024 * 1024),
            'by_analysis_type': type_counts,
            'cache_dir': str(self.cache_dir),
            'max_age_hours': self.cache_config['max_age_hours'],
            'max_size_mb': self.cache_config['max_cache_size_mb']
        }
        
        return stats
    
    def print_cache_stats(self):
        """Print cache statistics"""
        
        stats = self.get_cache_stats()
        
        print("CACHE STATISTICS")
        print("="*20)
        print(f"Total entries: {stats['total_entries']}")
        print(f"Total size: {stats['total_size_mb']:.1f} MB")
        print(f"Cache directory: {stats['cache_dir']}")
        print(f"Max age: {stats['max_age_hours']} hours")
        print(f"Max size: {stats['max_size_mb']} MB")
        
        if stats['by_analysis_type']:
            print("\nBy analysis type:")
            for analysis_type, count in stats['by_analysis_type'].items():
                print(f"  {analysis_type}: {count} entries")

# Decorator for easy caching
def cached_analysis(analysis_type, cache=None):
    """Decorator to automatically cache analysis results"""
    
    if cache is None:
        cache = PerformanceCache()
    
    def decorator(func):
        def wrapper(data_file_path, *args, **kwargs):
            
            # Try to get cached result
            cached_result = cache.get_cached_result(
                analysis_type, data_file_path, {'args': args, 'kwargs': kwargs}
            )
            
            if cached_result is not None:
                return cached_result
            
            # Run analysis
            print(f"Running fresh analysis: {analysis_type}")
            result = func(data_file_path, *args, **kwargs)
            
            # Cache result
            cache.cache_result(
                analysis_type, data_file_path, result, {'args': args, 'kwargs': kwargs}
            )
            
            return result
        
        return wrapper
    return decorator

# Example usage functions
def example_cached_analysis():
    """Example of how to use the cache system"""
    
    cache = PerformanceCache()
    
    # Example analysis function
    @cached_analysis('med_error_analysis', cache)
    def analyze_med_errors(data_file):
        # Simulate analysis work
        time.sleep(2)
        return {'errors': 5, 'accuracy': 0.95}
    
    # This will run fresh analysis
    result1 = analyze_med_errors('/path/to/data.txt')
    print("First call result:", result1)
    
    # This will use cached result
    result2 = analyze_med_errors('/path/to/data.txt')
    print("Second call result:", result2)
    
    # Print cache stats
    cache.print_cache_stats()

if __name__ == "__main__":
    cache = PerformanceCache()
    cache.print_cache_stats()
    
    # Run example if no cached data exists
    if not cache.cache_index:
        print("\nRunning cache example...")
        example_cached_analysis()
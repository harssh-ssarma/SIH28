import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.core.cache import cache
from django_redis import get_redis_connection

print("=" * 50)
print("Clearing All Redis Cache...")
print("=" * 50)

try:
    # Get Redis connection
    redis_conn = get_redis_connection("default")
    
    # Get all keys with our prefix
    keys = redis_conn.keys('sih28:*')
    
    if keys:
        print(f"\nFound {len(keys)} keys to delete:")
        for key in keys[:10]:  # Show first 10
            print(f"  - {key.decode()}")
        if len(keys) > 10:
            print(f"  ... and {len(keys) - 10} more")
        
        # Delete all keys
        deleted = redis_conn.delete(*keys)
        print(f"\n✓ Successfully deleted {deleted} cache keys")
    else:
        print("\nNo cache keys found.")
    
    print("\n" + "=" * 50)
    print("Cache Cleared Successfully!")
    print("=" * 50)
    print("\nRestart Django server to start fresh caching.")
    
except Exception as e:
    print(f"\n✗ Error clearing cache: {e}")

"""
Management command to monitor Redis cache statistics.

Usage:
    python manage.py cache_stats
    python manage.py cache_stats --clear

Shows cache hit/miss ratios, memory usage, and key patterns.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django_redis import get_redis_connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Display Redis cache statistics and health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all cache keys',
        )

    def handle(self, *args, **options):
        """Handle the command."""
        if options.get('clear'):
            self.clear_cache()
            return

        self.show_stats()

    def show_stats(self):
        """Display comprehensive cache statistics."""
        try:
            redis_conn = get_redis_connection("default")
            
            self.stdout.write(self.style.SUCCESS('=== Redis Cache Statistics ===\n'))
            
            # Get Redis info
            info = redis_conn.info()
            
            # Memory stats
            self.stdout.write(self.style.HTTP_INFO('Memory:'))
            used_memory = info.get('used_memory_human', 'N/A')
            max_memory = info.get('maxmemory_human', 'N/A')
            self.stdout.write(f'  Used: {used_memory}')
            self.stdout.write(f'  Max: {max_memory}\n')
            
            # Key statistics
            self.stdout.write(self.style.HTTP_INFO('Keys:'))
            total_keys = redis_conn.dbsize()
            self.stdout.write(f'  Total keys: {total_keys}\n')
            
            # Key patterns
            self.stdout.write(self.style.HTTP_INFO('Key Patterns:'))
            patterns = ['list:*', 'detail:*', 'count:*', 'stats:*']
            
            for pattern in patterns:
                full_pattern = f'sih28:v1:{pattern}'
                keys = redis_conn.keys(full_pattern)
                self.stdout.write(f'  {pattern}: {len(keys)} keys')
            
            # Hit/Miss ratio (if available)
            if 'keyspace_hits' in info and 'keyspace_misses' in info:
                hits = info['keyspace_hits']
                misses = info['keyspace_misses']
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0
                
                self.stdout.write(f'\n{self.style.HTTP_INFO("Cache Performance:")}')
                self.stdout.write(f'  Hits: {hits:,}')
                self.stdout.write(f'  Misses: {misses:,}')
                self.stdout.write(f'  Hit Rate: {hit_rate:.2f}%')
            
            # Connection stats
            self.stdout.write(f'\n{self.style.HTTP_INFO("Connections:")}')
            connected_clients = info.get('connected_clients', 0)
            self.stdout.write(f'  Connected clients: {connected_clients}')
            
            self.stdout.write(self.style.SUCCESS('\n✓ Cache is healthy'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to get cache stats: {e}'))

    def clear_cache(self):
        """Clear all cache keys."""
        try:
            redis_conn = get_redis_connection("default")
            
            # Get count before clearing
            total_keys = redis_conn.dbsize()
            
            # Clear all keys in the current database
            redis_conn.flushdb()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cleared {total_keys} cache keys')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to clear cache: {e}'))

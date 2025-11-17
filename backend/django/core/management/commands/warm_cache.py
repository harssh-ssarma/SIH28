"""
Management command to warm Redis cache with frequently accessed data.

Usage:
    python manage.py warm_cache
    python manage.py warm_cache --model Faculty
    python manage.py warm_cache --org <org_id>

This is run:
- After deployments
- During off-peak hours (via cron/scheduler)
- Before expected traffic spikes
"""

from django.core.management.base import BaseCommand
from django.apps import apps
from core.cache_service import CacheService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm Redis cache with frequently accessed data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Specific model to warm cache for (e.g., Faculty, Student)',
        )
        parser.add_argument(
            '--org',
            type=str,
            help='Organization ID to warm cache for',
        )

    def handle(self, *args, **options):
        model_name = options.get('model')
        org_id = options.get('org')

        self.stdout.write(self.style.SUCCESS('Starting cache warming...'))

        if model_name:
            self.warm_model(model_name, org_id)
        else:
            # Warm all major models
            for model in ['User', 'Faculty', 'Student', 'Department', 'Program']:
                self.warm_model(model, org_id)

        self.stdout.write(self.style.SUCCESS('Cache warming completed!'))

    def warm_model(self, model_name: str, org_id: str = None):
        """Warm cache for a specific model."""
        try:
            # Get model class
            model_class = apps.get_model('academics', model_name)
            
            self.stdout.write(f'Warming cache for {model_name}...')
            
            # Fetch first page of data
            queryset = model_class.objects.select_related().all()
            
            if org_id and hasattr(model_class, 'organization_id'):
                queryset = queryset.filter(organization_id=org_id)
            
            # Limit to first 100 records for warming
            data = list(queryset[:100].values())
            
            # Cache the data
            cache_key = CacheService.generate_cache_key(
                CacheService.PREFIX_LIST,
                model_name,
                page=1,
                org=org_id if org_id else 'all'
            )
            
            CacheService.set(cache_key, data, timeout=CacheService.TTL_LONG)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Warmed cache for {model_name}: {len(data)} records')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to warm cache for {model_name}: {e}')
            )

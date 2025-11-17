import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.conf import settings

db_config = settings.DATABASES['default']
print("=== DATABASE CONFIGURATION ===")
print(f"Engine: {db_config.get('ENGINE')}")
print(f"Name: {db_config.get('NAME')}")
print(f"User: {db_config.get('USER')}")
print(f"Host: {db_config.get('HOST')}")
print(f"Port: {db_config.get('PORT', '5432')}")

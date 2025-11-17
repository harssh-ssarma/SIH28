import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.db import connection

print("=== CLEARING ALL MIGRATION HISTORY ===")

with connection.cursor() as cursor:
    try:
        cursor.execute("DELETE FROM django_migrations")
        print("✓ Cleared all migration history")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n✅ Migration history reset complete!")

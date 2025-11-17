import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = [row[0] for row in cursor.fetchall()]

print("=== EXISTING TABLES ===")
for table in tables:
    print(f"  - {table}")

print(f"\nTotal: {len(tables)} tables")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.db import connection

# List of old tables to drop
old_tables = [
    'attendance', 'attendance_alerts', 'attendance_audit_logs', 'attendance_records',
    'attendance_reports', 'attendance_sessions', 'attendance_thresholds',
    'batches', 'classrooms', 'courses', 'departments', 'faculty', 'generation_jobs',
    'labs', 'students', 'subject_enrollments', 'subjects', 'timetable_slots', 'timetables'
]

print("=== DROPPING OLD TABLES ===")

with connection.cursor() as cursor:
    for table in old_tables:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
            print(f"✓ Dropped {table}")
        except Exception as e:
            print(f"✗ Error dropping {table}: {e}")
    
    print("\n=== RESETTING MIGRATION HISTORY ===")
    try:
        cursor.execute("DELETE FROM django_migrations WHERE app = 'academics'")
        print("✓ Cleared academics migration history")
    except Exception as e:
        print(f"✗ Error clearing migrations: {e}")

print("\n✅ Database cleanup complete!")
print("Next steps:")
print("  1. Run: python manage.py migrate")
print("  2. Run: python manage.py migrate_bhu_data")

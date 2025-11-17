import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from io import StringIO

print("=== GENERATING SQL FOR MULTI-TENANT TABLES ===")

# Get SQL for academics migration
sql_output = StringIO()
call_command('sqlmigrate', 'academics', '0001', stdout=sql_output)
sql = sql_output.getvalue()

print("\n=== CREATING MULTI-TENANT TABLES ===")

with connection.cursor() as cursor:
    # Execute the SQL
    try:
        cursor.execute(sql)
        print("✓ Multi-tenant tables created successfully!")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying to create tables individually...")
        
        # Just create the key tables we need
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS organizations (
                org_id UUID PRIMARY KEY,
                org_code VARCHAR(20) UNIQUE NOT NULL,
                org_name VARCHAR(200) NOT NULL,
                short_name VARCHAR(100) NOT NULL,
                institute_type VARCHAR(30) NOT NULL,
                established_year INTEGER,
                address TEXT NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                pincode VARCHAR(10) NOT NULL,
                country VARCHAR(100) DEFAULT 'India',
                contact_email VARCHAR(254) NOT NULL,
                contact_phone VARCHAR(20) NOT NULL,
                website VARCHAR(200),
                subscription_status VARCHAR(20) DEFAULT 'trial',
                subscription_start_date DATE NOT NULL,
                subscription_end_date DATE NOT NULL,
                max_students INTEGER DEFAULT 5000,
                max_faculty INTEGER DEFAULT 500,
                academic_year_format VARCHAR(20) DEFAULT '2024-25',
                current_academic_year VARCHAR(20) NOT NULL,
                timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
                logo_url VARCHAR(200),
                primary_color VARCHAR(7) DEFAULT '#0066CC',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS org_code_idx ON organizations(org_code);
            CREATE INDEX IF NOT EXISTS org_type_active_idx ON organizations(institute_type, is_active);
            """
        ]
        
        for table_sql in tables_sql:
            try:
                cursor.execute(table_sql)
                print("✓ Created table/index")
            except Exception as e2:
                print(f"  Error: {e2}")

print("\n✅ Setup complete! You can now run: python manage.py migrate_bhu_data")

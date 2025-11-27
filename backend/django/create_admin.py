import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from academics.models import User, Organization

# Get BHU organization
org = Organization.objects.get(org_code='BHU')

# Create or update admin user
user, created = User.objects.update_or_create(
    username='harshitverma',
    defaults={
        'email': 'harshit@bhu.ac.in',
        'organization': org,
        'role': 'ADMIN',  # Using uppercase ADMIN
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

# Set password
user.set_password('m@dhubala')
user.save()

print(f"{'Created' if created else 'Updated'} admin user")
print(f"Username: harshitverma")
print(f"Password: m@dhubala")
print(f"Role: {user.role}")
print(f"Organization: {org.org_name}")

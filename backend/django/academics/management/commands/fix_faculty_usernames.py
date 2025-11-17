"""
Fix faculty usernames - remove hyphens to match student format
BHU-CSE-001 → BHUCSE001
"""

from django.core.management.base import BaseCommand
from academics.models import User


class Command(BaseCommand):
    help = 'Remove hyphens from faculty usernames to match student format'

    def handle(self, *args, **kwargs):
        faculty_users = User.objects.filter(role='faculty')
        
        self.stdout.write(f"\n🔧 Updating {faculty_users.count()} faculty usernames...\n")
        
        updated = 0
        for user in faculty_users:
            old_username = user.username
            new_username = user.username.replace('-', '')
            
            if new_username != old_username:
                user.username = new_username
                user.save()
                updated += 1
                
                if updated <= 5:  # Show first 5 examples
                    self.stdout.write(f"  ✓ {old_username} → {new_username}")
        
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {updated} faculty usernames!"))
        self.stdout.write(f"{'='*70}")
        self.stdout.write(f"Format: BHU-CSE-001 → BHUCSE001")
        
        # Show samples
        sample = User.objects.filter(role='faculty')[:5]
        self.stdout.write(f"\n📋 Sample Faculty Usernames:")
        for u in sample:
            self.stdout.write(f"  Username: {u.username} | Email: {u.email}")
        
        self.stdout.write(f"\n✨ All faculty usernames now match student format!")
        self.stdout.write(f"Password: m@dhubala (unchanged)")

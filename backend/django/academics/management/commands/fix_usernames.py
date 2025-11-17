"""
Fix all usernames - remove hyphens from faculty and student usernames
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from academics.models import User, Faculty, Student
from django.db.models.signals import post_save, post_delete
from academics import signals


class Command(BaseCommand):
    help = 'Fix all usernames - remove hyphens'

    def handle(self, *args, **kwargs):
        # CRITICAL: Disconnect all signals to prevent infinite loop
        post_save.disconnect(signals.sync_user_to_faculty_student, sender=User)
        post_save.disconnect(signals.sync_faculty_to_user, sender=Faculty)
        post_save.disconnect(signals.sync_student_to_user, sender=Student)
        
        try:
            self.stdout.write("🔧 Fixing usernames (signals disconnected)...\n")
            
            # Fix faculty usernames
            faculty_users = User.objects.filter(username__contains='-')
            faculty_count = faculty_users.count()
            
            self.stdout.write(f"Found {faculty_count} users with hyphens in username")
            
            with transaction.atomic():
                for user in faculty_users:
                    old_username = user.username
                    new_username = old_username.replace('-', '')
                    
                    # Check if new username already exists
                    if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ Skipped {old_username} - {new_username} already exists")
                        )
                        continue
                    
                    user.username = new_username
                    user.save(update_fields=['username'])
                    
                    self.stdout.write(f"  ✓ {old_username} → {new_username}")
            
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS(f"✅ Fixed {faculty_count} usernames!"))
            self.stdout.write("="*70)
            
            # Show samples
            self.stdout.write("\n📋 Sample Fixed Usernames:")
            samples = User.objects.filter(role='faculty')[:5]
            for user in samples:
                self.stdout.write(f"  {user.username} - {user.email}")
            
        finally:
            # Reconnect signals
            post_save.connect(signals.sync_user_to_faculty_student, sender=User)
            post_save.connect(signals.sync_faculty_to_user, sender=Faculty)
            post_save.connect(signals.sync_student_to_user, sender=Student)
            self.stdout.write("\n✅ Signals reconnected")

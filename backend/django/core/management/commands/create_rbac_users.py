"""
Management command to create RBAC test users
"""
from django.core.management.base import BaseCommand
from academics.models import User, Organization, Department


class Command(BaseCommand):
    help = 'Create RBAC test users (Registrar, Dept Head, Coordinator)'

    def handle(self, *args, **options):
        # Get first organization
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found. Create one first.'))
            return
        
        # Get first department
        dept = Department.objects.first()
        if not dept:
            self.stdout.write(self.style.ERROR('No department found. Create one first.'))
            return
        
        # Create Registrar
        registrar, created = User.objects.get_or_create(
            username='registrar',
            defaults={
                'email': 'registrar@university.edu',
                'role': 'registrar',
                'organization': org,
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            registrar.set_password('registrar123')
            registrar.save()
            self.stdout.write(self.style.SUCCESS(f'Created Registrar: registrar / registrar123'))
        else:
            self.stdout.write(self.style.WARNING('Registrar already exists'))
        
        # Create Department Head
        dept_head, created = User.objects.get_or_create(
            username='dept_head',
            defaults={
                'email': 'depthead@university.edu',
                'role': 'dept_head',
                'organization': org,
                'department': dept.dept_id,
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            dept_head.set_password('depthead123')
            dept_head.save()
            self.stdout.write(self.style.SUCCESS(f'Created Dept Head: dept_head / depthead123'))
        else:
            self.stdout.write(self.style.WARNING('Dept Head already exists'))
        
        # Create Coordinator
        coordinator, created = User.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@university.edu',
                'role': 'coordinator',
                'organization': org,
                'department': dept.dept_id,
                'is_staff': False,
                'is_active': True,
            }
        )
        if created:
            coordinator.set_password('coordinator123')
            coordinator.save()
            self.stdout.write(self.style.SUCCESS(f'Created Coordinator: coordinator / coordinator123'))
        else:
            self.stdout.write(self.style.WARNING('Coordinator already exists'))
        
        self.stdout.write(self.style.SUCCESS('\n=== RBAC Users Created ==='))
        self.stdout.write(f'Organization: {org.org_code}')
        self.stdout.write(f'Department: {dept.dept_code}')
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('1. Registrar: registrar / registrar123')
        self.stdout.write('2. Dept Head: dept_head / depthead123')
        self.stdout.write('3. Coordinator: coordinator / coordinator123')

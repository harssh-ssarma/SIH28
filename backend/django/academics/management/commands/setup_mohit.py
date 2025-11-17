"""Setup Mohit Keshari faculty"""
from django.core.management.base import BaseCommand
from academics.models import Faculty, Subject, Department


class Command(BaseCommand):
    help = 'Setup Mohit Keshari with Algorithms subject'

    def handle(self, *args, **options):
        # Update F101 to Mohit Keshari
        try:
            fac = Faculty.objects.get(faculty_id='F101')
            fac.faculty_name = 'Mohit Keshari'
            fac.email = 'mohit@gmail.com'
            fac.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Updated: {fac.faculty_name} - {fac.email}'))
        except Faculty.DoesNotExist:
            dept = Department.objects.filter(department_name__icontains='computer').first()
            if not dept:
                dept = Department.objects.first()
            fac = Faculty.objects.create(
                faculty_id='F101',
                faculty_name='Mohit Keshari',
                designation='Assistant Professor',
                department=dept,
                specialization='Algorithms',
                max_workload_per_week=20,
                email='mohit@gmail.com',
                phone='9999999999'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {fac.faculty_name}'))
        
        # Create or update Algorithms subject
        dept = fac.department
        subj, created = Subject.objects.get_or_create(
            subject_id='S101',
            defaults={
                'subject_name': 'Algorithms',
                'department': dept,
                'credits': 4,
                'faculty_assigned': fac.faculty_id
            }
        )
        
        if not created and subj.faculty_assigned != fac.faculty_id:
            subj.faculty_assigned = fac.faculty_id
            subj.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Reassigned {subj.subject_name} to {fac.faculty_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Subject: {subj.subject_name} -> {fac.faculty_name}'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))

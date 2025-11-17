"""Setup mohit as faculty with Algorithms subject"""
from django.core.management.base import BaseCommand
from academics.models import Faculty, Subject, Department, User


class Command(BaseCommand):
    help = 'Setup mohit faculty with Algorithms subject'

    def handle(self, *args, **options):
        # Get mohit user
        mohit_user = User.objects.filter(username='mohit').first()
        if not mohit_user:
            self.stdout.write(self.style.ERROR('Mohit user not found'))
            return
        
        # Get or create CS department
        cs_dept, _ = Department.objects.get_or_create(
            department_id='CS',
            defaults={'department_name': 'Computer Science'}
        )
        
        # Create mohit faculty record
        faculty, created = Faculty.objects.get_or_create(
            email='mohit@gmail.com',
            defaults={
                'faculty_id': 'F101',
                'faculty_name': 'Mohit Kumar',
                'department': cs_dept,
                'qualification': 'M.Tech',
                'designation': 'Assistant Professor',
                'phone': '9876543210'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created faculty: {faculty.faculty_name}'))
        else:
            self.stdout.write(f'✓ Faculty already exists: {faculty.faculty_name}')
        
        # Create or get Algorithms subject
        algo_subject, created = Subject.objects.get_or_create(
            subject_id='S101',
            defaults={
                'subject_name': 'Algorithms',
                'department': cs_dept,
                'credits': 4,
                'faculty_assigned': faculty.faculty_id
            }
        )
        
        if not created and algo_subject.faculty_assigned != faculty.faculty_id:
            algo_subject.faculty_assigned = faculty.faculty_id
            algo_subject.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Assigned {algo_subject.subject_name} to {faculty.faculty_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Subject: {algo_subject.subject_name} - Faculty: {faculty.faculty_name}'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))

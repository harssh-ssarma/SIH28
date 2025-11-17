"""Assign Algorithms to Mohit Keshari"""
from django.core.management.base import BaseCommand
from academics.models import Subject, Faculty, Department


class Command(BaseCommand):
    help = 'Assign Algorithms subject to Mohit Keshari'

    def handle(self, *args, **options):
        # Get CS department
        dept = Department.objects.filter(department_name__icontains='computer').first()
        if not dept:
            dept = Department.objects.first()
        
        # Check Mohit faculty
        mohit = Faculty.objects.filter(faculty_id='F101').first()
        if not mohit:
            self.stdout.write(self.style.ERROR('Mohit faculty (F101) not found'))
            return
        
        self.stdout.write(f'Faculty: {mohit.faculty_name} ({mohit.email})')
        
        # Get a course
        from academics.models import Course
        course = Course.objects.first()
        
        # Create or update Algorithms subject
        algo, created = Subject.objects.get_or_create(
            subject_id='S101',
            defaults={
                'subject_name': 'Algorithms',
                'department': dept,
                'course': course,
                'credits': 4,
                'faculty_assigned': 'F101'
            }
        )
        
        if not created:
            algo.faculty_assigned = 'F101'
            algo.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Updated: {algo.subject_name} -> {mohit.faculty_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {algo.subject_name} -> {mohit.faculty_name}'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))

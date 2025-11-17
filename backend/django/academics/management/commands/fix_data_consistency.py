"""Fix inconsistent data - add realistic subjects and redistribute faculty"""
from django.core.management.base import BaseCommand
from academics.models import Faculty, Subject, Department, Course
from django.db import transaction


class Command(BaseCommand):
    help = 'Fix data consistency - add subjects and redistribute faculty'

    def handle(self, *args, **options):
        # Department-wise realistic subjects
        dept_subjects = {
            'Computer Science': ['Data Structures', 'Algorithms', 'Database Management', 'Operating Systems', 
                                'Computer Networks', 'Software Engineering', 'Artificial Intelligence', 
                                'Machine Learning', 'Web Development', 'Cyber Security'],
            'Electrical': ['Circuit Theory', 'Power Systems', 'Control Systems', 'Digital Electronics', 
                          'Signals and Systems', 'Electrical Machines'],
            'Mechanical': ['Thermodynamics', 'Fluid Mechanics', 'Manufacturing Processes', 
                          'Machine Design', 'Heat Transfer', 'Strength of Materials'],
            'Civil': ['Structural Analysis', 'Concrete Technology', 'Surveying', 
                     'Environmental Engineering', 'Geotechnical Engineering', 'Transportation Engineering'],
            'Biotechnology': ['Molecular Biology', 'Genetic Engineering', 'Biochemistry', 
                            'Cell Biology', 'Bioinformatics'],
            'Management': ['Marketing Management', 'Financial Management', 'Human Resource Management', 
                          'Operations Management', 'Strategic Management'],
            'Economics': ['Microeconomics', 'Macroeconomics', 'Econometrics', 'Development Economics'],
            'Humanities': ['English Literature', 'Philosophy', 'Psychology', 'Sociology'],
            'Mathematics': ['Calculus', 'Linear Algebra', 'Differential Equations', 'Statistics'],
            'Physics': ['Classical Mechanics', 'Quantum Mechanics', 'Electromagnetism', 'Thermodynamics'],
            'Chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Analytical Chemistry']
        }
        
        with transaction.atomic():
            self.stdout.write('Step 1: Creating subjects for all departments...')
            
            # Get all departments
            depts = {d.department_name: d for d in Department.objects.all()}
            course = Course.objects.first()
            
            subject_id_counter = 200
            created_subjects = 0
            
            for dept_name, subjects_list in dept_subjects.items():
                if dept_name in depts:
                    dept = depts[dept_name]
                    for subj_name in subjects_list:
                        # Check if subject exists
                        if not Subject.objects.filter(subject_name=subj_name, department=dept).exists():
                            Subject.objects.create(
                                subject_id=f'S{subject_id_counter}',
                                subject_name=subj_name,
                                department=dept,
                                course=course,
                                credits=4,
                                faculty_assigned=''  # Will assign later
                            )
                            created_subjects += 1
                            subject_id_counter += 1
            
            self.stdout.write(f'✓ Created {created_subjects} new subjects')
            
            self.stdout.write('\nStep 2: Assigning subjects to faculty...')
            
            # Now assign subjects to faculty
            all_faculties = list(Faculty.objects.all().select_related('department'))
            updated = 0
            
            for faculty in all_faculties:
                # Get unassigned subjects from this faculty's department
                unassigned = Subject.objects.filter(
                    department=faculty.department,
                    faculty_assigned=''
                ).first()
                
                if unassigned:
                    unassigned.faculty_assigned = faculty.faculty_id
                    unassigned.save()
                    
                    # Update faculty specialization
                    faculty.specialization = unassigned.subject_name
                    faculty.save()
                    
                    updated += 1
                    if updated % 10 == 0:
                        self.stdout.write(f'  Processed {updated} faculties...')
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Updated {updated} faculties with subjects'))
            self.stdout.write(self.style.SUCCESS('✓ Data is now consistent!'))

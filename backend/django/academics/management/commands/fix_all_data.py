"""Create realistic subjects and redistribute faculty across all departments"""
from django.core.management.base import BaseCommand
from academics.models import Faculty, Subject, Department, Course
from django.db import transaction


class Command(BaseCommand):
    help = 'Create realistic subjects and fix faculty distribution'

    def handle(self, *args, **options):
        # Department-wise realistic subjects
        dept_subjects = {
            'Computer Science': [
                'Data Structures', 'Algorithms', 'Operating Systems', 'Database Management',
                'Computer Networks', 'Software Engineering', 'Web Development', 'Machine Learning',
                'Artificial Intelligence', 'Compiler Design', 'Cloud Computing', 'Cybersecurity'
            ],
            'Electrical Engineering': [
                'Circuit Theory', 'Digital Electronics', 'Power Systems', 'Control Systems',
                'Signal Processing', 'Electromagnetic Theory', 'VLSI Design', 'Power Electronics'
            ],
            'Mechanical Engineering': [
                'Thermodynamics', 'Fluid Mechanics', 'Machine Design', 'Manufacturing Processes',
                'Heat Transfer', 'Engineering Mechanics', 'CAD/CAM', 'Automobile Engineering'
            ],
            'Civil Engineering': [
                'Structural Analysis', 'Concrete Technology', 'Surveying', 'Geotechnical Engineering',
                'Transportation Engineering', 'Environmental Engineering', 'Hydraulics', 'Building Design'
            ],
            'Biotechnology': [
                'Molecular Biology', 'Genetic Engineering', 'Bioprocess Engineering', 'Microbiology',
                'Cell Biology', 'Biochemistry', 'Immunology', 'Bioinformatics'
            ],
            'Management': [
                'Marketing Management', 'Financial Management', 'Human Resource Management', 'Operations Management',
                'Strategic Management', 'Business Analytics', 'Entrepreneurship', 'Organizational Behavior'
            ],
            'Economics': [
                'Microeconomics', 'Macroeconomics', 'Econometrics', 'International Economics',
                'Development Economics', 'Public Economics', 'Financial Economics', 'Game Theory'
            ],
            'Humanities': [
                'English Communication', 'Technical Writing', 'Ethics', 'Psychology',
                'Sociology', 'Philosophy', 'Indian Culture', 'Professional Communication'
            ],
            'Mathematics': [
                'Calculus', 'Linear Algebra', 'Differential Equations', 'Probability & Statistics',
                'Discrete Mathematics', 'Numerical Methods', 'Real Analysis', 'Complex Analysis'
            ],
            'Physics': [
                'Classical Mechanics', 'Quantum Mechanics', 'Electromagnetism', 'Thermodynamics',
                'Optics', 'Modern Physics', 'Solid State Physics', 'Nuclear Physics'
            ],
            'Chemistry': [
                'Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Analytical Chemistry',
                'Environmental Chemistry', 'Industrial Chemistry', 'Polymer Chemistry', 'Biochemistry'
            ]
        }
        
        # Realistic faculty distribution (total ~100)
        dept_faculty_count = {
            'Computer Science': 18,
            'Electrical Engineering': 12,
            'Mechanical Engineering': 12,
            'Civil Engineering': 10,
            'Biotechnology': 8,
            'Management': 10,
            'Economics': 8,
            'Humanities': 8,
            'Mathematics': 8,
            'Physics': 6,
            'Chemistry': 6
        }
        
        with transaction.atomic():
            course = Course.objects.first()
            
            # Step 1: Create/update subjects for each department
            self.stdout.write('\n=== Creating Subjects ===')
            subject_counter = 1
            created_subjects = {}
            
            for dept_name, subjects in dept_subjects.items():
                dept = Department.objects.filter(department_name__icontains=dept_name.split()[0]).first()
                if not dept:
                    self.stdout.write(f'⚠ Department not found: {dept_name}')
                    continue
                
                created_subjects[dept.department_id] = []
                for subj_name in subjects:
                    subj_id = f'S{subject_counter:03d}'
                    subject, created = Subject.objects.get_or_create(
                        subject_id=subj_id,
                        defaults={
                            'subject_name': subj_name,
                            'department': dept,
                            'course': course,
                            'credits': 4,
                            'faculty_assigned': ''
                        }
                    )
                    if not created:
                        subject.subject_name = subj_name
                        subject.department = dept
                        subject.save()
                    
                    created_subjects[dept.department_id].append(subject)
                    subject_counter += 1
                
                self.stdout.write(f'✓ {dept_name}: {len(subjects)} subjects')
            
            # Step 2: Redistribute faculties across departments
            self.stdout.write('\n=== Redistributing Faculty ===')
            all_faculties = list(Faculty.objects.all())
            faculty_idx = 0
            
            for dept_name, target_count in dept_faculty_count.items():
                dept = Department.objects.filter(department_name__icontains=dept_name.split()[0]).first()
                if not dept or dept.department_id not in created_subjects:
                    continue
                
                # Assign faculties to this department
                dept_faculties = all_faculties[faculty_idx:faculty_idx + target_count]
                dept_subjects = created_subjects[dept.department_id]
                
                for i, faculty in enumerate(dept_faculties):
                    # Update faculty department
                    faculty.department = dept
                    
                    # Assign 1-2 subjects per faculty
                    assigned_subjects = dept_subjects[i % len(dept_subjects):i % len(dept_subjects) + 2]
                    if not assigned_subjects:
                        assigned_subjects = [dept_subjects[0]]
                    
                    for subj in assigned_subjects:
                        if not subj.faculty_assigned:
                            subj.faculty_assigned = faculty.faculty_id
                            subj.save()
                    
                    # Update specialization
                    faculty.specialization = ', '.join([s.subject_name for s in assigned_subjects])
                    faculty.save()
                
                self.stdout.write(f'✓ {dept_name}: {len(dept_faculties)} faculties assigned')
                faculty_idx += target_count
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Created {subject_counter-1} subjects'))
            self.stdout.write(self.style.SUCCESS(f'✓ Redistributed {faculty_idx} faculties'))
            self.stdout.write(self.style.SUCCESS('✓ All data is now consistent!'))

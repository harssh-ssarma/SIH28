"""
SEED DATA GENERATOR FOR DEMO COLLEGES
======================================

Generates realistic demo data for multiple colleges to showcase the platform.
Can create 10-100 demo colleges with varying sizes and structures.

Usage:
    python manage.py generate_demo_colleges --count 10 --type all
    python manage.py generate_demo_colleges --count 5 --type iit
    python manage.py generate_demo_colleges --count 20 --type private
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
import random
from academics.models import *


class Command(BaseCommand):
    help = 'Generate demo college data for testing multi-tenant system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of colleges to generate'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['all', 'iit', 'nit', 'state', 'private'],
            help='Type of colleges to generate'
        )
        parser.add_argument(
            '--size',
            type=str,
            default='mixed',
            choices=['small', 'medium', 'large', 'mixed'],
            help='Size of colleges (small: 500-2000, medium: 2000-8000, large: 8000-25000)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        college_type = options['type']
        size = options['size']
        
        self.stdout.write(self.style.SUCCESS(f'\n🏫 Generating {count} demo colleges ({college_type} type, {size} size)...\n'))
        
        with transaction.atomic():
            for i in range(count):
                org = self.generate_college(i+1, college_type, size)
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {org.org_code} - {org.short_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Successfully generated {count} demo colleges!'))
        self.print_statistics()
    
    def generate_college(self, index, college_type, size):
        """Generate a single college with all data"""
        
        # Determine institute type
        if college_type == 'all':
            inst_type = random.choice(['iit', 'nit', 'state_university', 'private_university', 'autonomous_college'])
        else:
            inst_type = college_type if college_type != 'state' else 'state_university'
            inst_type = inst_type if inst_type != 'private' else 'private_university'
        
        # Determine size
        if size == 'mixed':
            college_size = random.choice(['small', 'medium', 'large'])
        else:
            college_size = size
        
        # Generate organization
        org = self.create_organization(index, inst_type, college_size)
        
        # Create infrastructure
        campus = self.create_campus(org)
        schools = self.create_schools_for_type(org, campus, inst_type, college_size)
        departments = self.create_departments_for_schools(org, schools, college_size)
        programs = self.create_programs_for_departments(org, schools, departments, college_size)
        
        # Create academic content
        subjects = self.create_subjects_for_programs(org, departments, programs, college_size)
        faculty = self.create_faculty_for_departments(org, departments, college_size)
        
        # Map faculty to subjects
        self.create_faculty_subject_mappings_bulk(org, faculty, subjects)
        
        # Create student infrastructure
        batches = self.create_batches_for_programs(org, programs, departments, college_size)
        classrooms = self.create_classrooms_for_campus(org, campus, departments, college_size)
        timeslots = self.create_standard_timeslots(org)
        
        # Create enrollments
        self.create_batch_enrollments_bulk(org, batches, subjects)
        
        # Create preferences
        self.create_timetable_preferences(org)
        
        return org
    
    def create_organization(self, index, inst_type, size):
        """Create organization"""
        
        # College name templates
        iit_names = ['Delhi', 'Bombay', 'Madras', 'Kanpur', 'Kharagpur', 'Roorkee', 'Guwahati', 'Hyderabad']
        nit_names = ['Trichy', 'Warangal', 'Surathkal', 'Calicut', 'Rourkela', 'Jaipur', 'Kurukshetra', 'Silchar']
        state_names = ['State University', 'Deemed University', 'Central University', 'Technical University']
        private_names = ['Institute of Technology', 'University', 'Institute of Engineering', 'College of Engineering']
        
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']
        states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Telangana', 'West Bengal', 'Rajasthan', 'Gujarat', 'Uttar Pradesh']
        
        if inst_type == 'iit':
            name_part = random.choice(iit_names)
            org_name = f'Indian Institute of Technology {name_part}'
            short_name = f'IIT {name_part}'
            org_code = f'IIT{name_part[:3].upper()}'
        elif inst_type == 'nit':
            name_part = random.choice(nit_names)
            org_name = f'National Institute of Technology {name_part}'
            short_name = f'NIT {name_part}'
            org_code = f'NIT{name_part[:3].upper()}'
        elif inst_type == 'state_university':
            city = random.choice(cities)
            suffix = random.choice(state_names)
            org_name = f'{city} {suffix}'
            short_name = f'{city} {suffix.split()[0]} Univ'
            org_code = f'{city[:3].upper()}U{index:02d}'
        else:  # private_university
            city = random.choice(cities)
            suffix = random.choice(private_names)
            org_name = f'{city} {suffix}'
            short_name = org_name
            org_code = f'PVT{index:03d}'
        
        # Size-based limits
        if size == 'small':
            max_students = random.randint(500, 2000)
            max_faculty = random.randint(50, 200)
        elif size == 'medium':
            max_students = random.randint(2000, 8000)
            max_faculty = random.randint(200, 800)
        else:  # large
            max_students = random.randint(8000, 25000)
            max_faculty = random.randint(800, 3000)
        
        city = random.choice(cities)
        state = random.choice(states)
        
        org = Organization.objects.create(
            org_code=org_code,
            org_name=org_name,
            short_name=short_name,
            institute_type=inst_type,
            established_year=random.randint(1950, 2020),
            address=f'{org_code} Campus, {city}',
            city=city,
            state=state,
            pincode=f'{random.randint(100000, 999999)}',
            country='India',
            contact_email=f'info@{org_code.lower()}.ac.in',
            contact_phone=f'+91-{random.randint(1000000000, 9999999999)}',
            website=f'https://www.{org_code.lower()}.ac.in',
            subscription_status='active',
            subscription_start_date=date(2024, 1, 1),
            subscription_end_date=date(2025, 12, 31),
            max_students=max_students,
            max_faculty=max_faculty,
            current_academic_year='2024-25',
            is_active=True
        )
        
        return org
    
    def create_campus(self, org):
        """Create main campus"""
        campus = Campus.objects.create(
            organization=org,
            campus_code='MAIN',
            campus_name=f'{org.short_name} Main Campus',
            address=org.address,
            city=org.city,
            area_in_acres=random.randint(50, 500),
            is_main_campus=True,
            is_active=True
        )
        return campus
    
    def create_schools_for_type(self, org, campus, inst_type, size):
        """Create schools based on institute type"""
        schools = []
        
        if inst_type in ['iit', 'nit']:
            # Engineering-focused institute
            school_names = ['School of Engineering', 'School of Science', 'School of Management']
            if size == 'large':
                school_names.extend(['School of Humanities', 'School of Design'])
        elif inst_type == 'state_university':
            # Multi-disciplinary university
            school_names = ['Faculty of Science', 'Faculty of Arts', 'Faculty of Commerce', 'Faculty of Law', 'Faculty of Education']
            if size == 'large':
                school_names.extend(['Faculty of Engineering', 'Faculty of Medicine', 'Faculty of Management'])
        else:  # private
            school_names = ['School of Engineering', 'School of Business', 'School of Computer Applications']
            if size != 'small':
                school_names.extend(['School of Design', 'School of Law'])
        
        for i, name in enumerate(school_names):
            school = School.objects.create(
                organization=org,
                campus=campus,
                school_code=f'SCH{i+1:02d}',
                school_name=name,
                dean_name=f'Prof. {self.generate_name()}',
                dean_email=f'dean.sch{i+1}@{org.org_code.lower()}.ac.in',
                is_active=True
            )
            schools.append(school)
        
        return schools
    
    def create_departments_for_schools(self, org, schools, size):
        """Create departments for each school"""
        departments = []
        
        # Department templates by school type
        engg_depts = [
            ('CSE', 'Computer Science and Engineering'),
            ('ECE', 'Electronics and Communication Engineering'),
            ('EE', 'Electrical Engineering'),
            ('ME', 'Mechanical Engineering'),
            ('CE', 'Civil Engineering'),
            ('CHE', 'Chemical Engineering'),
            ('IT', 'Information Technology'),
        ]
        
        science_depts = [
            ('PHYS', 'Physics'),
            ('CHEM', 'Chemistry'),
            ('MATH', 'Mathematics'),
            ('BIO', 'Biology'),
            ('STAT', 'Statistics'),
        ]
        
        mgmt_depts = [
            ('MBA', 'Business Administration'),
            ('FIN', 'Finance'),
            ('MKT', 'Marketing'),
        ]
        
        arts_depts = [
            ('ENG', 'English'),
            ('HIST', 'History'),
            ('ECON', 'Economics'),
            ('PSYCH', 'Psychology'),
        ]
        
        # Assign departments based on school name
        for school in schools:
            if 'Engineering' in school.school_name:
                dept_list = engg_depts if size != 'small' else engg_depts[:4]
            elif 'Science' in school.school_name:
                dept_list = science_depts
            elif 'Management' in school.school_name or 'Business' in school.school_name:
                dept_list = mgmt_depts
            elif 'Arts' in school.school_name or 'Humanities' in school.school_name:
                dept_list = arts_depts
            else:
                dept_list = [('DEPT1', 'General Department')]
            
            for code, name in dept_list:
                dept = Department.objects.create(
                    organization=org,
                    school=school,
                    dept_code=code,
                    dept_name=name,
                    hod_name=f'Dr. {self.generate_name()}',
                    hod_email=f'hod.{code.lower()}@{org.org_code.lower()}.ac.in',
                    building_name=f'{code} Block',
                    is_active=True
                )
                departments.append(dept)
        
        return departments
    
    def create_programs_for_departments(self, org, schools, departments, size):
        """Create programs"""
        programs = []
        
        for dept in departments:
            # Determine program types based on department
            if dept.dept_code in ['CSE', 'ECE', 'EE', 'ME', 'CE', 'CHE', 'IT']:
                # Engineering programs
                prog = Program.objects.create(
                    organization=org,
                    school=dept.school,
                    department=dept,
                    program_code=f'BTECH-{dept.dept_code}',
                    program_name=f'Bachelor of Technology in {dept.dept_name}',
                    program_type='ug',
                    duration_years=4.0,
                    total_semesters=8,
                    total_credits=160,
                    intake_capacity=random.randint(60, 120),
                    min_eligibility='JEE Mains Qualified',
                    is_active=True
                )
                programs.append(prog)
                
                if size != 'small':
                    # Add MTech
                    prog = Program.objects.create(
                        organization=org,
                        school=dept.school,
                        department=dept,
                        program_code=f'MTECH-{dept.dept_code}',
                        program_name=f'Master of Technology in {dept.dept_name}',
                        program_type='pg',
                        duration_years=2.0,
                        total_semesters=4,
                        total_credits=80,
                        intake_capacity=random.randint(20, 40),
                        min_eligibility='GATE Qualified',
                        is_active=True
                    )
                    programs.append(prog)
            
            elif dept.dept_code in ['PHYS', 'CHEM', 'MATH', 'BIO', 'STAT']:
                # Science programs
                prog = Program.objects.create(
                    organization=org,
                    school=dept.school,
                    department=dept,
                    program_code=f'BSC-{dept.dept_code}',
                    program_name=f'Bachelor of Science in {dept.dept_name}',
                    program_type='ug',
                    duration_years=3.0,
                    total_semesters=6,
                    total_credits=120,
                    intake_capacity=random.randint(40, 80),
                    min_eligibility='12th Science with 50%',
                    is_active=True
                )
                programs.append(prog)
            
            elif dept.dept_code in ['MBA', 'FIN', 'MKT']:
                # Management programs - make program code unique per department
                prog = Program.objects.create(
                    organization=org,
                    school=dept.school,
                    department=dept,
                    program_code=f'MBA-{dept.dept_code}',
                    program_name=f'Master of Business Administration ({dept.dept_name})',
                    program_type='pg',
                    duration_years=2.0,
                    total_semesters=4,
                    total_credits=90,
                    intake_capacity=random.randint(60, 120),
                    min_eligibility='Graduation + CAT/MAT',
                    is_active=True
                )
                programs.append(prog)
        
        return programs
    
    def create_subjects_for_programs(self, org, departments, programs, size):
        """Create subjects for programs"""
        subjects = []
        
        # Subject count based on size
        subjects_per_semester = 6 if size != 'small' else 5
        
        for program in programs:
            for sem in range(1, program.total_semesters + 1):
                for i in range(subjects_per_semester):
                    # Core subjects for first 4 semesters, electives later
                    subject_type = 'core' if sem <= 4 else ('elective' if i >= 2 else 'core')
                    
                    # Make subject code unique per program
                    subj = Subject.objects.create(
                        organization=org,
                        department=program.department,
                        program=program,
                        subject_code=f'{program.program_code}-S{sem:02d}{i+1}',
                        subject_name=f'{program.program_name} - Sem {sem} Subject {i+1}',
                        subject_type=subject_type,
                        credits=random.choice([3, 4]),
                        lecture_hours_per_week=3,
                        practical_hours_per_week=random.choice([0, 2]),
                        semester=sem,
                        requires_lab=(random.random() < 0.4),
                        max_students_per_class=60,
                        min_classroom_capacity=60,
                        is_active=True
                    )
                    subjects.append(subj)
        
        return subjects
    
    def create_faculty_for_departments(self, org, departments, size):
        """Create faculty"""
        faculty_list = []
        
        # Faculty count based on size
        if size == 'small':
            faculty_per_dept = random.randint(5, 10)
        elif size == 'medium':
            faculty_per_dept = random.randint(10, 20)
        else:
            faculty_per_dept = random.randint(20, 40)
        
        designations = [
            ('professor', 16, 1.0),
            ('associate_professor', 20, 1.5),
            ('assistant_professor', 22, 2.0),
            ('lecturer', 24, 2.5),
        ]
        
        for dept in departments:
            for i in range(faculty_per_dept):
                desig, max_hrs, leaves = random.choice(designations)
                
                name = self.generate_name()
                fac = Faculty.objects.create(
                    organization=org,
                    department=dept,
                    employee_id=f'{org.org_code}-{dept.dept_code}-{i+1:03d}',
                    faculty_name=f'Dr. {name}',
                    designation=desig,
                    email=f'{name.lower().replace(" ", ".")}@{org.org_code.lower()}.ac.in',
                    phone=f'+91-{random.randint(7000000000, 9999999999)}',
                    specialization=f'{dept.dept_name} Specialist',
                    max_teaching_hours_per_week=max_hrs,
                    avg_leaves_per_month=leaves,
                    is_available=True,
                    date_of_joining=date(2020, 1, 1) + timedelta(days=random.randint(0, 1460))
                )
                faculty_list.append(fac)
        
        return faculty_list
    
    def create_faculty_subject_mappings_bulk(self, org, faculty, subjects):
        """Map faculty to subjects"""
        mappings = []
        
        # Each faculty can teach 2-4 subjects
        for fac in faculty:
            dept_subjects = [s for s in subjects if s.department == fac.department]
            if dept_subjects:
                num_subjects = min(random.randint(2, 4), len(dept_subjects))
                assigned_subjects = random.sample(dept_subjects, num_subjects)
                
                for i, subj in enumerate(assigned_subjects):
                    mapping = FacultySubject.objects.create(
                        organization=org,
                        faculty=fac,
                        subject=subj,
                        preference_level=i+1,
                        can_handle_lab=subj.requires_lab,
                        years_of_experience_teaching=random.randint(1, 15)
                    )
                    mappings.append(mapping)
        
        return mappings
    
    def create_batches_for_programs(self, org, programs, departments, size):
        """Create batches"""
        batches = []
        
        # Number of sections based on size
        sections_per_year = 1 if size == 'small' else 2
        
        for program in programs:
            years = int(program.duration_years)
            
            for year in range(years):
                admission_year = 2024 - year
                current_sem = (year * 2) + 1
                
                for section in ['A', 'B'][:sections_per_year]:
                    students_per_section = program.intake_capacity // sections_per_year
                    
                    batch = Batch.objects.create(
                        organization=org,
                        program=program,
                        department=program.department,
                        batch_name=f'{program.program_code} {admission_year} Batch',
                        batch_code=f'{admission_year % 100}{program.program_code}-{section}',
                        year_of_admission=admission_year,
                        current_semester=current_sem,
                        section=section,
                        total_students=students_per_section,
                        is_active=True
                    )
                    batches.append(batch)
        
        return batches
    
    def create_classrooms_for_campus(self, org, campus, departments, size):
        """Create classrooms"""
        classrooms = []
        
        # Classroom count based on size
        if size == 'small':
            num_lh, num_labs, num_tr = 10, 5, 5
        elif size == 'medium':
            num_lh, num_labs, num_tr = 20, 10, 10
        else:
            num_lh, num_labs, num_tr = 30, 15, 15
        
        # Lecture Halls
        for i in range(num_lh):
            room = Classroom.objects.create(
                organization=org,
                campus=campus,
                classroom_code=f'LH-{i+1:03d}',
                building_name='Main Academic Block',
                floor_number=(i // 10) + 1,
                room_type='lecture_hall',
                seating_capacity=random.choice([60, 80, 100, 120]),
                has_projector=True,
                has_ac=(random.random() < 0.7),
                has_smart_board=(random.random() < 0.5),
                is_available=True
            )
            classrooms.append(room)
        
        # Labs
        for i in range(num_labs):
            dept = random.choice(departments)
            room = Classroom.objects.create(
                organization=org,
                campus=campus,
                department=dept,
                classroom_code=f'LAB-{i+1:03d}',
                building_name=f'{dept.dept_code} Block',
                floor_number=random.randint(1, 3),
                room_type='laboratory',
                seating_capacity=random.choice([40, 50, 60]),
                has_projector=True,
                has_ac=True,
                has_lab_equipment=True,
                has_computers=(random.random() < 0.7),
                is_available=True
            )
            classrooms.append(room)
        
        # Tutorial Rooms
        for i in range(num_tr):
            room = Classroom.objects.create(
                organization=org,
                campus=campus,
                classroom_code=f'TR-{i+1:03d}',
                building_name='Tutorial Block',
                floor_number=random.randint(1, 3),
                room_type='tutorial_room',
                seating_capacity=random.choice([30, 40, 50]),
                has_projector=True,
                has_ac=(random.random() < 0.5),
                is_available=True
            )
            classrooms.append(room)
        
        return classrooms
    
    def create_standard_timeslots(self, org):
        """Create standard 36 time slots"""
        timeslots = []
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        periods = [
            ('09:00:00', '10:00:00', 'Period 1'),
            ('10:00:00', '11:00:00', 'Period 2'),
            ('11:15:00', '12:15:00', 'Period 3'),
            ('12:15:00', '13:15:00', 'Period 4'),
            ('14:15:00', '15:15:00', 'Period 5'),
            ('15:15:00', '16:15:00', 'Period 6'),
        ]
        
        slot_order = 1
        for day in days:
            day_periods = periods if day != 'saturday' else periods[:3]
            
            for start, end, name in day_periods:
                slot = TimeSlot.objects.create(
                    organization=org,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    slot_name=name,
                    slot_order=slot_order,
                    is_available=True
                )
                timeslots.append(slot)
                slot_order += 1
        
        return timeslots
    
    def create_batch_enrollments_bulk(self, org, batches, subjects):
        """Create batch enrollments"""
        enrollments = []
        
        for batch in batches:
            # Get subjects for this batch's program and semester
            batch_subjects = [
                s for s in subjects 
                if s.program == batch.program and s.semester == batch.current_semester
            ]
            
            for subject in batch_subjects:
                if subject.subject_type == 'core':
                    enrolled = batch.total_students
                else:
                    enrolled = batch.total_students // 2
                
                enroll = BatchSubjectEnrollment.objects.create(
                    organization=org,
                    batch=batch,
                    subject=subject,
                    is_mandatory=(subject.subject_type == 'core'),
                    enrolled_students=enrolled,
                    academic_year='2024-25',
                    semester=batch.current_semester
                )
                enrollments.append(enroll)
        
        return enrollments
    
    def create_timetable_preferences(self, org):
        """Create timetable preferences"""
        from datetime import time
        
        TimetablePreferences.objects.create(
            organization=org,
            max_classes_per_day=6,
            max_consecutive_classes=3,
            min_break_duration_minutes=15,
            lunch_break_start=time(13, 15),
            lunch_break_end=time(14, 15),
            working_days_per_week=6,
            class_duration_minutes=60,
            allow_saturday_classes=True,
            allow_back_to_back_labs=False
        )
    
    def generate_name(self):
        """Generate random Indian name"""
        first_names = ['Rajesh', 'Priya', 'Amit', 'Neha', 'Suresh', 'Kavita', 'Vijay', 'Anita', 
                      'Manoj', 'Sunita', 'Anil', 'Meera', 'Ramesh', 'Pooja', 'Sanjay']
        last_names = ['Kumar', 'Sharma', 'Singh', 'Verma', 'Gupta', 'Mishra', 'Yadav', 'Tiwari',
                     'Pandey', 'Chandra', 'Devi', 'Prasad', 'Nath', 'Tripathi', 'Agarwal']
        
        return f'{random.choice(first_names)} {random.choice(last_names)}'
    
    def print_statistics(self):
        """Print generation statistics"""
        total_orgs = Organization.objects.count()
        total_schools = School.objects.count()
        total_depts = Department.objects.count()
        total_programs = Program.objects.count()
        total_subjects = Subject.objects.count()
        total_faculty = Faculty.objects.count()
        total_batches = Batch.objects.count()
        total_classrooms = Classroom.objects.count()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('OVERALL STATISTICS'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total Organizations: {total_orgs}')
        self.stdout.write(f'Total Schools: {total_schools}')
        self.stdout.write(f'Total Departments: {total_depts}')
        self.stdout.write(f'Total Programs: {total_programs}')
        self.stdout.write(f'Total Subjects: {total_subjects}')
        self.stdout.write(f'Total Faculty: {total_faculty}')
        self.stdout.write(f'Total Batches: {total_batches}')
        self.stdout.write(f'Total Classrooms: {total_classrooms}')
        self.stdout.write('='*60)
        
        # Average per organization
        self.stdout.write(f'\nAverage per Organization:')
        self.stdout.write(f'  Schools: {total_schools/total_orgs:.1f}')
        self.stdout.write(f'  Departments: {total_depts/total_orgs:.1f}')
        self.stdout.write(f'  Programs: {total_programs/total_orgs:.1f}')
        self.stdout.write(f'  Subjects: {total_subjects/total_orgs:.1f}')
        self.stdout.write(f'  Faculty: {total_faculty/total_orgs:.1f}')
        self.stdout.write(f'  Batches: {total_batches/total_orgs:.1f}')
        self.stdout.write('='*60)

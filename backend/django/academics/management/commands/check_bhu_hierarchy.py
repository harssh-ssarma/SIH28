"""
Check BHU Complete Hierarchical Structure
School -> Programs -> Departments -> Subjects/Faculty/Batches
"""

from django.core.management.base import BaseCommand
from academics.models import *


class Command(BaseCommand):
    help = 'Display complete BHU hierarchical structure'

    def handle(self, *args, **kwargs):
        org = Organization.objects.get(org_code='BHU')
        schools = School.objects.filter(organization=org).order_by('school_name')

        print('\n' + '='*90)
        print('BHU COMPLETE HIERARCHICAL STRUCTURE')
        print('='*90)

        for school in schools:
            print(f'\n📚 {school.school_name} ({school.school_code})')
            print('─'*90)
            
            # Get all programs in this school
            programs = Program.objects.filter(organization=org, school=school)
            print(f'   📊 Total Programs/Courses: {programs.count()}\n')
            
            if programs.count() > 0:
                for idx, program in enumerate(programs, 1):
                    print(f'   {idx}. 🎓 {program.program_code} - {program.program_name}')
                    print(f'      Duration: {program.duration_years} years, Total Credits: {program.total_credits}')
                    
                    # Get departments linked to this program
                    program_dept = program.department
                    
                    if program_dept:
                        subj_count = Subject.objects.filter(
                            organization=org, 
                            department=program_dept
                        ).count()
                        
                        fac_count = Faculty.objects.filter(
                            organization=org, 
                            department=program_dept
                        ).count()
                        
                        batch_count = Batch.objects.filter(
                            organization=org, 
                            program=program
                        ).count()
                        
                        print(f'      Department: {program_dept.dept_code} - {program_dept.dept_name}')
                        print(f'         └─ Subjects: {subj_count}')
                        print(f'         └─ Faculty: {fac_count}')
                        print(f'         └─ Batches: {batch_count}')
                    else:
                        print(f'      ⚠ No department assigned')
                    print()
            
            else:
                # No programs, show departments directly
                depts = Department.objects.filter(organization=org, school=school)
                print(f'   📊 No Programs (Showing {depts.count()} Departments directly)\n')
                
                for dept in depts:
                    subj_count = Subject.objects.filter(organization=org, department=dept).count()
                    fac_count = Faculty.objects.filter(organization=org, department=dept).count()
                    batch_count = Batch.objects.filter(organization=org, department=dept).count()
                    
                    if subj_count > 0 or fac_count > 0 or batch_count > 0:
                        print(f'   🏢 {dept.dept_code} - {dept.dept_name}')
                        print(f'      └─ Subjects: {subj_count}')
                        print(f'      └─ Faculty: {fac_count}')
                        print(f'      └─ Batches: {batch_count}')
                        print()

        # Summary
        print('\n' + '='*90)
        print('📈 OVERALL BHU SUMMARY')
        print('='*90)
        
        total_schools = schools.count()
        total_programs = Program.objects.filter(organization=org).count()
        total_depts = Department.objects.filter(organization=org).count()
        total_subjects = Subject.objects.filter(organization=org).count()
        total_faculty = Faculty.objects.filter(organization=org).count()
        total_batches = Batch.objects.filter(organization=org).count()
        
        print(f'Total Schools/Institutes: {total_schools}')
        print(f'Total Programs/Courses: {total_programs}')
        print(f'Total Departments: {total_depts}')
        print(f'Total Subjects: {total_subjects}')
        print(f'Total Faculty: {total_faculty}')
        print(f'Total Batches: {total_batches}')
        
        # Breakdown by school
        print(f'\n{"School":<50} {"Programs":<10} {"Depts":<10} {"Subjects":<10} {"Faculty":<10}')
        print('─'*90)
        
        for school in schools:
            prog_count = Program.objects.filter(organization=org, school=school).count()
            dept_count = Department.objects.filter(organization=org, school=school).count()
            
            # Count subjects and faculty for departments in this school
            depts = Department.objects.filter(organization=org, school=school)
            subj_count = sum(Subject.objects.filter(organization=org, department=d).count() for d in depts)
            fac_count = sum(Faculty.objects.filter(organization=org, department=d).count() for d in depts)
            
            print(f'{school.school_code:<50} {prog_count:<10} {dept_count:<10} {subj_count:<10} {fac_count:<10}')
        
        print('='*90 + '\n')

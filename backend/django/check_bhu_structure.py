from academics.models import *

schools = School.objects.filter(organization__org_code='BHU')
print('=== DEPARTMENTS BY SCHOOL ===\n')

for school in schools:
    depts = Department.objects.filter(school=school)
    print(f'{school.school_code} - {school.school_name}:')
    print(f'  Total Departments: {depts.count()}')
    if depts.count() > 0:
        for d in depts[:8]:
            print(f'    - {d.dept_code}: {d.dept_name}')
        if depts.count() > 8:
            print(f'    ... and {depts.count() - 8} more')
    print()

print('\n=== OVERALL SUMMARY ===')
print(f'Total Schools: {schools.count()}')
print(f'Total Departments: {Department.objects.filter(organization__org_code="BHU").count()}')
print(f'Total Faculty: {Faculty.objects.filter(organization__org_code="BHU").count()}')
print(f'Total Programs: {Program.objects.filter(organization__org_code="BHU").count()}')
print(f'Total Subjects: {Subject.objects.filter(organization__org_code="BHU").count()}')

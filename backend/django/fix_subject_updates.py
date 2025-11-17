import re

# Read the file
with open('academics/management/commands/complete_bhu_hierarchy.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Subject.objects.update_or_create with department in lookup
pattern1 = r'Subject\.objects\.update_or_create\(\s*organization=org,\s*department=dept,\s*subject_code=subj_code,\s*defaults=\{'
replacement1 = '''Subject.objects.update_or_create(
                organization=org,
                subject_code=subj_code,
                defaults={
                    'department': dept,'''

content = re.sub(pattern1, replacement1, content)

# Pattern 2: For loops creating subjects
pattern2 = r'for subj_code, subj_name, subj_type, credits, lec_hrs, prac_hrs, sem, max_stu in subjects:\s*Subject\.objects\.update_or_create\(\s*organization=org,\s*subject_code=subj_code,\s*defaults=\{\s*\'department\': dept,\s*\'department\': dept,'
replacement2 = '''for subj_code, subj_name, subj_type, credits, lec_hrs, prac_hrs, sem, max_stu in subjects:
                Subject.objects.update_or_create(
                organization=org,
                subject_code=subj_code,
                defaults={
                    'department': dept,'''

content = re.sub(pattern2, replacement2, content)

# Write back
with open('academics/management/commands/complete_bhu_hierarchy.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed Subject.update_or_create patterns")

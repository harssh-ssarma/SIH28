"""
Migration to add RBAC roles to User model
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0007_timetableconfiguration'),
    ]

    operations = [
        # Add department field to User if not exists
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.UUIDField(null=True, blank=True, db_column='dept_id'),
        ),
        
        # Update role choices to include new RBAC roles
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('super_admin', 'Super Admin (Platform)'),
                    ('org_admin', 'Organization Admin'),
                    ('registrar', 'Registrar'),
                    ('dept_head', 'Department Head'),
                    ('coordinator', 'Coordinator'),
                    ('dean', 'Dean'),
                    ('hod', 'Head of Department'),
                    ('faculty', 'Faculty'),
                    ('student', 'Student'),
                    ('staff', 'Administrative Staff'),
                ],
                default='student'
            ),
        ),
    ]

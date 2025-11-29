from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0008_add_rbac_roles'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='generationjob',
            index=models.Index(fields=['-created_at'], name='gen_job_created_idx'),
        ),
        migrations.AddIndex(
            model_name='generationjob',
            index=models.Index(fields=['status', '-created_at'], name='gen_job_status_idx'),
        ),
    ]

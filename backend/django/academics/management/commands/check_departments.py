from academics.models import Department, Organization
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check available departments"

    def handle(self, *args, **options):
        try:
            org = Organization.objects.first()
            if not org:
                self.stdout.write(self.style.ERROR("No organization found"))
                return

            departments = Department.objects.filter(organization=org, is_active=True)

            self.stdout.write(f"Found {departments.count()} departments:")
            for dept in departments:
                self.stdout.write(f"  - {dept.dept_code}: {dept.dept_name}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

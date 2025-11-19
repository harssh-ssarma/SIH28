from academics.models import Organization, Student
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check current student count by semester"

    def handle(self, *args, **kwargs):
        try:
            org = Organization.objects.first()
            if not org:
                self.stdout.write(self.style.ERROR("No organization found"))
                return

            self.stdout.write("Current Student Count by Semester:")

            for sem in range(1, 9):
                count = Student.objects.filter(
                    organization=org, current_semester=sem, is_active=True
                ).count()
                self.stdout.write(f"  Semester {sem}: {count} students")

            total = Student.objects.filter(organization=org, is_active=True).count()
            self.stdout.write(f"Total Active Students: {total}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

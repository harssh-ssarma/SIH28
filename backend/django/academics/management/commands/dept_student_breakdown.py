from academics.models import Department, Organization, Student
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Show department-wise student breakdown by semester"

    def handle(self, *args, **kwargs):
        try:
            org = Organization.objects.first()
            if not org:
                self.stdout.write(self.style.ERROR("No organization found"))
                return

            self.stdout.write("Department-wise Student Breakdown by Semester:")
            self.stdout.write("=" * 80)

            departments = Department.objects.filter(organization=org, is_active=True)

            for dept in departments:
                dept_total = 0
                sem_data = []

                for sem in range(1, 9):
                    count = Student.objects.filter(
                        organization=org,
                        department=dept,
                        current_semester=sem,
                        is_active=True,
                    ).count()
                    if count > 0:
                        sem_data.append(f"Sem{sem}: {count}")
                        dept_total += count

                if dept_total > 0:
                    self.stdout.write(
                        f'{dept.dept_code:10} | {dept.dept_name:40} | Total: {dept_total:4} | {" | ".join(sem_data)}'
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

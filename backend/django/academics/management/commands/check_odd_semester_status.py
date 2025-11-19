from academics.models import Department, Organization, Student
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check status of odd semester filling"

    def handle(self, *args, **kwargs):
        try:
            org = Organization.objects.first()
            if not org:
                self.stdout.write(self.style.ERROR("No organization found"))
                return

            self.stdout.write("Odd Semester Status Check:")
            self.stdout.write("=" * 80)

            odd_semesters = [1, 3, 5, 7]
            departments = Department.objects.filter(organization=org, is_active=True)

            # Overall summary
            self.stdout.write("Overall Summary:")
            for sem in odd_semesters:
                count = Student.objects.filter(
                    organization=org, current_semester=sem, is_active=True
                ).count()
                self.stdout.write(f"  Semester {sem}: {count:4} students")

            total = Student.objects.filter(organization=org, is_active=True).count()
            self.stdout.write(f"  Total:      {total:4} students")

            # Department status
            self.stdout.write(
                "\nDepartment Status (showing departments with <50 in any odd semester):"
            )
            self.stdout.write("-" * 80)

            incomplete_depts = 0
            complete_depts = 0

            for dept in departments:
                issues = []
                for sem in odd_semesters:
                    count = Student.objects.filter(
                        organization=org,
                        department=dept,
                        current_semester=sem,
                        is_active=True,
                    ).count()
                    if count < 50:
                        issues.append(f"S{sem}:{count}")

                if issues:
                    incomplete_depts += 1
                    self.stdout.write(
                        f'{dept.dept_code:10}: NEEDS FILLING - {", ".join(issues)}'
                    )
                else:
                    complete_depts += 1

            self.stdout.write(
                f"\nSummary: {complete_depts} departments complete, {incomplete_depts} need filling"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

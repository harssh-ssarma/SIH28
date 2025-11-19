from academics.models import Student, StudentElectiveChoice, Subject
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check if students are enrolled in subjects"

    def handle(self, *args, **options):
        # Count totals
        total_students = Student.objects.count()
        total_subjects = Subject.objects.count()
        total_enrollments = StudentElectiveChoice.objects.count()

        self.stdout.write(f"Total students: {total_students}")
        self.stdout.write(f"Total subjects: {total_subjects}")
        self.stdout.write(f"Total enrollments: {total_enrollments}")

        # Check students with enrollments
        students_with_enrollments = (
            Student.objects.filter(elective_choices__isnull=False).distinct().count()
        )

        students_without_enrollments = total_students - students_with_enrollments

        self.stdout.write(f"Students with enrollments: {students_with_enrollments}")
        self.stdout.write(
            f"Students without enrollments: {students_without_enrollments}"
        )

        # Check subjects with enrollments
        subjects_with_enrollments = (
            Subject.objects.filter(student_choices__isnull=False).distinct().count()
        )

        subjects_without_enrollments = total_subjects - subjects_with_enrollments

        self.stdout.write(f"Subjects with enrollments: {subjects_with_enrollments}")
        self.stdout.write(
            f"Subjects without enrollments: {subjects_without_enrollments}"
        )

        if total_enrollments == 0:
            self.stdout.write(self.style.WARNING("❌ NO STUDENT ENROLLMENTS FOUND"))
            self.stdout.write(
                "Use the Bulk Enrollment Tool in admin panel to create enrollments"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ {total_enrollments} student enrollments exist")
            )

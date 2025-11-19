from academics.models import Classroom, Subject
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check subjects with lab requirements and available lab classrooms"

    def handle(self, *args, **options):
        # Check subjects with lab requirements
        lab_subjects = Subject.objects.filter(requires_lab=True)
        total_subjects = Subject.objects.count()

        self.stdout.write(f"Total subjects: {total_subjects}")
        self.stdout.write(f"Subjects requiring labs: {lab_subjects.count()}")

        # Show some lab subjects
        self.stdout.write("\nSample lab subjects:")
        for subject in lab_subjects[:10]:
            self.stdout.write(f"  - {subject.subject_code}: {subject.subject_name}")
            self.stdout.write(f"    Lab batch size: {subject.lab_batch_size}")
            self.stdout.write(
                f"    Practical hours/week: {subject.practical_hours_per_week}"
            )

        # Check lab classrooms
        lab_classrooms = Classroom.objects.filter(room_type="laboratory")
        total_classrooms = Classroom.objects.count()

        self.stdout.write(f"\nTotal classrooms: {total_classrooms}")
        self.stdout.write(f"Laboratory classrooms: {lab_classrooms.count()}")

        # Show some lab classrooms
        self.stdout.write("\nSample lab classrooms:")
        for classroom in lab_classrooms[:10]:
            self.stdout.write(
                f"  - {classroom.classroom_code}: {classroom.building_name}"
            )
            self.stdout.write(f"    Capacity: {classroom.seating_capacity}")
            self.stdout.write(
                f"    Has computers: {classroom.has_computers} ({classroom.computer_count})"
            )

        # Summary
        if lab_subjects.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ {lab_subjects.count()} subjects have lab requirements"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("\n❌ No subjects have lab requirements set")
            )

        if lab_classrooms.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {lab_classrooms.count()} lab classrooms available"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("❌ No lab classrooms found"))

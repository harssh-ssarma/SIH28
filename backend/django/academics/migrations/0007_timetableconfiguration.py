# Generated manually
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0006_building_course_room_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimetableConfiguration",
            fields=[
                (
                    "config_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "config_name",
                    models.CharField(default="Default Configuration", max_length=200),
                ),
                ("academic_year", models.CharField(max_length=20)),
                ("semester", models.IntegerField()),
                ("working_days", models.IntegerField(default=6)),
                ("slots_per_day", models.IntegerField(default=8)),
                ("start_time", models.TimeField(default="08:00")),
                ("end_time", models.TimeField(default="17:00")),
                ("slot_duration_minutes", models.IntegerField(default=60)),
                ("lunch_break_enabled", models.BooleanField(default=True)),
                ("lunch_break_start", models.TimeField(default="13:00")),
                ("lunch_break_end", models.TimeField(default="14:00")),
                ("selected_departments", models.JSONField(blank=True, default=list)),
                ("include_open_electives", models.BooleanField(default=True)),
                ("max_classes_per_day", models.IntegerField(default=6)),
                ("min_gap_between_classes", models.IntegerField(default=0)),
                ("avoid_first_last_slot", models.BooleanField(default=False)),
                ("faculty_max_continuous", models.IntegerField(default=3)),
                (
                    "optimization_priority",
                    models.CharField(
                        choices=[
                            ("balanced", "Balanced"),
                            ("compact", "Compact"),
                            ("spread", "Spread Out"),
                        ],
                        default="balanced",
                        max_length=20,
                    ),
                ),
                ("minimize_faculty_travel", models.BooleanField(default=True)),
                ("prefer_morning_slots", models.BooleanField(default=False)),
                ("group_same_subject", models.BooleanField(default=True)),
                ("number_of_variants", models.IntegerField(default=5)),
                ("timeout_minutes", models.IntegerField(default=10)),
                ("allow_conflicts", models.BooleanField(default=False)),
                ("use_ai_optimization", models.BooleanField(default=True)),
                ("is_default", models.BooleanField(default=False)),
                ("last_used_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_timetable_configs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        db_column="org_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="timetable_configs",
                        to="academics.organization",
                    ),
                ),
            ],
            options={
                "db_table": "timetable_configurations",
                "ordering": ["-last_used_at"],
            },
        ),
        migrations.AddIndex(
            model_name="timetableconfiguration",
            index=models.Index(
                fields=["organization", "is_default"], name="idx_config_org_default"
            ),
        ),
        migrations.AddIndex(
            model_name="timetableconfiguration",
            index=models.Index(
                fields=["organization", "last_used_at"], name="idx_config_org_used"
            ),
        ),
    ]

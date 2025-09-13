from django.db import models

class Classroom(models.Model):
    CLASSROOM_TYPES = [
        ('lecture', 'Lecture Hall'),
        ('lab', 'Laboratory'),
        ('seminar', 'Seminar Room'),
        ('auditorium', 'Auditorium'),
    ]

    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    type = models.CharField(max_length=20, choices=CLASSROOM_TYPES)
    equipment = models.JSONField(default=list, blank=True)
    building = models.CharField(max_length=100)
    floor = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.building})"

    class Meta:
        ordering = ['building', 'floor', 'name']
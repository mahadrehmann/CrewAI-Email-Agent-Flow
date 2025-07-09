from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Schedule(models.Model):
    DAYS = [
        ('monday',    'Monday'),
        ('tuesday',   'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday',  'Thursday'),
        ('friday',    'Friday'),
        ('saturday',  'Saturday'),
        ('sunday',    'Sunday'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    receiver   = models.EmailField()
    filepath   = models.URLField()
    day        = models.CharField(max_length=9, choices=DAYS)
    time       = models.TimeField()
    active     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.day.capitalize()} @ {self.time}"

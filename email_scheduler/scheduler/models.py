from django.db import models

class Schedule(models.Model):
    receiver = models.EmailField()
    filepath = models.CharField(max_length=255)
    day = models.CharField(max_length=10)
    time = models.TimeField()

    def __str__(self):
        return f"{self.receiver} on {self.day} at {self.time}"

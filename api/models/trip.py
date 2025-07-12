
from django.db import models
from .user import User
import uuid

class Trip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name='created_trips', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='joined_trips', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} to {self.destination} by {self.creator.username}"

    class Meta:
        indexes = [
            models.Index(fields=['destination', 'start_date']),
        ]
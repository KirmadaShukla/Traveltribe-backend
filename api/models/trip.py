
from django.db import models
from .user import User
import uuid

class TripParticipant(models.Model):
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE)
    participant = models.ForeignKey('User', on_delete=models.CASCADE, db_column='participant_id')
    ROLE_CHOICES = [
        ("participant", "Participant"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="participant")

    class Meta:
        unique_together = ('trip', 'participant')
        db_table = 'api_trip_participant'

class Trip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name='created_trips', on_delete=models.CASCADE)
    participants = models.ManyToManyField(
        User,
        through='TripParticipant',
        related_name='joined_trips',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Estimated total budget for the trip")
    group_size = models.PositiveIntegerField(null=True, blank=True, help_text="Expected number of participants")
    currency = models.CharField(max_length=10, null=True, blank=True, help_text="Currency for the budget, e.g., USD")
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned", help_text="Current status of the trip")
    cover_image_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL of the cover image stored in Cloudinary")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated timestamp")
    is_public = models.BooleanField(default=True, help_text="Whether the trip is public or private")
    interests = models.CharField(max_length=255, blank=True, help_text="Comma-separated interests or tags")

    def __str__(self):
        return f"{self.title} to {self.destination} by {self.creator.username}"

    class Meta:
        indexes = [
            models.Index(fields=['destination', 'start_date']),
        ]
from django.db import models
from .trip import Trip
from .user import User

class TripLike(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'user')
        db_table = 'api_trip_like'

class TripComment(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_trip_comment' 
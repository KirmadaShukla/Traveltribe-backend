from django.db import models
from .trip import Trip
from .user import User

class Review(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'reviewer', 'reviewee')
        db_table = 'api_review'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.reviewee} on {self.trip}" 
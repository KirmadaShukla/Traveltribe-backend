from rest_framework import viewsets, permissions
from ..models.review import Review
from ..serializers.review import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        reviewee = serializer.validated_data.get('reviewee')
        trip = serializer.validated_data.get('trip')
        if reviewee == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'reviewee': 'You cannot review yourself.'})
        # Check if both reviewer and reviewee are participants of the trip
        participants = trip.participants.all()
        if self.request.user not in participants or reviewee not in participants:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Both reviewer and reviewee must be participants of the trip.'})
        review = serializer.save(reviewer=self.request.user)
        # Update dashboard fields
        reviewer = self.request.user
        reviewer.total_reviews_given = reviewer.given_reviews.count()
        reviewer.save(update_fields=['total_reviews_given'])
        reviewee.total_reviews_received = reviewee.received_reviews.count()
        # Recalculate average rating received
        from django.db.models import Avg
        avg_rating = reviewee.received_reviews.aggregate(avg=Avg('rating'))['avg']
        reviewee.average_rating_received = round(avg_rating, 2) if avg_rating is not None else None
        reviewee.save(update_fields=['total_reviews_received', 'average_rating_received']) 
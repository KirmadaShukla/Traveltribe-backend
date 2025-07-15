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
        serializer.save(reviewer=self.request.user) 
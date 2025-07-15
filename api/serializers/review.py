from rest_framework import serializers
from ..models.review import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'trip', 'reviewer', 'reviewee', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'reviewer'] 
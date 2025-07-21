
from rest_framework import serializers
from ..models import Trip, User
from .user import UserSerializer

class TripSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    cover_image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    cover_image_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'creator', 'participants', 'created_at', 'budget', 'group_size', 'currency', 'status', 'cover_image', 'cover_image_url', 'updated_at', 'is_public', 'interests']

    def create(self, validated_data):
        validated_data.pop('cover_image', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('cover_image', None)
        return super().update(instance, validated_data)

class FeaturedTripSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    cover_image_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'start_date', 'end_date', 'description',
            'created_at', 'budget', 'group_size', 'currency', 'cover_image', 'cover_image_url', 'updated_at', 'is_public', 'interests'
        ]
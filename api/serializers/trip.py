
from rest_framework import serializers
from ..models import Trip, User, TripLike
from .user import UserSerializer

class TripSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    cover_image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'creator', 'participants', 'created_at', 'budget', 'group_size', 'currency', 'status', 'cover_image', 'cover_image_url', 'updated_at', 'is_public', 'interests']

    def get_cover_image_url(self, obj):
        return obj.cover_image_url

    def create(self, validated_data):
        validated_data.pop('cover_image', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('cover_image', None)
        return super().update(instance, validated_data)

class FeaturedTripSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'start_date', 'end_date', 'description',
            'created_at', 'budget', 'group_size', 'currency', 'cover_image_url', 'updated_at', 'is_public', 'interests'
        ]
    
    def get_cover_image_url(self, obj):
        return obj.cover_image_url

class UpcomingTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'created_at', 'budget', 'group_size', 'currency', 'cover_image_url', 'updated_at', 'is_public', 'interests']

class RecommendedTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'created_at', 'budget', 'group_size', 'currency', 'cover_image_url', 'updated_at', 'interests']

class TrendingDestinationSerializer(serializers.Serializer):
    destination = serializers.CharField()
    trip_count = serializers.IntegerField()
    cover_image_url = serializers.URLField()

class ExploreTripSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'created_at', 'budget', 'cover_image_url', 'updated_at', 'is_public', 'interests', 'likes_count', 'creator', 'is_liked']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return TripLike.objects.filter(trip=obj, user=user).exists()
        return False

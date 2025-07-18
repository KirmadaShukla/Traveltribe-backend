
from rest_framework import serializers
from api.models.user import User
from api.models.trip import Trip
from api.models.review import Review
from django.db import models

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, error_messages={
        'required': 'Password is required.'
    })
    email = serializers.EmailField(required=True, error_messages={
        'required': 'Email is required.'
    })
    name = serializers.CharField(required=True, error_messages={
        'required': 'Name is required.'
    })

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'bio', 'date_joined', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class UserDashboardSerializer(serializers.ModelSerializer):
    trips_completed = serializers.SerializerMethodField()
    trips_cancelled = serializers.SerializerMethodField()
    trips_planned = serializers.SerializerMethodField()
    trips_ongoing = serializers.SerializerMethodField()
    total_trips_created = serializers.SerializerMethodField()
    total_trips_joined = serializers.SerializerMethodField()
    total_reviews_received = serializers.SerializerMethodField()
    total_reviews_given = serializers.SerializerMethodField()
    average_rating_received = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'phone', 'bio', 'date_joined',
            'trips_completed', 'trips_cancelled',
            'trips_planned', 'trips_ongoing',
            'total_trips_created', 'total_trips_joined',
            'total_reviews_received', 'total_reviews_given',
            'average_rating_received',
        ]

    def get_trips_completed(self, obj):
        return Trip.objects.filter(creator=obj, status='completed').count()

    def get_trips_cancelled(self, obj):
        return Trip.objects.filter(creator=obj, status='cancelled').count()

    def get_trips_planned(self, obj):
        return Trip.objects.filter(creator=obj, status='planned').count()

    def get_trips_ongoing(self, obj):
        return Trip.objects.filter(creator=obj, status='ongoing').count()

    def get_total_trips_created(self, obj):
        return Trip.objects.filter(creator=obj).count()

    def get_total_trips_joined(self, obj):
        return obj.joined_trips.count()

    def get_total_reviews_received(self, obj):
        return Review.objects.filter(reviewee=obj).count()

    def get_total_reviews_given(self, obj):
        return Review.objects.filter(reviewer=obj).count()

    def get_average_rating_received(self, obj):
        reviews = Review.objects.filter(reviewee=obj)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return None

from rest_framework import serializers
from ..models import Trip, User
from .user import UserSerializer

class TripSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'creator', 'participants', 'created_at']
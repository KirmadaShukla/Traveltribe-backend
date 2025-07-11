
from rest_framework import serializers
from ..models import Trip, User
from .user import UserSerializer

class TripSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    creator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='creator', write_only=True
    )

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'start_date', 'end_date', 'description', 
                  'creator', 'creator_id', 'participants', 'created_at']
from rest_framework import serializers
from api.models.trip_interaction import TripLike, TripComment
from api.models.trip import Trip

class TripLikeSerializer(serializers.ModelSerializer):
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())

    class Meta:
        model = TripLike
        fields = '__all__'
        read_only_fields = ['user']

class TripCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripComment
        fields = '__all__'
        read_only_fields = ['user'] 
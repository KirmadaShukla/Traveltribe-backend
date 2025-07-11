
from rest_framework import serializers
from ..models import User

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
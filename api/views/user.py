
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from ..models import User
from ..serializers import UserSerializer
from api.serializers.user import UserDashboardSerializer
from api.models.user import Address
import requests
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
   
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':  # Allow anyone to register
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        address_data = validated_data.pop('address', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        if address_data:
            Address.objects.create(user=user, **address_data)
        headers = self.get_success_headers(serializer.data)
        # Re-serialize to return the created user (without password)
        response_serializer = self.get_serializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDashboardSerializer(request.user)
        return Response(serializer.data)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'error': 'No id_token provided'}, status=status.HTTP_400_BAD_REQUEST)
        # Verify the token with Google
        google_response = requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': id_token}
        )
        if google_response.status_code != 200:
            return Response({'error': 'Invalid id_token'}, status=status.HTTP_400_BAD_REQUEST)
        user_info = google_response.json()
        print("user_onfo",user_info)
        email = user_info.get('email')
        name = user_info.get('name', email)
        if not email:
            return Response({'error': 'No email in Google token'}, status=status.HTTP_400_BAD_REQUEST)
        # Find or create user
        user, created = User.objects.update_or_create(
            email=email,
            defaults={'name': name}
        )
        
        # Log the user in
        # Manually set the backend attribute to prevent a 500 error
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'email': email,
            'name': name
        })

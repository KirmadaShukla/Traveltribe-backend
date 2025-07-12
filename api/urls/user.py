
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from ..views import UserViewSet, user_profile, LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),  # <-- Add this line to include the router URLs
    path('profile/', user_profile, name='user_profile'),
    path('login/', LoginView.as_view(), name='user_login'),  # legacy token login
    path('jwt/login/', TokenObtainPairView.as_view(), name='jwt_login'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
]
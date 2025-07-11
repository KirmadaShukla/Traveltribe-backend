
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import UserViewSet, user_profile, LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', user_profile, name='user_profile'),
    path('login/', LoginView.as_view(), name='user_login'),  # legacy token login
    path('jwt/login/', TokenObtainPairView.as_view(), name='jwt_login'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
]
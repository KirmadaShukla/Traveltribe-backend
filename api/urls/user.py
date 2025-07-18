
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from ..views import UserViewSet, user_profile, LoginView, UserDashboardView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = SimpleRouter()
router.register(r'', UserViewSet, basename='user')  # No 'users' prefix here

urlpatterns = [
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('profile/', user_profile, name='user_profile'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('jwt/login/', TokenObtainPairView.as_view(), name='jwt_login'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import TripViewSet
from api.views.trip_interaction import TripLikeViewSet, TripCommentViewSet

router = DefaultRouter()
router.register(r'comments', TripCommentViewSet)
router.register(r'likes', TripLikeViewSet)
router.register(r'', TripViewSet, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
]
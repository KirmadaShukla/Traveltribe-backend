from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from api.models.trip import Trip
from api.models.trip_interaction import TripLike, TripComment
from api.serializers.trip_interaction import TripLikeSerializer, TripCommentSerializer
import logging

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        # Write/delete permissions are only allowed to the owner of the like.
        return obj.user == request.user

class TripLikeViewSet(viewsets.ModelViewSet):
    queryset = TripLike.objects.all()
    serializer_class = TripLikeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        trip_like = serializer.save(user=self.request.user)
        trip = trip_like.trip
        trip.likes_count = (trip.likes_count or 0) + 1
        trip.save(update_fields=["likes_count"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        trip = instance.trip
        self.perform_destroy(instance)
        if trip.likes_count and trip.likes_count > 0:
            trip.likes_count -= 1
            trip.save(update_fields=["likes_count"])
        return Response(
            {
                "detail": "Like deleted successfully.",
                "likes_count": trip.likes_count
            },
            status=status.HTTP_200_OK
        )

class TripCommentViewSet(viewsets.ModelViewSet):
    queryset = TripComment.objects.all()
    serializer_class = TripCommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 
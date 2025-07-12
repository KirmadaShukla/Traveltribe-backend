
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from ..models import Trip
from ..serializers import TripSerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('creator').prefetch_related('participants')
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        print(request.data)
        return Response({'message': 'Trip created successfully'}, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({'message': 'Trip updated successfully'}, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'message': 'Trip deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        try:
            trip = self.get_object()
            if request.user == trip.creator:
                return Response({
                    'error': 'Creator cannot join their own trip'
                }, status=status.HTTP_400_BAD_REQUEST)
            if request.user in trip.participants.all():
                return Response({
                    'error': 'User already joined this trip'
                }, status=status.HTTP_400_BAD_REQUEST)
            trip.participants.add(request.user)
            return Response({
                'message': 'Successfully joined the trip'
            }, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({
                'error': 'Trip not found'
            }, status=status.HTTP_404_NOT_FOUND)
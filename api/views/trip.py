
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
        # Prevent user from creating a new trip if they have an ongoing one
        ongoing_trip_exists = Trip.objects.filter(creator=request.user, is_completed=False).exists()
        if ongoing_trip_exists:
            return Response({'error': 'You already have an ongoing trip. Complete it before creating a new one.'}, status=status.HTTP_400_BAD_REQUEST)
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

    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, pk=None):
        try:
            # Check if user is already a participant in any ongoing trip
            ongoing_participation = Trip.objects.filter(participants=request.user, is_completed=False).exists()
            if ongoing_participation:
                return Response({'error': 'You are already a participant in an ongoing trip. Leave it before joining another.'}, status=status.HTTP_400_BAD_REQUEST)
            trip = Trip.objects.get(id=pk)
            if request.user == trip.creator:
                return Response({'error': 'Creator cannot join their own trip'}, status=status.HTTP_400_BAD_REQUEST)
            if request.user in trip.participants.all():
                return Response({'error': 'User already joined this trip'}, status=status.HTTP_400_BAD_REQUEST)
            trip.participants.add(request.user)
            return Response({'message': 'Successfully joined the trip'}, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='leave')
    def leave(self, request, pk=None):
        try:
            trip = Trip.objects.get(id=pk)
            if request.user == trip.creator:
                return Response({'error': 'Creator cannot leave their own trip'}, status=status.HTTP_400_BAD_REQUEST)
            if request.user not in trip.participants.all():
                return Response({'error': 'User is not a participant of this trip'}, status=status.HTTP_400_BAD_REQUEST)
            trip.participants.remove(request.user)
            return Response({'message': 'Successfully left the trip'}, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
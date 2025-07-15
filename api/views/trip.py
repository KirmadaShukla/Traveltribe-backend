
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from ..models import Trip
from ..serializers import TripSerializer
from ..serializers import UserSerializer
from ..utils.cloudinary_utils import upload_image_to_cloudinary
from rest_framework.pagination import PageNumberPagination

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('creator').prefetch_related('participants')
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        # Block creation if user has any trip not completed or cancelled
        ongoing_trip_exists = Trip.objects.filter(creator=request.user).exclude(status__in=["completed", "cancelled"]).exists()
        if ongoing_trip_exists:
            return Response({'error': 'You already have an ongoing trip. You can only create a new trip when your existing trip is completed or cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        cover_image = request.FILES.get('cover_image')
        if cover_image:
            image_url = upload_image_to_cloudinary(cover_image)
            print("image_url",image_url)
            data['cover_image_url'] = image_url
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Trip created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        cover_image = request.FILES.get('cover_image')
        if cover_image:
            image_url = upload_image_to_cloudinary(cover_image)
            data['cover_image_url'] = image_url
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'message': 'Trip deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, pk=None):
        try:
            # Check if user is already a participant in any ongoing trip
            ongoing_participation = Trip.objects.filter(
                participants=request.user
            ).exclude(status__in=["completed", "cancelled"]).exists()
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

    @action(detail=True, methods=['get'], url_path='participant-contact/(?P<user_id>[0-9a-f-]+)', permission_classes=[IsAuthenticated])
    def participant_contact(self, request, pk=None, user_id=None):
        try:
            trip = Trip.objects.get(id=pk)
            if request.user != trip.creator:
                return Response({'error': 'Only the creator can view participant contact details.'}, status=status.HTTP_403_FORBIDDEN)
            participant = trip.participants.filter(id=user_id).first()
            if not participant:
                return Response({'error': 'User is not a participant of this trip.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(participant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='participants-list', permission_classes=[IsAuthenticated])
    def participants_list(self, request, pk=None):
        try:
            trip = Trip.objects.get(id=pk)
            if request.user != trip.creator:
                return Response({'error': 'Only the creator can view the participants list.'}, status=status.HTTP_403_FORBIDDEN)
            participants = trip.participants.all()
            data = [{'id': str(p.id), 'name': p.name, 'email': p.email, 'phone': p.phone} for p in participants]
            return Response(data, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

    def _filter_trips(self, queryset, params):
        filter_map = {
            'destination': 'destination__icontains',
            'start_date': 'start_date__gte',
            'end_date': 'end_date__lte',
            'min_budget': 'budget__gte',
            'max_budget': 'budget__lte',
        }
        filters = {v: params[k] for k, v in filter_map.items() if params.get(k)}
        queryset = queryset.filter(**filters)
        interests = params.get('interests')
        if interests:
            for interest in interests.split(','):
                queryset = queryset.filter(interests__icontains=interest.strip())
        return queryset

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        params = request.query_params
        queryset = self._filter_trips(Trip.objects.all(), params)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
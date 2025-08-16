
from datetime import date
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from ..models import Trip
from ..serializers import TripSerializer, UpcomingTripSerializer, RecommendedTripSerializer
from ..serializers import UserSerializer, FeaturedTripSerializer
from ..utils.cloudinary_utils import upload_image_to_cloudinary
from ..utils.gemini_utils import get_recommendations
from ..pagination import StandardResultsSetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from api.models.trip import Trip
from api.models.trip_interaction import TripLike, TripComment

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('creator').prefetch_related('participants')
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        # Debug logging for incoming data
        print('FILES:', request.FILES)
        print('DATA:', request.data)
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
        old_status = instance.status
        data = request.data.copy()
        cover_image = request.FILES.get('cover_image')
        if cover_image:
            image_url = upload_image_to_cloudinary(cover_image)
            data['cover_image_url'] = image_url
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Update creator's dashboard fields if status changed
        new_status = serializer.instance.status
        creator = instance.creator
        if old_status != new_status:
            if old_status == 'completed':
                creator.trips_completed = max(0, creator.trips_completed - 1)
            if old_status == 'cancelled':
                creator.trips_cancelled = max(0, creator.trips_cancelled - 1)
            if new_status == 'completed':
                creator.trips_completed += 1
                # Award points to all participants and the host
                trip = serializer.instance
                participants = list(trip.participants.all())
                if creator not in participants:
                    participants.append(creator)
                for user in participants:
                    user.points += 100  # Award 10 points
                    user.save(update_fields=['points'])
            if new_status == 'cancelled':
                creator.trips_cancelled += 1
            creator.save(update_fields=['trips_completed', 'trips_cancelled'])
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
            # Enforce group_size limit
            if trip.group_size is not None and trip.participants.count() >= trip.group_size:
                return Response({'error': 'This trip has reached its participant limit.'}, status=status.HTTP_400_BAD_REQUEST)
            trip.participants.add(request.user)
            # Update user's total_trips_joined
            user = request.user
            user.total_trips_joined = user.joined_trips.count()
            user.save(update_fields=['total_trips_joined'])
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
            # Update user's total_trips_joined
            user = request.user
            user.total_trips_joined = user.joined_trips.count()
            user.save(update_fields=['total_trips_joined'])
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

    def is_admin_or_creator(self, user, trip):
        if user == trip.creator:
            return True
        from ..models.trip import TripParticipant
        return TripParticipant.objects.filter(trip=trip, participant=user, role='admin').exists()

    @action(detail=True, methods=['post'], url_path='kickout', permission_classes=[IsAuthenticated])
    def kickout_participant(self, request, pk=None):
        trip = self.get_object()
        if not self.is_admin_or_creator(request.user, trip):
            return Response({'error': 'Only the host or an admin can remove participants.'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if str(trip.creator.id) == str(user_id):
            return Response({'error': 'Host cannot be removed from the trip.'}, status=status.HTTP_400_BAD_REQUEST)
        participant = trip.participants.filter(id=user_id).first()
        if not participant:
            return Response({'error': 'User is not a participant of this trip.'}, status=status.HTTP_404_NOT_FOUND)
        trip.participants.remove(participant)
        return Response({'message': 'Participant removed from the trip.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='make-admin', permission_classes=[IsAuthenticated])
    def make_admin(self, request, pk=None):
        trip = self.get_object()
        if not self.is_admin_or_creator(request.user, trip):
            return Response({'error': 'Only the host or an admin can promote participants to admin.'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if str(trip.creator.id) == str(user_id):
            return Response({'error': 'Host is already the admin of the trip.'}, status=status.HTTP_400_BAD_REQUEST)
        from ..models.trip import TripParticipant
        trip_participant = TripParticipant.objects.filter(trip=trip, participant_id=user_id).first()
        if not trip_participant:
            return Response({'error': 'User is not a participant of this trip.'}, status=status.HTTP_404_NOT_FOUND)
        trip_participant.role = 'admin'
        trip_participant.save(update_fields=['role'])
        return Response({'message': 'Participant promoted to admin.'}, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        # Return top 10 public trips ordered by likes_count and start_date
        trips = Trip.objects.filter(is_public=True).order_by('-likes_count', 'start_date')[:10]
        serializer = FeaturedTripSerializer(trips, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        today = date.today()
        upcoming_trips = Trip.objects.filter(start_date__gte=today, cover_image_url__isnull=False).exclude(cover_image_url__exact='')
        
        if upcoming_trips.count() > 5:
            random_trips = random.sample(list(upcoming_trips), 5)
        else:
            random_trips = upcoming_trips
            
        serializer = UpcomingTripSerializer(random_trips, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='explore')
    def explore(self, request):
        today = date.today()
        queryset = Trip.objects.filter(start_date__gte=today, is_public=True).order_by('start_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='recommend', permission_classes=[IsAuthenticated])
    def recommend(self, request):
        user = request.user
        user_interest = user.interest
        if not user_interest:
            return Response({'error': 'User has no interests set.'}, status=status.HTTP_400_BAD_REQUEST)

        all_trips = Trip.objects.exclude(creator=user).filter(status__in=['planned', 'upcoming'])
        trip_interests = [trip.interests for trip in all_trips if trip.interests]
        
        recommended_trip_interests = get_recommendations(user_interest, trip_interests)

        if not recommended_trip_interests:
            return Response([], status=status.HTTP_200_OK)

        # Build a query to find trips that contain any of the recommended interests
        query = Q()
        for interest in recommended_trip_interests:
            query |= Q(interests__icontains=interest)
            
        # Filter the trips using the constructed query and remove duplicates
        recommended_trips = all_trips.filter(query).distinct()
        
        serializer = RecommendedTripSerializer(recommended_trips, many=True)
        return Response(serializer.data)


class PopularCitiesView(APIView):
    def get(self, request):
        popular_cities = Trip.objects.values('destination').annotate(trip_count=Count('id')).order_by('-trip_count')[:10]
        return Response(popular_cities)

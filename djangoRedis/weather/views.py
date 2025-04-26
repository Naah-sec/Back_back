from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from .models import Location, WeatherQuery, UserSearchHistory
from .serializers import LocationSerializer, WeatherQuerySerializer, UserSearchHistorySerializer
from .services import VisualCrossingAPIClient
from .tasks import fetch_weather_async
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class WeatherViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        # Get user's recent weather queries
        queryset = WeatherQuery.objects.filter(user=request.user).order_by('-query_date')[:10]
        serializer = WeatherQuerySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        location_id = request.query_params.get('location_id')
        address = request.query_params.get('address')
        
        if not location_id and not address:
            return Response(
                {'error': 'Either location_id or address must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if location_id:
                location = Location.objects.get(id=location_id)
                address = f"{location.latitude},{location.longitude}"
            else:
                location = None
            
            client = VisualCrossingAPIClient()
            weather_data = client.get_current_weather(address)
            
            # Save query to history
            if location:
                UserSearchHistory.objects.create(user=request.user, location=location)
                WeatherQuery.objects.create(
                    user=request.user,
                    location=location,
                    forecast_date=timezone.now().date(),
                    raw_data=weather_data
                )
            
            return Response(weather_data)
        except Exception as e:
            logger.error(f"Error fetching current weather: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        location_id = request.query_params.get('location_id')
        address = request.query_params.get('address')
        days = int(request.query_params.get('days', 7))
        
        if not location_id and not address:
            return Response(
                {'error': 'Either location_id or address must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if location_id:
                location = Location.objects.get(id=location_id)
                address = f"{location.latitude},{location.longitude}"
            else:
                location = None
            
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Use Celery for async task if days > 3
            if days > 3:
                task = fetch_weather_async.delay(address, 'today', end_date, request.user.id, location.id if location else None)
                return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
            else:
                client = VisualCrossingAPIClient()
                weather_data = client.get_weather(address, 'today', end_date)
                
                if location:
                    UserSearchHistory.objects.create(user=request.user, location=location)
                    for day in weather_data.get('days', []):
                        WeatherQuery.objects.create(
                            user=request.user,
                            location=location,
                            forecast_date=day['datetime'],
                            raw_data=day
                        )
                
                return Response(weather_data)
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        location_id = request.query_params.get('location_id')
        date = request.query_params.get('date')
        
        if not location_id or not date:
            return Response(
                {'error': 'Both location_id and date must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            location = Location.objects.get(id=location_id)
            client = VisualCrossingAPIClient()
            weather_data = client.get_historical_weather(location, date)
            
            # Save query to history
            UserSearchHistory.objects.create(user=request.user, location=location)
            WeatherQuery.objects.create(
                user=request.user,
                location=location,
                forecast_date=date,
                raw_data=weather_data
            )
            
            return Response(weather_data)
        except Exception as e:
            logger.error(f"Error fetching historical weather: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserSearchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSearchHistorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserSearchHistory.objects.filter(user=self.request.user).order_by('-search_date')
    
    @action(detail=False, methods=['get'])
    def frequent_locations(self, request):
        # Get user's 5 most frequently searched locations
        from django.db.models import Count
        
        locations = (
            UserSearchHistory.objects
            .filter(user=request.user)
            .values('location__id', 'location__name')
            .annotate(search_count=Count('location__id'))
            .order_by('-search_count')[:5]
        )
        
        return Response(locations)
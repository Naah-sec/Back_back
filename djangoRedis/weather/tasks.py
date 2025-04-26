from celery import shared_task
from .services import VisualCrossingAPIClient
from .models import Location, WeatherQuery, UserSearchHistory
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task(bind=True)
def fetch_weather_async(self, address, start_date, end_date, user_id=None, location_id=None):
    try:
        client = VisualCrossingAPIClient()
        weather_data = client.get_weather(address, start_date, end_date)
        
        if user_id and location_id:
            user = User.objects.get(id=user_id)
            location = Location.objects.get(id=location_id)
            
            UserSearchHistory.objects.create(user=user, location=location)
            
            for day in weather_data.get('days', []):
                WeatherQuery.objects.create(
                    user=user,
                    location=location,
                    forecast_date=day['datetime'],
                    raw_data=day
                )
        
        return weather_data
    except Exception as e:
        logger.error(f"Error in async weather fetch: {str(e)}")
        raise self.retry(exc=e, countdown=60)
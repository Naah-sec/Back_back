import requests
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VisualCrossingAPIError(Exception):
    pass

class VisualCrossingAPIClient:
    def __init__(self):
        self.base_url = settings.VISUAL_CROSSING_BASE_URL
        self.api_key = settings.VISUAL_CROSSING_API_KEY
    
    def get_weather(self, location, start_date=None, end_date=None, unit_group='metric', include='days,hours,current'):
        """
        Get weather data from Visual Crossing API
        """
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'unitGroup': unit_group,
            'include': include,
            'key': self.api_key,
            'contentType': 'json',
        }
        
        try:
            # Check if location is a string (address) or a Location model instance
            if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                url = f"{self.base_url}/{location.latitude},{location.longitude}/{start_date}/{end_date}"
            else:
                url = f"{self.base_url}/{location}/{start_date}/{end_date}"
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise VisualCrossingAPIError(f"Failed to fetch weather data: {str(e)}")
    
    def get_historical_weather(self, location, date, unit_group='metric'):
        """
        Get historical weather data
        """
        return self.get_weather(location, start_date=date, end_date=date, unit_group=unit_group)
    
    def get_current_weather(self, location, unit_group='metric'):
        """
        Get current weather data
        """
        return self.get_weather(location, start_date='today', end_date='today', unit_group=unit_group, include='current')
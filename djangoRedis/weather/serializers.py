from rest_framework import serializers
from .models import Location, WeatherQuery, UserSearchHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude']

class WeatherQuerySerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    
    class Meta:
        model = WeatherQuery
        fields = ['id', 'user', 'location', 'query_date', 'forecast_date', 'raw_data']
        read_only_fields = ['user', 'query_date', 'raw_data']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserSearchHistorySerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    user = UserSerializer()
    
    class Meta:
        model = UserSearchHistory
        fields = ['id', 'user', 'location', 'search_date']
        read_only_fields = ['user', 'search_date']
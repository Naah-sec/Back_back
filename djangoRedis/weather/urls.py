from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, WeatherViewSet, UserSearchHistoryViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'weather', WeatherViewSet, basename='weather')
router.register(r'search-history', UserSearchHistoryViewSet, basename='search-history')

urlpatterns = [
    path('', include(router.urls)),
]
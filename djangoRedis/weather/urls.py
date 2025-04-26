from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import LocationViewSet, WeatherViewSet, UserSearchHistoryViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'weather', WeatherViewSet, basename='weather')
router.register(r'search-history', UserSearchHistoryViewSet, basename='search-history')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    
]
# weather/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    def __str__(self):
        return self.name

class WeatherQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    query_date = models.DateTimeField(auto_now_add=True)
    forecast_date = models.DateField()
    raw_data = models.JSONField()
    
    class Meta:
        verbose_name_plural = 'Weather Queries'
        ordering = ['-query_date']
    
    def __str__(self):
        return f"Weather for {self.location} on {self.forecast_date}"

class UserSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    search_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'User Search Histories'
        ordering = ['-search_date']
    
    def __str__(self):
        return f"{self.user} searched for {self.location}"
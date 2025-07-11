"""
Configures the admin panel for TravelTribe.
"""
from django.contrib import admin
from .models import User, Trip

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'date_joined']
    search_fields = ['email', 'name']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'creator', 'start_date', 'end_date', 'created_at']
    search_fields = ['title', 'destination', 'creator__email']
    list_filter = ['start_date', 'end_date']
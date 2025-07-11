
from django.urls import path, include

urlpatterns = [
    path('', include('api.urls.user')),
    path('', include('api.urls.trip')),
]

from django.urls import path, include

urlpatterns = [
    path('users/', include('api.urls.user')),
    path('trips/', include('api.urls.trip')),
    path('reviews/', include('api.urls.review'))
]

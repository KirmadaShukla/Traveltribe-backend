from django.urls import path, include

urlpatterns = [
    path('review/', include('api.urls.review')),
    path('trip/', include('api.urls.trip')),
    path('user/', include('api.urls.user')),
] 
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf.urls import handler404

def api_info(request):
    return JsonResponse({
        'message': 'Welcome to TravelTribe API',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'users': '/api/users/',
            'trips': '/api/trips/',
            'login': '/api/login/',
            'jwt_login': '/api/users/jwt/login/',
            'profile': '/api/users/profile/'
        },
        'status': 'running'
    })

def custom_404(request, exception=None):
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found on this server.',
        'status_code': 404,
        'path': request.path
    }, status=404)

urlpatterns = [
    path('', api_info, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]

handler404 = custom_404
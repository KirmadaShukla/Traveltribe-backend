
from .user import urlpatterns as user_urlpatterns
from .trip import urlpatterns as trip_urlpatterns

urlpatterns = user_urlpatterns + trip_urlpatterns

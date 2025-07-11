
from django.http import JsonResponse
from django.core.exceptions import ValidationError

class GlobalErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return JsonResponse({
                'error': 'Something went wrong',
                'message': str(e)
            }, status=500)

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            return JsonResponse({
                'error': 'Invalid data',
                'message': str(exception)
            }, status=400)
        return None
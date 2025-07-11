
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    logger.error(f"Error: {str(exc)}")
    response = exception_handler(exc, context)

    # Handle Django IntegrityError (e.g., unique constraint)
    if isinstance(exc, IntegrityError):
        # Try to detect duplicate email or other unique constraint
        msg = str(exc)
        if 'unique constraint' in msg and 'email' in msg:
            return Response({
                "error": "Email already exists."
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "error": "A database integrity error occurred.",
            "message": msg
        }, status=status.HTTP_400_BAD_REQUEST)

    # If DRF handled it, wrap all errors in a consistent format
    if response is not None:
        # Validation errors
        if response.status_code == 400 and isinstance(response.data, dict):
            return Response({
                "error": "Validation error",
                "details": response.data
            }, status=400)
        # Auth errors, permission denied, not found, etc.
        detail = response.data.get('detail') if isinstance(response.data, dict) else None
        return Response({
            "error": detail or "An error occurred",
            "status_code": response.status_code
        }, status=response.status_code)

    # Fallback for unhandled errors
    return Response({
        "error": "Something went wrong",
        "message": str(exc)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class TrackingAPIException(Exception):
    """Custom exception for tracking API errors."""
    
    def __init__(self, message, error_code=None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.error_code = error_code or 'TRACKING_ERROR'
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self):
        return self.message


class ValidationException(TrackingAPIException):
    """Exception for validation errors."""
    
    def __init__(self, message, field=None):
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            status_code=status.HTTP_400_BAD_REQUEST
        )
        self.field = field


class GenerationException(TrackingAPIException):
    """Exception for tracking number generation errors."""
    
    def __init__(self, message):
        super().__init__(
            message=message,
            error_code='GENERATION_ERROR',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def custom_exception_handler(exc, context):
    """Custom exception handler for the API."""
    
    # Get correlation ID from request if available
    correlation_id = getattr(context.get('request'), 'correlation_id', None)
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the exception
        logger.error(
            f"API Exception: {str(exc)}",
            extra={
                'correlation_id': correlation_id,
                'status_code': response.status_code,
                'exception_type': type(exc).__name__
            }
        )
        
        # Customize the response format
        custom_response_data = {
            'error': str(exc),
            'status_code': response.status_code,
        }
        
        if correlation_id:
            custom_response_data['correlation_id'] = correlation_id
        
        # Add error details for validation errors
        if hasattr(exc, 'detail'):
            custom_response_data['details'] = exc.detail
        
        response.data = custom_response_data
    
    return response

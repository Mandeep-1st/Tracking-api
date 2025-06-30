import time
import uuid
import logging
from django.utils.deprecation import MiddlewareMixin
from .models import APIMetrics

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging requests and collecting metrics."""
    
    def process_request(self, request):
        """Process incoming request."""
        request.start_time = time.time()
        
        # Add correlation ID if not present
        if not hasattr(request, 'correlation_id'):
            request.correlation_id = str(uuid.uuid4())
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.path}",
            extra={
                'correlation_id': request.correlation_id,
                'method': request.method,
                'path': request.path,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': self._get_client_ip(request)
            }
        )
    
    def process_response(self, request, response):
        """Process outgoing response."""
        if hasattr(request, 'start_time'):
            response_time = int((time.time() - request.start_time) * 1000)
            
            # Log response
            logger.info(
                f"Response: {response.status_code} in {response_time}ms",
                extra={
                    'correlation_id': getattr(request, 'correlation_id', 'unknown'),
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'method': request.method,
                    'path': request.path
                }
            )
            
            # Store metrics (async in production)
            try:
                APIMetrics.objects.create(
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    correlation_id=getattr(request, 'correlation_id', 'unknown')
                )
            except Exception as e:
                logger.warning(f"Failed to store metrics: {str(e)}")
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

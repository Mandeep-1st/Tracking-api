from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
import uuid
import logging
import time

from .serializers import TrackingNumberRequestSerializer, TrackingNumberResponseSerializer
from .services import TrackingService
from .exceptions import TrackingAPIException

logger = logging.getLogger(__name__)


@method_decorator(never_cache, name='dispatch')
class NextTrackingNumberView(APIView):
    """
    API endpoint to generate unique tracking numbers for parcels.
    
    GET /next-tracking-number
    
    Query Parameters:
    - origin_country_id: ISO 3166-1 alpha-2 format (e.g., "MY")
    - destination_country_id: ISO 3166-1 alpha-2 format (e.g., "ID")
    - weight: float in kg, up to 3 decimal places (e.g., "1.234")
    - created_at: RFC 3339 timestamp format (e.g., "2018-11-20T19:29:32+08:00")
    - customer_id: UUID (e.g., "de619854-b59b-425e-9db4-943979e1bd49")
    - customer_name: string (e.g., "RedBox Logistics")
    - customer_slug: slug/kebab-case string (e.g., "redbox-logistics")
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tracking_service = TrackingService()
    
    def get(self, request):
        """Handle GET request for tracking number generation."""
        start_time = time.time()
        correlation_id = str(uuid.uuid4())
        
        # Add correlation ID to request for tracking
        request.correlation_id = correlation_id
        
        logger.info(
            "Received tracking number generation request",
            extra={
                'correlation_id': correlation_id,
                'query_params': dict(request.query_params),
                'method': 'GET',
                'endpoint': '/next-tracking-number'
            }
        )
        
        try:
            # Validate input parameters
            serializer = TrackingNumberRequestSerializer(data=request.query_params)
            
            if not serializer.is_valid():
                logger.warning(
                    f"Invalid request parameters: {serializer.errors}",
                    extra={'correlation_id': correlation_id}
                )
                return Response(
                    {
                        'error': 'Invalid request parameters',
                        'details': serializer.errors,
                        'correlation_id': correlation_id
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate tracking number
            result = self.tracking_service.create_tracking_number(
                validated_data=serializer.validated_data,
                correlation_id=correlation_id
            )
            
            # Serialize response
            response_serializer = TrackingNumberResponseSerializer(result)
            
            # Log successful response
            response_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"Successfully generated tracking number in {response_time}ms",
                extra={
                    'correlation_id': correlation_id,
                    'tracking_number': result['tracking_number'],
                    'response_time_ms': response_time
                }
            )
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except TrackingAPIException as e:
            response_time = int((time.time() - start_time) * 1000)
            logger.error(
                f"Tracking API error: {str(e)}",
                extra={
                    'correlation_id': correlation_id,
                    'response_time_ms': response_time,
                    'error_code': e.error_code
                }
            )
            return Response(
                {
                    'error': str(e),
                    'error_code': e.error_code,
                    'correlation_id': correlation_id
                },
                status=e.status_code
            )
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            logger.error(
                f"Unexpected error: {str(e)}",
                extra={
                    'correlation_id': correlation_id,
                    'response_time_ms': response_time
                }
            )
            return Response(
                {
                    'error': 'Internal server error',
                    'correlation_id': correlation_id
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""
    
    def get(self, request):
        """Return API health status."""
        return Response({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0'
        })


class MetricsView(APIView):
    """Basic metrics endpoint for monitoring."""
    
    def get(self, request):
        """Return basic API metrics."""
        try:
            from .models import TrackingNumberRequest, APIMetrics
            from django.db.models import Count, Avg
            from datetime import datetime, timedelta
            
            # Get metrics for last 24 hours
            last_24h = datetime.now() - timedelta(hours=24)
            
            tracking_stats = TrackingNumberRequest.objects.filter(
                created_at__gte=last_24h
            ).aggregate(
                total_requests=Count('id')
            )
            
            api_stats = APIMetrics.objects.filter(
                timestamp__gte=last_24h
            ).aggregate(
                total_api_calls=Count('id'),
                avg_response_time=Avg('response_time_ms'),
                success_rate=Count('id', filter=models.Q(status_code__lt=400)) * 100.0 / Count('id')
            )
            
            return Response({
                'period': '24h',
                'tracking_requests': tracking_stats['total_requests'] or 0,
                'api_calls': api_stats['total_api_calls'] or 0,
                'avg_response_time_ms': round(api_stats['avg_response_time'] or 0, 2),
                'success_rate_percent': round(api_stats['success_rate'] or 0, 2),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            return Response(
                {'error': 'Unable to retrieve metrics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

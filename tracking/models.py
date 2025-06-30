from django.db import models
import uuid


class TrackingNumberRequest(models.Model):
    """Model to log tracking number generation requests for monitoring."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_number = models.CharField(max_length=16, db_index=True, unique=True)
    origin_country_id = models.CharField(max_length=2)
    destination_country_id = models.CharField(max_length=2)
    weight = models.DecimalField(max_digits=10, decimal_places=3)
    customer_id = models.UUIDField()
    customer_name = models.CharField(max_length=255)
    customer_slug = models.CharField(max_length=255)
    request_timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    correlation_id = models.CharField(max_length=36, db_index=True)
    
    class Meta:
        db_table = 'tracking_requests'
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Tracking: {self.tracking_number} - {self.customer_name}"


class APIMetrics(models.Model):
    """Model to store API metrics for monitoring."""
    
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    correlation_id = models.CharField(max_length=36)
    
    class Meta:
        db_table = 'api_metrics'
        indexes = [
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['status_code']),
        ]

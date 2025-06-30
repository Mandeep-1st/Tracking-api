from django.contrib import admin
from .models import TrackingNumberRequest, APIMetrics


@admin.register(TrackingNumberRequest)
class TrackingNumberRequestAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_number', 'customer_name', 'origin_country_id', 
        'destination_country_id', 'weight', 'created_at'
    ]
    list_filter = ['origin_country_id', 'destination_country_id', 'created_at']
    search_fields = ['tracking_number', 'customer_name', 'customer_slug']
    readonly_fields = ['id', 'created_at', 'correlation_id']


@admin.register(APIMetrics)
class APIMetricsAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'method', 'status_code', 'response_time_ms', 'timestamp']
    list_filter = ['endpoint', 'method', 'status_code', 'timestamp']
    readonly_fields = ['timestamp', 'correlation_id']

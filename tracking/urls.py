from django.urls import path
from .views import NextTrackingNumberView, HealthCheckView, MetricsView

urlpatterns = [
    path('next-tracking-number', NextTrackingNumberView.as_view(), name='next-tracking-number'),
    path('health', HealthCheckView.as_view(), name='health-check'),
    path('metrics', MetricsView.as_view(), name='metrics'),
]

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import json


class NextTrackingNumberViewTest(TestCase):
    """Test cases for NextTrackingNumberView."""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('next-tracking-number')
        self.valid_params = {
            'origin_country_id': 'MY',
            'destination_country_id': 'ID',
            'weight': '1.234',
            'created_at': '2018-11-20T19:29:32+08:00',
            'customer_id': 'de619854-b59b-425e-9db4-943979e1bd49',
            'customer_name': 'RedBox Logistics',
            'customer_slug': 'redbox-logistics'
        }
    
    @patch('tracking.views.TrackingService')
    def test_successful_tracking_number_generation(self, mock_service_class):
        """Test successful tracking number generation."""
        # Mock service response
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.create_tracking_number.return_value = {
            'tracking_number': 'MYID123456789',
            'created_at': '2023-11-20T19:29:32+08:00',
            'correlation_id': 'test-correlation-id',
            'request_metadata': {
                'origin_country': 'MY',
                'destination_country': 'ID',
                'weight_kg': '1.234',
                'customer_slug': 'redbox-logistics'
            }
        }
        
        response = self.client.get(self.url, self.valid_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('tracking_number', data)
        self.assertIn('created_at', data)
        self.assertIn('correlation_id', data)
        self.assertEqual(data['tracking_number'], 'MYID123456789')
    
    def test_missing_required_parameter(self):
        """Test error when required parameter is missing."""
        params = self.valid_params.copy()
        del params['origin_country_id']
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('details', data)
    
    def test_invalid_country_code_format(self):
        """Test error with invalid country code format."""
        params = self.valid_params.copy()
        params['origin_country_id'] = 'INVALID'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
    
    def test_invalid_weight_format(self):
        """Test error with invalid weight format."""
        params = self.valid_params.copy()
        params['weight'] = 'invalid_weight'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_uuid_format(self):
        """Test error with invalid UUID format."""
        params = self.valid_params.copy()
        params['customer_id'] = 'invalid-uuid'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_datetime_format(self):
        """Test error with invalid datetime format."""
        params = self.valid_params.copy()
        params['created_at'] = 'invalid-datetime'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_customer_slug_format(self):
        """Test error with invalid customer slug format."""
        params = self.valid_params.copy()
        params['customer_slug'] = 'Invalid_Slug'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_negative_weight(self):
        """Test error with negative weight."""
        params = self.valid_params.copy()
        params['weight'] = '-1.0'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_zero_weight(self):
        """Test error with zero weight."""
        params = self.valid_params.copy()
        params['weight'] = '0.0'
        
        response = self.client.get(self.url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class HealthCheckViewTest(TestCase):
    """Test cases for HealthCheckView."""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('health-check')
    
    def test_health_check_success(self):
        """Test health check endpoint returns success."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)


class MetricsViewTest(TestCase):
    """Test cases for MetricsView."""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('metrics')
    
    @patch('tracking.models.TrackingNumberRequest.objects.filter')
    @patch('tracking.models.APIMetrics.objects.filter')
    def test_metrics_success(self, mock_api_metrics, mock_tracking_requests):
        """Test metrics endpoint returns data."""
        # Mock database queries
        mock_tracking_requests.return_value.aggregate.return_value = {'total_requests': 10}
        mock_api_metrics.return_value.aggregate.return_value = {
            'total_api_calls': 20,
            'avg_response_time': 150.5,
            'success_rate': 95.0
        }
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('tracking_requests', data)
        self.assertIn('api_calls', data)
        self.assertIn('avg_response_time_ms', data)
        self.assertIn('success_rate_percent', data)

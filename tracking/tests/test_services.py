import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from decimal import Decimal
import uuid

from django.test import TestCase
from tracking.services import TrackingNumberGenerator, TrackingService


class TrackingNumberGeneratorTest(TestCase):
    """Test cases for TrackingNumberGenerator."""
    
    def setUp(self):
        self.generator = TrackingNumberGenerator()
        self.test_data = {
            'origin_country_id': 'MY',
            'destination_country_id': 'ID',
            'weight': 1.234,
            'created_at': datetime(2023, 11, 20, 19, 29, 32),
            'customer_id': 'de619854-b59b-425e-9db4-943979e1bd49',
            'customer_name': 'RedBox Logistics',
            'customer_slug': 'redbox-logistics',
            'correlation_id': str(uuid.uuid4())
        }
    
    def test_generate_tracking_number_format(self):
        """Test that generated tracking number matches required format."""
        tracking_number = self.generator.generate_tracking_number(**self.test_data)
        
        # Should match regex ^[A-Z0-9]{1,16}$
        self.assertRegex(tracking_number, r'^[A-Z0-9]{1,16}$')
        self.assertLessEqual(len(tracking_number), 16)
        self.assertGreaterEqual(len(tracking_number), 1)
    
    def test_generate_tracking_number_uniqueness(self):
        """Test that different inputs generate different tracking numbers."""
        tracking_number1 = self.generator.generate_tracking_number(**self.test_data)
        
        # Change one parameter
        modified_data = self.test_data.copy()
        modified_data['weight'] = 2.345
        tracking_number2 = self.generator.generate_tracking_number(**modified_data)
        
        self.assertNotEqual(tracking_number1, tracking_number2)
    
    def test_generate_tracking_number_deterministic(self):
        """Test that same inputs generate same tracking number."""
        tracking_number1 = self.generator.generate_tracking_number(**self.test_data)
        tracking_number2 = self.generator.generate_tracking_number(**self.test_data)
        
        self.assertEqual(tracking_number1, tracking_number2)
    
    def test_generate_tracking_number_with_different_correlation_ids(self):
        """Test that different correlation IDs generate different tracking numbers."""
        tracking_number1 = self.generator.generate_tracking_number(**self.test_data)
        
        modified_data = self.test_data.copy()
        modified_data['correlation_id'] = str(uuid.uuid4())
        tracking_number2 = self.generator.generate_tracking_number(**modified_data)
        
        self.assertNotEqual(tracking_number1, tracking_number2)
    
    def test_to_base36_conversion(self):
        """Test base36 conversion utility method."""
        self.assertEqual(self.generator._to_base36(0), '0')
        self.assertEqual(self.generator._to_base36(35), 'Z')
        self.assertEqual(self.generator._to_base36(36), '10')
        self.assertEqual(self.generator._to_base36(1295), 'ZZ')


class TrackingServiceTest(TestCase):
    """Test cases for TrackingService."""
    
    def setUp(self):
        self.service = TrackingService()
        self.correlation_id = str(uuid.uuid4())
        self.validated_data = {
            'origin_country_id': 'MY',
            'destination_country_id': 'ID',
            'weight': Decimal('1.234'),
            'created_at': datetime(2023, 11, 20, 19, 29, 32),
            'customer_id': 'de619854-b59b-425e-9db4-943979e1bd49',
            'customer_name': 'RedBox Logistics',
            'customer_slug': 'redbox-logistics'
        }
    
    @patch('tracking.services.TrackingService._log_tracking_request')
    def test_create_tracking_number_success(self, mock_log):
        """Test successful tracking number creation."""
        result = self.service.create_tracking_number(
            validated_data=self.validated_data,
            correlation_id=self.correlation_id
        )
        
        # Check response structure
        self.assertIn('tracking_number', result)
        self.assertIn('created_at', result)
        self.assertIn('correlation_id', result)
        self.assertIn('request_metadata', result)
        
        # Check tracking number format
        self.assertRegex(result['tracking_number'], r'^[A-Z0-9]{1,16}$')
        
        # Check correlation ID
        self.assertEqual(result['correlation_id'], self.correlation_id)
        
        # Check that logging was called
        mock_log.assert_called_once()
    
    @patch('tracking.services.TrackingService._log_tracking_request')
    def test_create_tracking_number_metadata(self, mock_log):
        """Test that response includes correct metadata."""
        result = self.service.create_tracking_number(
            validated_data=self.validated_data,
            correlation_id=self.correlation_id
        )
        
        metadata = result['request_metadata']
        self.assertEqual(metadata['origin_country'], 'MY')
        self.assertEqual(metadata['destination_country'], 'ID')
        self.assertEqual(metadata['weight_kg'], '1.234')
        self.assertEqual(metadata['customer_slug'], 'redbox-logistics')
    
    @patch('tracking.models.TrackingNumberRequest.objects.create')
    def test_log_tracking_request(self, mock_create):
        """Test tracking request logging."""
        tracking_number = 'MYID123456789'
        
        self.service._log_tracking_request(
            validated_data=self.validated_data,
            tracking_number=tracking_number,
            correlation_id=self.correlation_id
        )
        
        # Check that model create was called with correct data
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        
        self.assertEqual(call_args['tracking_number'], tracking_number)
        self.assertEqual(call_args['origin_country_id'], 'MY')
        self.assertEqual(call_args['destination_country_id'], 'ID')
        self.assertEqual(call_args['correlation_id'], self.correlation_id)

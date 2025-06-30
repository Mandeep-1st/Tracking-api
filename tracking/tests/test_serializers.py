from django.test import TestCase
from tracking.serializers import TrackingNumberRequestSerializer
from rest_framework import serializers


class TrackingNumberRequestSerializerTest(TestCase):
    """Test cases for TrackingNumberRequestSerializer."""
    
    def setUp(self):
        self.valid_data = {
            'origin_country_id': 'MY',
            'destination_country_id': 'ID',
            'weight': '1.234',
            'created_at': '2018-11-20T19:29:32+08:00',
            'customer_id': 'de619854-b59b-425e-9db4-943979e1bd49',
            'customer_name': 'RedBox Logistics',
            'customer_slug': 'redbox-logistics'
        }
    
    def test_valid_data_serialization(self):
        """Test serialization with valid data."""
        serializer = TrackingNumberRequestSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['origin_country_id'], 'MY')
        self.assertEqual(validated_data['destination_country_id'], 'ID')
        self.assertEqual(str(validated_data['weight']), '1.234')
    
    def test_country_id_validation_lowercase(self):
        """Test country ID validation converts to uppercase."""
        data = self.valid_data.copy()
        data['origin_country_id'] = 'my'
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['origin_country_id'], 'MY')
    
    def test_invalid_country_id_format(self):
        """Test validation fails for invalid country ID format."""
        data = self.valid_data.copy()
        data['origin_country_id'] = 'USA'  # 3 characters instead of 2
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('origin_country_id', serializer.errors)
    
    def test_invalid_country_id_numbers(self):
        """Test validation fails for country ID with numbers."""
        data = self.valid_data.copy()
        data['origin_country_id'] = 'M1'
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('origin_country_id', serializer.errors)
    
    def test_invalid_weight_negative(self):
        """Test validation fails for negative weight."""
        data = self.valid_data.copy()
        data['weight'] = '-1.0'
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('weight', serializer.errors)
    
    def test_invalid_weight_zero(self):
        """Test validation fails for zero weight."""
        data = self.valid_data.copy()
        data['weight'] = '0.0'
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('weight', serializer.errors)
    
    def test_invalid_datetime_format(self):
        """Test validation fails for invalid datetime format."""
        data = self.valid_data.copy()
        data['created_at'] = '2018-11-20 19:29:32'  # Missing timezone
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('created_at', serializer.errors)
    
    def test_invalid_uuid_format(self):
        """Test validation fails for invalid UUID format."""
        data = self.valid_data.copy()
        data['customer_id'] = 'not-a-uuid'
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer_id', serializer.errors)
    
    def test_invalid_customer_slug_format(self):
        """Test validation fails for invalid customer slug format."""
        data = self.valid_data.copy()
        data['customer_slug'] = 'Invalid_Slug'  # Underscore not allowed
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer_slug', serializer.errors)
    
    def test_valid_customer_slug_formats(self):
        """Test various valid customer slug formats."""
        valid_slugs = [
            'redbox-logistics',
            'simple',
            'multi-word-slug',
            'with123numbers',
            'a-b-c-d-e'
        ]
        
        for slug in valid_slugs:
            data = self.valid_data.copy()
            data['customer_slug'] = slug
            
            serializer = TrackingNumberRequestSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Failed for slug: {slug}")
    
    def test_empty_customer_name(self):
        """Test validation fails for empty customer name."""
        data = self.valid_data.copy()
        data['customer_name'] = ''
        
        serializer = TrackingNumberRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer_name', serializer.errors)

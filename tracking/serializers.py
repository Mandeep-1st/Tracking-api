from rest_framework import serializers
from datetime import datetime
import uuid
import re
from django.utils.dateparse import parse_datetime


class TrackingNumberRequestSerializer(serializers.Serializer):
    """Serializer for tracking number generation request."""
    
    origin_country_id = serializers.CharField(max_length=2, min_length=2)
    destination_country_id = serializers.CharField(max_length=2, min_length=2)
    weight = serializers.DecimalField(max_digits=10, decimal_places=3, min_value=0.001)
    created_at = serializers.CharField()
    customer_id = serializers.CharField()
    customer_name = serializers.CharField(max_length=255, min_length=1)
    customer_slug = serializers.CharField(max_length=255, min_length=1)
    
    def validate_origin_country_id(self, value):
        """Validate origin country ID is ISO 3166-1 alpha-2 format."""
        if not re.match(r'^[A-Z]{2}$', value.upper()):
            raise serializers.ValidationError(
                "Origin country ID must be ISO 3166-1 alpha-2 format (e.g., 'MY')"
            )
        return value.upper()
    
    def validate_destination_country_id(self, value):
        """Validate destination country ID is ISO 3166-1 alpha-2 format."""
        if not re.match(r'^[A-Z]{2}$', value.upper()):
            raise serializers.ValidationError(
                "Destination country ID must be ISO 3166-1 alpha-2 format (e.g., 'ID')"
            )
        return value.upper()
    
    def validate_created_at(self, value):
        """Validate created_at is RFC 3339 timestamp format."""
        try:
            parsed_datetime = parse_datetime(value)
            if parsed_datetime is None:
                raise ValueError("Invalid datetime format")
            return parsed_datetime
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                "created_at must be RFC 3339 timestamp format (e.g., '2018-11-20T19:29:32+08:00')"
            )
    
    def validate_customer_id(self, value):
        """Validate customer_id is a valid UUID."""
        try:
            uuid_obj = uuid.UUID(value)
            return str(uuid_obj)
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                "customer_id must be a valid UUID (e.g., 'de619854-b59b-425e-9db4-943979e1bd49')"
            )
    
    def validate_customer_slug(self, value):
        """Validate customer_slug is kebab-case format."""
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', value):
            raise serializers.ValidationError(
                "customer_slug must be kebab-case format (e.g., 'redbox-logistics')"
            )
        return value


class TrackingNumberResponseSerializer(serializers.Serializer):
    """Serializer for tracking number generation response."""
    
    tracking_number = serializers.CharField(max_length=16)
    created_at = serializers.DateTimeField()
    correlation_id = serializers.CharField(max_length=36)
    request_metadata = serializers.DictField(read_only=True)

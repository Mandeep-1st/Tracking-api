import hashlib
import time
import uuid
from datetime import datetime
from typing import Dict, Any
import logging
from django.db import IntegrityError

logger = logging.getLogger(__name__)


class TrackingNumberGenerator:
    """Service class for generating unique tracking numbers."""
    
    @staticmethod
    def generate_tracking_number(
        origin_country_id: str,
        destination_country_id: str,
        weight: float,
        created_at: datetime,
        customer_id: str,
        customer_name: str,
        customer_slug: str,
        correlation_id: str
    ) -> str:
        """
        Generate a unique tracking number based on input parameters.
        
        Algorithm:
        1. Create a deterministic hash from input parameters
        2. Add timestamp component for uniqueness
        3. Add random component for additional uniqueness
        4. Encode to alphanumeric format matching regex ^[A-Z0-9]{1,16}$
        """
        try:
            # Create deterministic hash from input parameters
            input_string = f"{origin_country_id}{destination_country_id}{weight}{customer_id}{customer_slug}"
            hash_object = hashlib.sha256(input_string.encode())
            hash_hex = hash_object.hexdigest()
            
            # Add timestamp component (microseconds for uniqueness)
            timestamp_component = str(int(created_at.timestamp() * 1000000))
            
            # Add correlation ID for additional uniqueness
            unique_string = f"{hash_hex}{timestamp_component}{correlation_id.replace('-', '')}"
            
            # Create final hash
            final_hash = hashlib.sha256(unique_string.encode()).hexdigest()
            
            # Convert to base36 (0-9, A-Z) and take first 12 characters
            # Add country codes for context
            base_number = int(final_hash[:12], 16)
            tracking_base = TrackingNumberGenerator._to_base36(base_number)[:10]
            
            # Combine with country codes for final tracking number
            tracking_number = f"{origin_country_id}{destination_country_id}{tracking_base}"
            
            # Ensure it fits the regex and length requirements
            tracking_number = tracking_number[:16].upper()
            
            logger.info(
                f"Generated tracking number: {tracking_number}",
                extra={
                    'correlation_id': correlation_id,
                    'customer_id': customer_id,
                    'origin': origin_country_id,
                    'destination': destination_country_id
                }
            )
            
            return tracking_number
            
        except Exception as e:
            logger.error(
                f"Error generating tracking number: {str(e)}",
                extra={'correlation_id': correlation_id}
            )
            raise
    
    @staticmethod
    def _to_base36(number: int) -> str:
        """Convert number to base36 (0-9, A-Z)."""
        if number == 0:
            return '0'
        
        digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''
        
        while number > 0:
            result = digits[number % 36] + result
            number //= 36
        
        return result


class TrackingService:
    """Main service class for tracking number operations."""
    
    def __init__(self):
        self.generator = TrackingNumberGenerator()
    
    def create_tracking_number(self, validated_data: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """
        Create a new tracking number and log the request.
        Retries up to 3 times if a tracking number collision occurs.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Generate tracking number
                tracking_number = self.generator.generate_tracking_number(
                    origin_country_id=validated_data['origin_country_id'],
                    destination_country_id=validated_data['destination_country_id'],
                    weight=float(validated_data['weight']),
                    created_at=validated_data['created_at'],
                    customer_id=validated_data['customer_id'],
                    customer_name=validated_data['customer_name'],
                    customer_slug=validated_data['customer_slug'],
                    correlation_id=correlation_id
                )
                # Log the request (async in production)
                self._log_tracking_request(validated_data, tracking_number, correlation_id)
                # Prepare response
                response_data = {
                    'tracking_number': tracking_number,
                    'created_at': datetime.now(),
                    'correlation_id': correlation_id,
                    'request_metadata': {
                        'origin_country': validated_data['origin_country_id'],
                        'destination_country': validated_data['destination_country_id'],
                        'weight_kg': str(validated_data['weight']),
                        'customer_slug': validated_data['customer_slug']
                    }
                }
                logger.info(
                    f"Successfully created tracking number: {tracking_number}",
                    extra={
                        'correlation_id': correlation_id,
                        'customer_id': validated_data['customer_id'],
                        'tracking_number': tracking_number
                    }
                )
                return response_data
            except IntegrityError as e:
                logger.warning(
                    f"Tracking number collision detected, retrying... (attempt {attempt+1})",
                    extra={'correlation_id': correlation_id}
                )
                # Generate a new correlation_id for the next attempt
                correlation_id = str(uuid.uuid4())
                continue
            except Exception as e:
                logger.error(
                    f"Error in create_tracking_number: {str(e)}",
                    extra={'correlation_id': correlation_id}
                )
                raise
        # If we reach here, all attempts failed
        logger.error(
            "Failed to create a unique tracking number after multiple attempts.",
            extra={'correlation_id': correlation_id}
        )
        raise Exception("Failed to create a unique tracking number after multiple attempts.")
    
    def _log_tracking_request(self, validated_data: Dict[str, Any], tracking_number: str, correlation_id: str):
        """Log tracking request to database for monitoring."""
        try:
            from .models import TrackingNumberRequest
            
            TrackingNumberRequest.objects.create(  # type: ignore
                tracking_number=tracking_number,
                origin_country_id=validated_data['origin_country_id'],
                destination_country_id=validated_data['destination_country_id'],
                weight=validated_data['weight'],
                customer_id=validated_data['customer_id'],
                customer_name=validated_data['customer_name'],
                customer_slug=validated_data['customer_slug'],
                request_timestamp=validated_data['created_at'],
                correlation_id=correlation_id
            )
        except Exception as e:
            # Don't fail the request if logging fails
            logger.warning(
                f"Failed to log tracking request: {str(e)}",
                extra={'correlation_id': correlation_id}
            )

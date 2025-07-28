"""SMS provider implementations for different SMS services."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SMSProvider(ABC):
    """Abstract base class for SMS providers."""
    
    def __init__(self):
        """Initialize SMS provider."""
        self.provider_name = "base"
    
    @abstractmethod
    async def send_message(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message.
        
        Args:
            to_phone: Recipient phone number in E.164 format.
            message: Message content.
            from_phone: Sender phone number.
            
        Returns:
            dict: Send result with success status and metadata.
        """
        pass
    
    @abstractmethod
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of a message."""
        pass
    
    @abstractmethod
    async def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Validate phone number format and availability."""
        pass


class TwilioProvider(SMSProvider):
    """Twilio SMS provider implementation."""
    
    def __init__(self):
        """Initialize Twilio provider."""
        super().__init__()
        self.provider_name = "twilio"
        
        # Twilio credentials
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_phone = settings.TWILIO_FROM_PHONE
        
        # Initialize Twilio client
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twilio client."""
        try:
            from twilio.rest import Client
            
            if self.account_sid and self.auth_token:
                self._client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully")
            else:
                logger.warning("Twilio credentials not provided, using mock mode")
                self._client = None
                
        except ImportError:
            logger.warning("Twilio library not installed, using mock mode")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            self._client = None
    
    async def send_message(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS message via Twilio."""
        try:
            if not self._client:
                # Mock mode for development/testing
                return await self._mock_send_message(to_phone, message, from_phone)
            
            sender_phone = from_phone or self.from_phone
            
            # Send message via Twilio
            twilio_message = self._client.messages.create(
                body=message,
                from_=sender_phone,
                to=to_phone
            )
            
            logger.info(
                "SMS sent via Twilio",
                message_id=twilio_message.sid,
                to_phone=to_phone,
                status=twilio_message.status,
            )
            
            return {
                "success": True,
                "message_id": twilio_message.sid,
                "status": twilio_message.status,
                "to_phone": to_phone,
                "from_phone": sender_phone,
                "provider": "twilio",
                "cost": self._estimate_cost(message),
            }
            
        except Exception as e:
            logger.error(f"Twilio SMS send failed: {e}")
            
            # Extract Twilio-specific error information
            error_info = {
                "success": False,
                "error": str(e),
                "provider": "twilio",
                "to_phone": to_phone,
            }
            
            # Handle Twilio-specific errors
            if hasattr(e, 'code'):
                error_info["error_code"] = e.code
                error_info["provider_error"] = str(e)
                
                # Map common Twilio errors
                if e.code == 21211:
                    error_info["error_type"] = "invalid_phone_number"
                elif e.code == 21408:
                    error_info["error_type"] = "permission_denied"
                elif e.code == 21610:
                    error_info["error_type"] = "unsubscribed"
            
            return error_info
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get message delivery status from Twilio."""
        try:
            if not self._client:
                return {
                    "success": False,
                    "error": "Twilio client not available",
                }
            
            message = self._client.messages(message_id).fetch()
            
            return {
                "success": True,
                "message_id": message_id,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "date_updated": message.date_updated.isoformat() if message.date_updated else None,
                "price": message.price,
                "price_unit": message.price_unit,
            }
            
        except Exception as e:
            logger.error(f"Failed to get Twilio message status: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_id": message_id,
            }
    
    async def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Validate phone number using Twilio Lookup API."""
        try:
            if not self._client:
                return {
                    "success": False,
                    "error": "Twilio client not available",
                }
            
            # Use Twilio Lookup API
            try:
                phone_info = self._client.lookups.v2.phone_numbers(phone_number).fetch()
                
                return {
                    "success": True,
                    "phone_number": phone_number,
                    "valid": phone_info.valid,
                    "formatted": phone_info.phone_number,
                    "country_code": phone_info.country_code,
                    "carrier": phone_info.carrier,
                    "line_type": phone_info.line_type_intelligence.get("type") if phone_info.line_type_intelligence else None,
                }
                
            except Exception as lookup_error:
                # Fallback to basic validation
                return {
                    "success": True,
                    "phone_number": phone_number,
                    "valid": False,
                    "error": str(lookup_error),
                }
                
        except Exception as e:
            logger.error(f"Phone number validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number,
            }
    
    async def _mock_send_message(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock SMS sending for development/testing."""
        import uuid
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Generate mock message ID
        mock_message_id = f"SM{uuid.uuid4().hex[:32]}"
        
        logger.info(
            f"MOCK SMS: To {to_phone}, Message: {message[:50]}...",
            message_id=mock_message_id,
        )
        
        return {
            "success": True,
            "message_id": mock_message_id,
            "status": "queued",
            "to_phone": to_phone,
            "from_phone": from_phone or self.from_phone,
            "provider": "twilio_mock",
            "cost": self._estimate_cost(message),
        }
    
    def _estimate_cost(self, message: str) -> float:
        """Estimate SMS cost based on message length."""
        # Twilio pricing: ~$0.0075 per SMS segment
        segments = (len(message) + 159) // 160  # 160 chars per segment
        return round(segments * 0.0075, 4)


class AWSProvider(SMSProvider):
    """AWS SNS SMS provider implementation."""
    
    def __init__(self):
        """Initialize AWS SNS provider."""
        super().__init__()
        self.provider_name = "aws_sns"
        
        # AWS credentials
        self.aws_access_key = settings.AWS_ACCESS_KEY_ID
        self.aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.aws_region = settings.AWS_REGION
        
        # Initialize AWS client
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS SNS client."""
        try:
            import boto3
            
            if self.aws_access_key and self.aws_secret_key:
                self._client = boto3.client(
                    'sns',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
                logger.info("AWS SNS client initialized successfully")
            else:
                logger.warning("AWS credentials not provided, using mock mode")
                self._client = None
                
        except ImportError:
            logger.warning("boto3 library not installed, using mock mode")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize AWS SNS client: {e}")
            self._client = None
    
    async def send_message(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS message via AWS SNS."""
        try:
            if not self._client:
                # Mock mode for development/testing
                return await self._mock_send_message(to_phone, message, from_phone)
            
            # Publish message to SNS
            response = self._client.publish(
                PhoneNumber=to_phone,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': from_phone or 'SMS'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(
                "SMS sent via AWS SNS",
                message_id=response['MessageId'],
                to_phone=to_phone,
            )
            
            return {
                "success": True,
                "message_id": response['MessageId'],
                "status": "sent",
                "to_phone": to_phone,
                "from_phone": from_phone,
                "provider": "aws_sns",
                "cost": self._estimate_cost(message),
            }
            
        except Exception as e:
            logger.error(f"AWS SNS SMS send failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "aws_sns",
                "to_phone": to_phone,
            }
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get message delivery status from AWS SNS."""
        # AWS SNS doesn't provide delivery status tracking for SMS
        return {
            "success": False,
            "error": "AWS SNS does not support SMS delivery status tracking",
            "message_id": message_id,
        }
    
    async def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Validate phone number (basic validation for AWS SNS)."""
        import re
        
        # Basic E.164 format validation
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        
        if re.match(e164_pattern, phone_number):
            return {
                "success": True,
                "phone_number": phone_number,
                "valid": True,
                "formatted": phone_number,
            }
        else:
            return {
                "success": True,
                "phone_number": phone_number,
                "valid": False,
                "error": "Invalid E.164 format",
            }
    
    async def _mock_send_message(
        self,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock SMS sending for development/testing."""
        import uuid
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Generate mock message ID
        mock_message_id = str(uuid.uuid4())
        
        logger.info(
            f"MOCK AWS SNS SMS: To {to_phone}, Message: {message[:50]}...",
            message_id=mock_message_id,
        )
        
        return {
            "success": True,
            "message_id": mock_message_id,
            "status": "sent",
            "to_phone": to_phone,
            "from_phone": from_phone,
            "provider": "aws_sns_mock",
            "cost": self._estimate_cost(message),
        }
    
    def _estimate_cost(self, message: str) -> float:
        """Estimate SMS cost for AWS SNS."""
        # AWS SNS pricing: ~$0.00645 per SMS
        return 0.00645


def get_sms_provider(provider_name: str = None) -> SMSProvider:
    """
    Get SMS provider instance.
    
    Args:
        provider_name: Name of the provider to use.
        
    Returns:
        SMSProvider: Provider instance.
    """
    provider_name = provider_name or settings.SMS_PROVIDER
    
    if provider_name == "twilio":
        return TwilioProvider()
    elif provider_name == "aws_sns":
        return AWSProvider()
    else:
        logger.warning(f"Unknown SMS provider: {provider_name}, using Twilio")
        return TwilioProvider()
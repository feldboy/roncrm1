"""SMS Service Agent implementation."""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...config.settings import get_settings
from ...models.database import Plaintiff, Communication
from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger
from ..base.agent import BaseAgent, AgentTask, AgentResponse
from ..base.communication import agent_communication
from .providers import SMSProvider, TwilioProvider
from .compliance import SMSComplianceTracker
from .templates import SMSTemplateEngine

logger = get_logger(__name__)
settings = get_settings()


class SMSServiceAgent(BaseAgent):
    """
    SMS Service Agent for automated SMS communication.
    
    Handles SMS sending, compliance tracking, opt-in/opt-out management,
    template management, and automated SMS workflows.
    """
    
    def __init__(self, config):
        """Initialize the SMS Service Agent."""
        super().__init__(config)
        
        # Initialize SMS components
        self.ai_client = OpenAIClient()
        self.sms_provider = TwilioProvider() if settings.SMS_PROVIDER == "twilio" else SMSProvider()
        self.compliance_tracker = SMSComplianceTracker()
        self.template_engine = SMSTemplateEngine(self.ai_client)
        
        # Operation handlers
        self._handlers = {
            "send_sms": self._send_sms,
            "send_templated_sms": self._send_templated_sms,
            "send_bulk_sms": self._send_bulk_sms,
            "handle_inbound_sms": self._handle_inbound_sms,
            "handle_opt_out": self._handle_opt_out,
            "handle_opt_in": self._handle_opt_in,
            "check_opt_in_status": self._check_opt_in_status,
            "schedule_sms": self._schedule_sms,
            "process_scheduled_sms": self._process_scheduled_sms,
            "create_sms_template": self._create_sms_template,
            "get_sms_template": self._get_sms_template,
            "list_sms_templates": self._list_sms_templates,
            "validate_phone_numbers": self._validate_phone_numbers,
            "get_sms_analytics": self._get_sms_analytics,
            "generate_sms_content": self._generate_sms_content,
            "check_compliance": self._check_compliance,
        }
        
        # SMS statistics
        self.sms_stats = {
            "total_sent": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "inbound_messages": 0,
            "opt_outs": 0,
            "opt_ins": 0,
            "compliance_violations": 0,
            "last_sent": None,
        }
        
        # Compliance settings
        self.compliance_rules = {
            "require_opt_in": True,
            "include_opt_out_instructions": True,
            "respect_quiet_hours": True,
            "quiet_hours_start": "21:00",  # 9 PM
            "quiet_hours_end": "08:00",    # 8 AM
            "max_daily_messages": 3,
            "max_message_length": 160,
            "prohibited_keywords": [
                "guaranteed", "risk-free", "urgent", "act now",
                "limited time", "instant", "winner"
            ],
        }
        
        self.logger.info("SMS Service Agent initialized")
    
    def get_operation_handler(self, operation: str) -> Optional[callable]:
        """Get the handler function for a specific operation."""
        return self._handlers.get(operation)
    
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a task with comprehensive error handling and metrics.
        
        Args:
            task: The task to process.
            
        Returns:
            AgentResponse: The result of processing the task.
        """
        start_time = datetime.utcnow()
        
        try:
            # Get operation handler
            handler = self.get_operation_handler(task.operation)
            if not handler:
                return self.create_error_response(
                    task.id,
                    f"Unknown operation: {task.operation}"
                )
            
            # Execute handler
            result = await handler(task)
            
            # Update statistics
            if task.operation in ["send_sms", "send_templated_sms"]:
                self.sms_stats["total_sent"] += 1
                if result.get("success", True):
                    self.sms_stats["successful_sends"] += 1
                else:
                    self.sms_stats["failed_sends"] += 1
                self.sms_stats["last_sent"] = datetime.utcnow().isoformat()
            
            # Calculate execution time
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=True,
                data=result,
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            # Update error statistics
            if task.operation in ["send_sms", "send_templated_sms"]:
                self.sms_stats["total_sent"] += 1
                self.sms_stats["failed_sends"] += 1
            
            self.logger.error(
                f"SMS service task processing failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            return self.create_error_response(task.id, str(e))
    
    async def _send_sms(self, task: AgentTask) -> Dict[str, Any]:
        """
        Send a single SMS message.
        
        Args:
            task: Task containing SMS parameters.
            
        Returns:
            dict: SMS sending result.
        """
        to_phone = task.payload.get("to_phone")
        message = task.payload.get("message")
        from_phone = task.payload.get("from_phone", settings.SMS_FROM_PHONE)
        plaintiff_id = task.payload.get("plaintiff_id")
        bypass_compliance = task.payload.get("bypass_compliance", False)
        
        if not to_phone or not message:
            raise ValueError("Missing required fields: to_phone and message")
        
        # Normalize phone number
        normalized_phone = self._normalize_phone_number(to_phone)
        if not normalized_phone:
            raise ValueError(f"Invalid phone number format: {to_phone}")
        
        self.logger.info(
            "Sending SMS",
            to_phone=normalized_phone,
            message_length=len(message),
            from_phone=from_phone,
            plaintiff_id=plaintiff_id,
        )
        
        try:
            # Check compliance unless bypassed
            if not bypass_compliance:
                compliance_check = await self.compliance_tracker.check_compliance(
                    phone_number=normalized_phone,
                    message=message,
                    plaintiff_id=plaintiff_id,
                    rules=self.compliance_rules
                )
                
                if not compliance_check["compliant"]:
                    self.sms_stats["compliance_violations"] += 1
                    return {
                        "success": False,
                        "error": "Compliance violation",
                        "compliance_issues": compliance_check["issues"],
                        "blocked": True,
                    }
            
            # Check opt-in status
            opt_in_status = await self.compliance_tracker.check_opt_in_status(normalized_phone)
            if not opt_in_status["opted_in"] and self.compliance_rules["require_opt_in"]:
                return {
                    "success": False,
                    "error": "Recipient has not opted in to SMS communications",
                    "opt_in_required": True,
                }
            
            # Add opt-out instructions if required
            final_message = message
            if self.compliance_rules["include_opt_out_instructions"]:
                final_message = self._add_opt_out_instructions(message)
            
            # Send SMS via provider
            send_result = await self.sms_provider.send_message(
                to_phone=normalized_phone,
                message=final_message,
                from_phone=from_phone
            )
            
            if not send_result["success"]:
                return {
                    "success": False,
                    "error": send_result.get("error", "SMS send failed"),
                    "provider_error": send_result.get("provider_error"),
                }
            
            # Store communication record
            await self._store_communication_record(
                plaintiff_id=UUID(plaintiff_id) if plaintiff_id else None,
                communication_type="sms_sent",
                direction="outbound",
                content=final_message,
                to_address=normalized_phone,
                from_address=from_phone,
                metadata={
                    "message_id": send_result.get("message_id"),
                    "provider": self.sms_provider.provider_name,
                    "compliance_checked": not bypass_compliance,
                    "original_message_length": len(message),
                    "final_message_length": len(final_message),
                }
            )
            
            # Track compliance
            await self.compliance_tracker.track_outbound_message(
                phone_number=normalized_phone,
                message=final_message,
                plaintiff_id=plaintiff_id,
                message_id=send_result.get("message_id")
            )
            
            # Publish SMS sent event
            await agent_communication.publish(
                sender_id=self.agent_id,
                event_type="sms_sent",
                payload={
                    "to_phone": normalized_phone,
                    "message_length": len(final_message),
                    "plaintiff_id": plaintiff_id,
                    "message_id": send_result.get("message_id"),
                    "sent_at": datetime.utcnow().isoformat(),
                }
            )
            
            return {
                "success": True,
                "message_id": send_result.get("message_id"),
                "to_phone": normalized_phone,
                "message_length": len(final_message),
                "sent_at": datetime.utcnow().isoformat(),
                "cost": send_result.get("cost"),
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _send_templated_sms(self, task: AgentTask) -> Dict[str, Any]:
        """
        Send SMS using a template.
        
        Args:
            task: Task containing templated SMS parameters.
            
        Returns:
            dict: SMS sending result.
        """
        template_name = task.payload.get("template_name")
        to_phone = task.payload.get("to_phone")
        template_data = task.payload.get("template_data", {})
        plaintiff_id = task.payload.get("plaintiff_id")
        
        if not template_name or not to_phone:
            raise ValueError("Missing required fields: template_name and to_phone")
        
        self.logger.info(
            "Sending templated SMS",
            template_name=template_name,
            to_phone=to_phone,
            plaintiff_id=plaintiff_id,
        )
        
        # Get template
        template = await self.template_engine.get_template(template_name)
        if not template:
            raise ValueError(f"SMS template not found: {template_name}")
        
        # Render template
        rendered_message = await self.template_engine.render_template(
            template_name, template_data
        )
        
        if not rendered_message.get("success"):
            raise ValueError(f"Template rendering failed: {rendered_message.get('error')}")
        
        # Send SMS using rendered content
        send_task = AgentTask(
            agent_type=self.agent_type,
            operation="send_sms",
            payload={
                "to_phone": to_phone,
                "message": rendered_message["message"],
                "from_phone": template.get("from_phone", settings.SMS_FROM_PHONE),
                "plaintiff_id": plaintiff_id,
                "bypass_compliance": task.payload.get("bypass_compliance", False),
            }
        )
        
        result = await self._send_sms(send_task)
        result["template_name"] = template_name
        result["template_data"] = template_data
        
        return result
    
    async def _send_bulk_sms(self, task: AgentTask) -> Dict[str, Any]:
        """
        Send SMS messages to multiple recipients.
        
        Args:
            task: Task containing bulk SMS parameters.
            
        Returns:
            dict: Bulk SMS sending result.
        """
        recipients = task.payload.get("recipients", [])
        template_name = task.payload.get("template_name")
        message = task.payload.get("message")
        batch_size = task.payload.get("batch_size", 10)
        delay_between_batches = task.payload.get("delay_between_batches", 2)
        
        if not recipients:
            raise ValueError("No recipients provided")
        
        if not template_name and not message:
            raise ValueError("Either template_name or message must be provided")
        
        self.logger.info(
            "Starting bulk SMS send",
            recipient_count=len(recipients),
            template_name=template_name,
            batch_size=batch_size,
        )
        
        results = {
            "total_recipients": len(recipients),
            "successful_sends": 0,
            "failed_sends": 0,
            "compliance_blocked": 0,
            "opt_in_required": 0,
            "results": [],
            "errors": [],
        }
        
        # Process recipients in batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            # Create SMS tasks for batch
            tasks = []
            for recipient in batch:
                if isinstance(recipient, str):
                    recipient_phone = recipient
                    recipient_data = {}
                else:
                    recipient_phone = recipient.get("phone")
                    recipient_data = recipient.get("data", {})
                
                if template_name:
                    # Use template
                    sms_task = AgentTask(
                        agent_type=self.agent_type,
                        operation="send_templated_sms",
                        payload={
                            "template_name": template_name,
                            "to_phone": recipient_phone,
                            "template_data": recipient_data,
                            "plaintiff_id": recipient_data.get("plaintiff_id"),
                            "bypass_compliance": task.payload.get("bypass_compliance", False),
                        }
                    )
                else:
                    # Use direct message
                    sms_task = AgentTask(
                        agent_type=self.agent_type,
                        operation="send_sms",
                        payload={
                            "to_phone": recipient_phone,
                            "message": message,
                            "plaintiff_id": recipient_data.get("plaintiff_id"),
                            "bypass_compliance": task.payload.get("bypass_compliance", False),
                        }
                    )
                
                tasks.append(sms_task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(
                *[self._send_templated_sms(task) if template_name else self._send_sms(task) 
                  for task in tasks],
                return_exceptions=True
            )
            
            # Process batch results
            for result in batch_results:
                if isinstance(result, Exception):
                    results["failed_sends"] += 1
                    results["errors"].append(str(result))
                elif result.get("success"):
                    results["successful_sends"] += 1
                    results["results"].append(result)
                else:
                    results["failed_sends"] += 1
                    error = result.get("error", "Unknown error")
                    results["errors"].append(error)
                    
                    # Track specific failure types
                    if result.get("blocked"):
                        results["compliance_blocked"] += 1
                    elif result.get("opt_in_required"):
                        results["opt_in_required"] += 1
            
            # Delay between batches
            if i + batch_size < len(recipients):
                await asyncio.sleep(delay_between_batches)
        
        # Publish bulk SMS completion event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="bulk_sms_completed",
            payload={
                "total_recipients": results["total_recipients"],
                "successful_sends": results["successful_sends"],
                "failed_sends": results["failed_sends"],
                "compliance_blocked": results["compliance_blocked"],
                "completion_time": datetime.utcnow().isoformat(),
            }
        )
        
        return results
    
    async def _handle_inbound_sms(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle incoming SMS message.
        
        Args:
            task: Task containing inbound SMS data.
            
        Returns:
            dict: Inbound SMS handling result.
        """
        from_phone = task.payload.get("from_phone")
        message = task.payload.get("message")
        to_phone = task.payload.get("to_phone")
        message_id = task.payload.get("message_id")
        
        if not from_phone or not message:
            raise ValueError("Missing required fields: from_phone and message")
        
        # Normalize phone number
        normalized_phone = self._normalize_phone_number(from_phone)
        
        self.logger.info(
            "Handling inbound SMS",
            from_phone=normalized_phone,
            message_length=len(message),
            message_preview=message[:50] + "..." if len(message) > 50 else message,
        )
        
        self.sms_stats["inbound_messages"] += 1
        
        # Check for opt-out keywords
        if self._is_opt_out_message(message):
            opt_out_result = await self._handle_opt_out_request(normalized_phone, message)
            return {
                "message_type": "opt_out",
                "handled": True,
                "opt_out_result": opt_out_result,
            }
        
        # Check for opt-in keywords
        if self._is_opt_in_message(message):
            opt_in_result = await self._handle_opt_in_request(normalized_phone, message)
            return {
                "message_type": "opt_in",
                "handled": True,
                "opt_in_result": opt_in_result,
            }
        
        # Find associated plaintiff
        plaintiff = await self._find_plaintiff_by_phone(normalized_phone)
        
        # Store communication record
        await self._store_communication_record(
            plaintiff_id=plaintiff.id if plaintiff else None,
            communication_type="sms_received",
            direction="inbound",
            content=message,
            from_address=normalized_phone,
            to_address=to_phone,
            metadata={
                "message_id": message_id,
                "provider": self.sms_provider.provider_name,
                "auto_response_sent": False,
            }
        )
        
        # Generate auto-response if configured
        auto_response = await self._generate_auto_response(message, plaintiff)
        
        response_result = None
        if auto_response:
            # Send auto-response
            response_task = AgentTask(
                agent_type=self.agent_type,
                operation="send_sms",
                payload={
                    "to_phone": normalized_phone,
                    "message": auto_response,
                    "plaintiff_id": str(plaintiff.id) if plaintiff else None,
                    "bypass_compliance": True,  # Auto-responses can bypass some checks
                }
            )
            response_result = await self._send_sms(response_task)
        
        # Publish inbound SMS event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="sms_received",
            payload={
                "from_phone": normalized_phone,
                "message": message,
                "plaintiff_id": str(plaintiff.id) if plaintiff else None,
                "auto_response_sent": response_result is not None,
                "received_at": datetime.utcnow().isoformat(),
            }
        )
        
        return {
            "message_type": "general",
            "from_phone": normalized_phone,
            "plaintiff_found": plaintiff is not None,
            "plaintiff_id": str(plaintiff.id) if plaintiff else None,
            "auto_response_sent": response_result is not None,
            "auto_response_result": response_result,
            "handled": True,
        }
    
    async def _handle_opt_out(self, task: AgentTask) -> Dict[str, Any]:
        """Handle opt-out request."""
        phone_number = task.payload.get("phone_number")
        reason = task.payload.get("reason", "User request")
        
        if not phone_number:
            raise ValueError("Missing phone_number")
        
        normalized_phone = self._normalize_phone_number(phone_number)
        result = await self.compliance_tracker.handle_opt_out(normalized_phone, reason)
        
        if result["success"]:
            self.sms_stats["opt_outs"] += 1
        
        return result
    
    async def _handle_opt_in(self, task: AgentTask) -> Dict[str, Any]:
        """Handle opt-in request."""
        phone_number = task.payload.get("phone_number")
        consent_method = task.payload.get("consent_method", "SMS reply")
        
        if not phone_number:
            raise ValueError("Missing phone_number")
        
        normalized_phone = self._normalize_phone_number(phone_number)
        result = await self.compliance_tracker.handle_opt_in(normalized_phone, consent_method)
        
        if result["success"]:
            self.sms_stats["opt_ins"] += 1
        
        return result
    
    async def _check_opt_in_status(self, task: AgentTask) -> Dict[str, Any]:
        """Check opt-in status for phone number."""
        phone_number = task.payload.get("phone_number")
        
        if not phone_number:
            raise ValueError("Missing phone_number")
        
        normalized_phone = self._normalize_phone_number(phone_number)
        return await self.compliance_tracker.check_opt_in_status(normalized_phone)
    
    async def _generate_sms_content(self, task: AgentTask) -> Dict[str, Any]:
        """Generate SMS content using AI."""
        purpose = task.payload.get("purpose")
        context = task.payload.get("context", {})
        tone = task.payload.get("tone", "professional")
        max_length = task.payload.get("max_length", 160)
        
        if not purpose:
            raise ValueError("Missing purpose for SMS generation")
        
        result = await self.template_engine.generate_sms_content(
            purpose, context, tone, max_length
        )
        
        return result
    
    def _normalize_phone_number(self, phone: str) -> Optional[str]:
        """Normalize phone number to E.164 format."""
        if not phone:
            return None
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if len(digits) == 10:
            # US number without country code
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith('1'):
            # US number with country code
            return f"+{digits}"
        elif len(digits) > 11:
            # International number
            return f"+{digits}"
        else:
            # Invalid format
            return None
    
    def _add_opt_out_instructions(self, message: str) -> str:
        """Add opt-out instructions to SMS message."""
        opt_out_text = " Reply STOP to opt out."
        
        # Check if message already has opt-out instructions
        if "STOP" in message.upper() or "opt out" in message.lower():
            return message
        
        # Add opt-out instructions, truncating message if necessary
        max_length = self.compliance_rules["max_message_length"] - len(opt_out_text)
        
        if len(message) > max_length:
            message = message[:max_length-3] + "..."
        
        return message + opt_out_text
    
    def _is_opt_out_message(self, message: str) -> bool:
        """Check if message is an opt-out request."""
        opt_out_keywords = [
            "STOP", "QUIT", "CANCEL", "UNSUBSCRIBE", "REMOVE", "OPTOUT", "OPT OUT"
        ]
        
        message_upper = message.upper().strip()
        return any(keyword in message_upper for keyword in opt_out_keywords)
    
    def _is_opt_in_message(self, message: str) -> bool:
        """Check if message is an opt-in request."""
        opt_in_keywords = [
            "START", "YES", "OPTIN", "OPT IN", "SUBSCRIBE", "JOIN"
        ]
        
        message_upper = message.upper().strip()
        return any(keyword in message_upper for keyword in opt_in_keywords)
    
    async def _handle_opt_out_request(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Handle opt-out request from SMS."""
        result = await self.compliance_tracker.handle_opt_out(
            phone_number, f"SMS reply: {message}"
        )
        
        if result["success"]:
            # Send confirmation message
            confirmation_message = "You have been unsubscribed from SMS messages. You will not receive any more messages from us."
            
            try:
                await self.sms_provider.send_message(
                    to_phone=phone_number,
                    message=confirmation_message,
                    from_phone=settings.SMS_FROM_PHONE
                )
            except Exception as e:
                self.logger.error(f"Failed to send opt-out confirmation: {e}")
        
        return result
    
    async def _handle_opt_in_request(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Handle opt-in request from SMS."""
        result = await self.compliance_tracker.handle_opt_in(
            phone_number, f"SMS reply: {message}"
        )
        
        if result["success"]:
            # Send welcome message
            welcome_message = "Welcome! You have successfully opted in to receive SMS updates. Reply STOP at any time to unsubscribe."
            
            try:
                await self.sms_provider.send_message(
                    to_phone=phone_number,
                    message=welcome_message,
                    from_phone=settings.SMS_FROM_PHONE
                )
            except Exception as e:
                self.logger.error(f"Failed to send opt-in welcome message: {e}")
        
        return result
    
    async def _find_plaintiff_by_phone(self, phone_number: str) -> Optional:
        """Find plaintiff by phone number."""
        async with get_database_session() as session:
            stmt = select(Plaintiff).where(Plaintiff.phone == phone_number)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def _generate_auto_response(
        self,
        inbound_message: str,
        plaintiff: Optional = None
    ) -> Optional[str]:
        """Generate appropriate auto-response for inbound message."""
        # Simple auto-response logic
        # In a real implementation, this would use AI to generate contextual responses
        
        if not plaintiff:
            return "Thank you for your message. We'll get back to you soon. If this is urgent, please call our office."
        
        # Check if message seems like a question
        question_indicators = ["?", "how", "what", "when", "where", "why", "can you", "could you"]
        
        if any(indicator in inbound_message.lower() for indicator in question_indicators):
            return f"Hi {plaintiff.first_name}, thanks for your question. A team member will respond shortly. For urgent matters, please call us."
        
        return f"Hi {plaintiff.first_name}, we received your message and will respond soon. Thank you!"
    
    async def _store_communication_record(
        self,
        plaintiff_id: Optional[UUID],
        communication_type: str,
        direction: str,
        content: str,
        to_address: Optional[str] = None,
        from_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store communication record in database."""
        async with get_database_session() as session:
            communication = Communication(
                plaintiff_id=plaintiff_id,
                communication_type=communication_type,
                direction=direction,
                content=content,
                to_address=to_address,
                from_address=from_address,
                metadata=metadata or {},
                status="completed",
            )
            
            session.add(communication)
            await session.commit()
    
    def get_sms_statistics(self) -> Dict[str, Any]:
        """Get current SMS statistics."""
        total = self.sms_stats["total_sent"]
        
        return {
            **self.sms_stats,
            "success_rate": (
                self.sms_stats["successful_sends"] / total * 100
                if total > 0 else 0
            ),
            "compliance_violation_rate": (
                self.sms_stats["compliance_violations"] / total * 100
                if total > 0 else 0
            ),
            "opt_out_rate": (
                self.sms_stats["opt_outs"] / self.sms_stats["successful_sends"] * 100
                if self.sms_stats["successful_sends"] > 0 else 0
            ),
        }
"""Email Service Agent implementation."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...config.settings import get_settings
from ...models.database import Plaintiff, LawFirm, Communication
from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger
from ..base.agent import BaseAgent, AgentTask, AgentResponse
from ..base.communication import agent_communication
from .templates import EmailTemplateEngine
from .tracking import EmailTracker

logger = get_logger(__name__)
settings = get_settings()


class EmailServiceAgent(BaseAgent):
    """
    Email Service Agent for automated email communication.
    
    Handles email sending, template management, tracking,
    and automated email workflows.
    """
    
    def __init__(self, config):
        """Initialize the Email Service Agent."""
        super().__init__(config)
        
        # Initialize email components
        self.ai_client = OpenAIClient()
        self.template_engine = EmailTemplateEngine(self.ai_client)
        self.email_tracker = EmailTracker()
        
        # SMTP configuration
        self.smtp_config = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "username": settings.SMTP_USERNAME,
            "password": settings.SMTP_PASSWORD,
            "use_tls": settings.SMTP_USE_TLS,
            "use_ssl": settings.SMTP_USE_SSL,
        }
        
        # Operation handlers
        self._handlers = {
            "send_email": self._send_email,
            "send_templated_email": self._send_templated_email,
            "send_bulk_emails": self._send_bulk_emails,
            "create_template": self._create_template,
            "update_template": self._update_template,
            "get_template": self._get_template,
            "list_templates": self._list_templates,
            "schedule_email": self._schedule_email,
            "process_scheduled_emails": self._process_scheduled_emails,
            "track_email_opens": self._track_email_opens,
            "track_email_clicks": self._track_email_clicks,
            "generate_email_content": self._generate_email_content,
            "validate_email_list": self._validate_email_list,
            "send_automated_workflow": self._send_automated_workflow,
        }
        
        # Email statistics
        self.email_stats = {
            "total_sent": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "bounced_emails": 0,
            "opened_emails": 0,
            "clicked_emails": 0,
            "unsubscribed": 0,
            "last_sent": None,
        }
        
        # Email queue for batch processing
        self.email_queue = asyncio.Queue()
        self.processing_queue = False
        
        self.logger.info("Email Service Agent initialized")
    
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
            if task.operation in ["send_email", "send_templated_email"]:
                self.email_stats["total_sent"] += 1
                if result.get("success", True):
                    self.email_stats["successful_sends"] += 1
                else:
                    self.email_stats["failed_sends"] += 1
                self.email_stats["last_sent"] = datetime.utcnow().isoformat()
            
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
            if task.operation in ["send_email", "send_templated_email"]:
                self.email_stats["total_sent"] += 1
                self.email_stats["failed_sends"] += 1
            
            self.logger.error(
                f"Email service task processing failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            return self.create_error_response(task.id, str(e))
    
    async def _send_email(self, task: AgentTask) -> Dict[str, Any]:
        """
        Send a single email.
        
        Args:
            task: Task containing email parameters.
            
        Returns:
            dict: Email sending result.
        """
        to_email = task.payload.get("to_email")
        subject = task.payload.get("subject")
        body = task.payload.get("body")
        body_html = task.payload.get("body_html")
        from_email = task.payload.get("from_email", settings.DEFAULT_FROM_EMAIL)
        from_name = task.payload.get("from_name", settings.DEFAULT_FROM_NAME)
        cc_emails = task.payload.get("cc_emails", [])
        bcc_emails = task.payload.get("bcc_emails", [])
        attachments = task.payload.get("attachments", [])
        tracking_enabled = task.payload.get("tracking_enabled", True)
        plaintiff_id = task.payload.get("plaintiff_id")
        
        if not to_email or not subject:
            raise ValueError("Missing required fields: to_email and subject")
        
        self.logger.info(
            "Sending email",
            to_email=to_email,
            subject=subject,
            from_email=from_email,
            tracking_enabled=tracking_enabled,
        )
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add tracking pixel if enabled
            if tracking_enabled:
                tracking_id = self.email_tracker.generate_tracking_id()
                body_html = self.email_tracker.add_tracking_pixel(body_html or body, tracking_id)
                
                # Store tracking info
                await self.email_tracker.store_tracking_info(
                    tracking_id=tracking_id,
                    to_email=to_email,
                    subject=subject,
                    plaintiff_id=plaintiff_id,
                )
            
            # Add body parts
            if body:
                text_part = MIMEText(body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if body_html:
                html_part = MIMEText(body_html, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment_path)}'
                        )
                        msg.attach(attachment)
            
            # Send email
            all_recipients = [to_email] + cc_emails + bcc_emails
            await self._send_smtp_email(msg, all_recipients)
            
            # Store communication record
            await self._store_communication_record(
                plaintiff_id=UUID(plaintiff_id) if plaintiff_id else None,
                communication_type="email_sent",
                direction="outbound",
                content=body or body_html,
                subject=subject,
                to_address=to_email,
                from_address=from_email,
                metadata={
                    "tracking_enabled": tracking_enabled,
                    "tracking_id": tracking_id if tracking_enabled else None,
                    "cc_emails": cc_emails,
                    "bcc_emails": bcc_emails,
                    "attachments_count": len(attachments),
                }
            )
            
            # Publish email sent event
            await agent_communication.publish(
                sender_id=self.agent_id,
                event_type="email_sent",
                payload={
                    "to_email": to_email,
                    "subject": subject,
                    "plaintiff_id": plaintiff_id,
                    "tracking_id": tracking_id if tracking_enabled else None,
                    "sent_at": datetime.utcnow().isoformat(),
                }
            )
            
            return {
                "success": True,
                "message_id": msg.get('Message-ID'),
                "tracking_id": tracking_id if tracking_enabled else None,
                "sent_at": datetime.utcnow().isoformat(),
                "recipients": all_recipients,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _send_templated_email(self, task: AgentTask) -> Dict[str, Any]:
        """
        Send email using a template.
        
        Args:
            task: Task containing templated email parameters.
            
        Returns:
            dict: Email sending result.
        """
        template_name = task.payload.get("template_name")
        to_email = task.payload.get("to_email")
        template_data = task.payload.get("template_data", {})
        plaintiff_id = task.payload.get("plaintiff_id")
        
        if not template_name or not to_email:
            raise ValueError("Missing required fields: template_name and to_email")
        
        self.logger.info(
            "Sending templated email",
            template_name=template_name,
            to_email=to_email,
            plaintiff_id=plaintiff_id,
        )
        
        # Get template
        template = await self.template_engine.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Render template
        rendered_email = await self.template_engine.render_template(
            template_name, template_data
        )
        
        # Send email using rendered content
        send_task = AgentTask(
            agent_type=self.agent_type,
            operation="send_email",
            payload={
                "to_email": to_email,
                "subject": rendered_email["subject"],
                "body": rendered_email.get("body_text"),
                "body_html": rendered_email.get("body_html"),
                "from_email": template.get("from_email", settings.DEFAULT_FROM_EMAIL),
                "from_name": template.get("from_name", settings.DEFAULT_FROM_NAME),
                "tracking_enabled": task.payload.get("tracking_enabled", True),
                "plaintiff_id": plaintiff_id,
            }
        )
        
        result = await self._send_email(send_task)
        result["template_name"] = template_name
        result["template_data"] = template_data
        
        return result
    
    async def _send_bulk_emails(self, task: AgentTask) -> Dict[str, Any]:
        """
        Send emails to multiple recipients.
        
        Args:
            task: Task containing bulk email parameters.
            
        Returns:
            dict: Bulk email sending result.
        """
        recipients = task.payload.get("recipients", [])
        template_name = task.payload.get("template_name")
        subject = task.payload.get("subject")
        body = task.payload.get("body")
        body_html = task.payload.get("body_html")
        batch_size = task.payload.get("batch_size", 10)
        delay_between_batches = task.payload.get("delay_between_batches", 5)
        
        if not recipients:
            raise ValueError("No recipients provided")
        
        if not template_name and not (subject and (body or body_html)):
            raise ValueError("Either template_name or subject+body must be provided")
        
        self.logger.info(
            "Starting bulk email send",
            recipient_count=len(recipients),
            template_name=template_name,
            batch_size=batch_size,
        )
        
        results = {
            "total_recipients": len(recipients),
            "successful_sends": 0,
            "failed_sends": 0,
            "results": [],
            "errors": [],
        }
        
        # Process recipients in batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            # Create email tasks for batch
            tasks = []
            for recipient in batch:
                if isinstance(recipient, str):
                    recipient_email = recipient
                    recipient_data = {}
                else:
                    recipient_email = recipient.get("email")
                    recipient_data = recipient.get("data", {})
                
                if template_name:
                    # Use template
                    email_task = AgentTask(
                        agent_type=self.agent_type,
                        operation="send_templated_email",
                        payload={
                            "template_name": template_name,
                            "to_email": recipient_email,
                            "template_data": recipient_data,
                            "plaintiff_id": recipient_data.get("plaintiff_id"),
                            "tracking_enabled": task.payload.get("tracking_enabled", True),
                        }
                    )
                else:
                    # Use direct content
                    email_task = AgentTask(
                        agent_type=self.agent_type,
                        operation="send_email",
                        payload={
                            "to_email": recipient_email,
                            "subject": subject,
                            "body": body,
                            "body_html": body_html,
                            "plaintiff_id": recipient_data.get("plaintiff_id"),
                            "tracking_enabled": task.payload.get("tracking_enabled", True),
                        }
                    )
                
                tasks.append(email_task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(
                *[self._send_templated_email(task) if template_name else self._send_email(task) 
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
                    results["errors"].append(result.get("error", "Unknown error"))
            
            # Delay between batches
            if i + batch_size < len(recipients):
                await asyncio.sleep(delay_between_batches)
        
        # Publish bulk email completion event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="bulk_email_completed",
            payload={
                "total_recipients": results["total_recipients"],
                "successful_sends": results["successful_sends"],
                "failed_sends": results["failed_sends"],
                "completion_time": datetime.utcnow().isoformat(),
            }
        )
        
        return results
    
    async def _create_template(self, task: AgentTask) -> Dict[str, Any]:
        """Create a new email template."""
        template_name = task.payload.get("template_name")
        template_data = task.payload.get("template_data")
        
        if not template_name or not template_data:
            raise ValueError("Missing template_name or template_data")
        
        result = await self.template_engine.create_template(template_name, template_data)
        return result
    
    async def _update_template(self, task: AgentTask) -> Dict[str, Any]:
        """Update an existing email template."""
        template_name = task.payload.get("template_name")
        template_data = task.payload.get("template_data")
        
        if not template_name or not template_data:
            raise ValueError("Missing template_name or template_data")
        
        result = await self.template_engine.update_template(template_name, template_data)
        return result
    
    async def _get_template(self, task: AgentTask) -> Dict[str, Any]:
        """Get an email template."""
        template_name = task.payload.get("template_name")
        
        if not template_name:
            raise ValueError("Missing template_name")
        
        template = await self.template_engine.get_template(template_name)
        return {"template": template} if template else {"error": "Template not found"}
    
    async def _list_templates(self, task: AgentTask) -> Dict[str, Any]:
        """List all email templates."""
        templates = await self.template_engine.list_templates()
        return {"templates": templates}
    
    async def _generate_email_content(self, task: AgentTask) -> Dict[str, Any]:
        """Generate email content using AI."""
        purpose = task.payload.get("purpose")
        context = task.payload.get("context", {})
        tone = task.payload.get("tone", "professional")
        length = task.payload.get("length", "medium")
        
        if not purpose:
            raise ValueError("Missing purpose for email generation")
        
        result = await self.template_engine.generate_email_content(
            purpose, context, tone, length
        )
        
        return result
    
    async def _send_smtp_email(
        self,
        message: MIMEMultipart,
        recipients: List[str]
    ) -> None:
        """Send email via SMTP."""
        try:
            if self.smtp_config["use_ssl"]:
                server = smtplib.SMTP_SSL(
                    self.smtp_config["host"],
                    self.smtp_config["port"]
                )
            else:
                server = smtplib.SMTP(
                    self.smtp_config["host"],
                    self.smtp_config["port"]
                )
                
                if self.smtp_config["use_tls"]:
                    server.starttls()
            
            if self.smtp_config["username"] and self.smtp_config["password"]:
                server.login(
                    self.smtp_config["username"],
                    self.smtp_config["password"]
                )
            
            server.send_message(message, to_addrs=recipients)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"SMTP send failed: {e}")
            raise
    
    async def _store_communication_record(
        self,
        plaintiff_id: Optional[UUID],
        communication_type: str,
        direction: str,
        content: str,
        subject: Optional[str] = None,
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
                subject=subject,
                to_address=to_address,
                from_address=from_address,
                metadata=metadata or {},
                status="sent",
            )
            
            session.add(communication)
            await session.commit()
    
    def get_email_statistics(self) -> Dict[str, Any]:
        """Get current email statistics."""
        total = self.email_stats["total_sent"]
        
        return {
            **self.email_stats,
            "success_rate": (
                self.email_stats["successful_sends"] / total * 100
                if total > 0 else 0
            ),
            "open_rate": (
                self.email_stats["opened_emails"] / self.email_stats["successful_sends"] * 100
                if self.email_stats["successful_sends"] > 0 else 0
            ),
            "click_rate": (
                self.email_stats["clicked_emails"] / self.email_stats["opened_emails"] * 100
                if self.email_stats["opened_emails"] > 0 else 0
            ),
        }
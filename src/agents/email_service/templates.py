"""Email template management and rendering system."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateError

from ...config.settings import get_settings
from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmailTemplateEngine:
    """
    Email template management and rendering engine.
    
    Handles template storage, rendering with Jinja2,
    and AI-powered template generation.
    """
    
    def __init__(self, ai_client: Optional[OpenAIClient] = None):
        """
        Initialize email template engine.
        
        Args:
            ai_client: OpenAI client for AI-powered template generation.
        """
        self.ai_client = ai_client or OpenAIClient()
        
        # Setup template directory
        self.templates_dir = Path(settings.EMAIL_TEMPLATES_PATH)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom filters
        self.jinja_env.filters['currency'] = self._currency_filter
        self.jinja_env.filters['date_format'] = self._date_format_filter
        self.jinja_env.filters['phone_format'] = self._phone_format_filter
        
        # Built-in templates
        self.builtin_templates = {
            "welcome_plaintiff": {
                "name": "Welcome Plaintiff",
                "description": "Welcome email for new plaintiffs",
                "subject": "Welcome to {{ company_name }} - Your Case: {{ case_number }}",
                "body_text": self._get_welcome_plaintiff_text(),
                "body_html": self._get_welcome_plaintiff_html(),
                "variables": [
                    "plaintiff_name", "case_number", "company_name", 
                    "lawyer_name", "case_type", "next_steps"
                ],
            },
            "document_request": {
                "name": "Document Request",
                "description": "Request documents from plaintiff",
                "subject": "Document Request for Case {{ case_number }}",
                "body_text": self._get_document_request_text(),
                "body_html": self._get_document_request_html(),
                "variables": [
                    "plaintiff_name", "case_number", "documents_needed",
                    "deadline", "upload_link", "contact_info"
                ],
            },
            "case_update": {
                "name": "Case Update",
                "description": "General case status update",
                "subject": "Case Update: {{ case_number }} - {{ update_type }}",
                "body_text": self._get_case_update_text(),
                "body_html": self._get_case_update_html(),
                "variables": [
                    "plaintiff_name", "case_number", "update_type",
                    "update_details", "next_steps", "contact_info"
                ],
            },
            "funding_approval": {
                "name": "Funding Approval",
                "description": "Funding approval notification",
                "subject": "Great News! Your Funding Has Been Approved - {{ case_number }}",
                "body_text": self._get_funding_approval_text(),
                "body_html": self._get_funding_approval_html(),
                "variables": [
                    "plaintiff_name", "case_number", "approved_amount",
                    "disbursement_timeline", "terms_link", "contact_info"
                ],
            },
            "payment_reminder": {
                "name": "Payment Reminder",
                "description": "Payment reminder for outstanding amounts",
                "subject": "Payment Reminder - Case {{ case_number }}",
                "body_text": self._get_payment_reminder_text(),
                "body_html": self._get_payment_reminder_html(),
                "variables": [
                    "plaintiff_name", "case_number", "outstanding_amount",
                    "due_date", "payment_link", "contact_info"
                ],
            },
        }
        
        # Ensure built-in templates are saved
        # Note: In production, this should be done during application startup
        # asyncio.create_task(self._initialize_builtin_templates())
    
    async def create_template(
        self,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new email template.
        
        Args:
            template_name: Name of the template.
            template_data: Template configuration and content.
            
        Returns:
            dict: Creation result.
        """
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            
            if template_file.exists():
                return {
                    "success": False,
                    "error": f"Template '{template_name}' already exists",
                }
            
            # Validate template data
            validation_result = self._validate_template_data(template_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Template validation failed: {validation_result['errors']}",
                }
            
            # Add metadata
            template_data["created_at"] = datetime.utcnow().isoformat()
            template_data["updated_at"] = datetime.utcnow().isoformat()
            template_data["version"] = "1.0"
            
            # Save template
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Email template created: {template_name}")
            
            return {
                "success": True,
                "template_name": template_name,
                "template_path": str(template_file),
            }
            
        except Exception as e:
            logger.error(f"Failed to create email template {template_name}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def update_template(
        self,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing email template."""
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            
            if not template_file.exists():
                return {
                    "success": False,
                    "error": f"Template '{template_name}' not found",
                }
            
            # Load existing template
            with open(template_file, 'r', encoding='utf-8') as f:
                existing_template = json.load(f)
            
            # Merge updates
            existing_template.update(template_data)
            existing_template["updated_at"] = datetime.utcnow().isoformat()
            
            # Validate updated template
            validation_result = self._validate_template_data(existing_template)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Template validation failed: {validation_result['errors']}",
                }
            
            # Save updated template
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(existing_template, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Email template updated: {template_name}")
            
            return {
                "success": True,
                "template_name": template_name,
                "updated_at": existing_template["updated_at"],
            }
            
        except Exception as e:
            logger.error(f"Failed to update email template {template_name}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name."""
        try:
            # Check built-in templates first
            if template_name in self.builtin_templates:
                return self.builtin_templates[template_name]
            
            # Check saved templates
            template_file = self.templates_dir / f"{template_name}.json"
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get email template {template_name}: {e}")
            return None
    
    async def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates."""
        templates = []
        
        # Add built-in templates
        for name, template in self.builtin_templates.items():
            templates.append({
                "name": name,
                "display_name": template["name"],
                "description": template["description"],
                "type": "builtin",
                "variables": template.get("variables", []),
            })
        
        # Add saved templates
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                templates.append({
                    "name": template_file.stem,
                    "display_name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", ""),
                    "type": "custom",
                    "variables": template_data.get("variables", []),
                    "created_at": template_data.get("created_at"),
                    "updated_at": template_data.get("updated_at"),
                })
                
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")
        
        return templates
    
    async def render_template(
        self,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Render a template with provided data.
        
        Args:
            template_name: Name of the template to render.
            template_data: Data to use for rendering.
            
        Returns:
            dict: Rendered template content.
        """
        try:
            template = await self.get_template(template_name)
            if not template:
                raise ValueError(f"Template '{template_name}' not found")
            
            # Prepare template context
            context = {
                **template_data,
                "current_date": datetime.now().strftime("%B %d, %Y"),
                "current_year": datetime.now().year,
                "company_name": settings.COMPANY_NAME,
                "company_email": settings.COMPANY_EMAIL,
                "company_phone": settings.COMPANY_PHONE,
                "company_address": settings.COMPANY_ADDRESS,
            }
            
            # Render subject
            subject_template = Template(template["subject"])
            rendered_subject = subject_template.render(**context)
            
            # Render text body
            rendered_text = None
            if template.get("body_text"):
                text_template = Template(template["body_text"])
                rendered_text = text_template.render(**context)
            
            # Render HTML body
            rendered_html = None
            if template.get("body_html"):
                html_template = Template(template["body_html"])
                rendered_html = html_template.render(**context)
            
            return {
                "success": True,
                "template_name": template_name,
                "subject": rendered_subject,
                "body_text": rendered_text,
                "body_html": rendered_html,
                "context_used": context,
            }
            
        except TemplateError as e:
            logger.error(f"Template rendering error for {template_name}: {e}")
            return {
                "success": False,
                "error": f"Template rendering failed: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def generate_email_content(
        self,
        purpose: str,
        context: Dict[str, Any],
        tone: str = "professional",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate email content using AI.
        
        Args:
            purpose: Purpose of the email.
            context: Context information for the email.
            tone: Tone of the email (professional, friendly, formal).
            length: Length of the email (short, medium, long).
            
        Returns:
            dict: Generated email content.
        """
        try:
            prompt = f"""
            Generate an email for the following purpose: {purpose}
            
            Context information:
            {json.dumps(context, indent=2)}
            
            Requirements:
            - Tone: {tone}
            - Length: {length}
            - Include appropriate subject line
            - Make it suitable for a legal services/pre-settlement funding company
            - Be empathetic and professional
            - Include clear next steps if applicable
            
            Provide the response in JSON format:
            {{
                "subject": "Email subject line",
                "body": "Email body content",
                "suggested_variables": ["list", "of", "template", "variables"]
            }}
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            # Parse AI response
            try:
                generated_content = json.loads(response.strip())
                
                return {
                    "success": True,
                    "generated_content": generated_content,
                    "purpose": purpose,
                    "tone": tone,
                    "length": length,
                }
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw content
                return {
                    "success": True,
                    "generated_content": {
                        "subject": f"Regarding: {purpose}",
                        "body": response.strip(),
                        "suggested_variables": [],
                    },
                    "purpose": purpose,
                    "tone": tone,
                    "length": length,
                    "note": "Raw AI response (JSON parsing failed)",
                }
                
        except Exception as e:
            logger.error(f"Failed to generate email content: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def _validate_template_data(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template data structure."""
        errors = []
        
        # Required fields
        required_fields = ["name", "subject"]
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Must have at least one body
        if not template_data.get("body_text") and not template_data.get("body_html"):
            errors.append("Template must have either body_text or body_html")
        
        # Validate Jinja2 syntax
        if template_data.get("subject"):
            try:
                Template(template_data["subject"])
            except TemplateError as e:
                errors.append(f"Invalid Jinja2 syntax in subject: {e}")
        
        if template_data.get("body_text"):
            try:
                Template(template_data["body_text"])
            except TemplateError as e:
                errors.append(f"Invalid Jinja2 syntax in body_text: {e}")
        
        if template_data.get("body_html"):
            try:
                Template(template_data["body_html"])
            except TemplateError as e:
                errors.append(f"Invalid Jinja2 syntax in body_html: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
    
    # Custom Jinja2 filters
    def _currency_filter(self, value: Any) -> str:
        """Format value as currency."""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _date_format_filter(self, value: Any, format_string: str = "%B %d, %Y") -> str:
        """Format date value."""
        try:
            if isinstance(value, str):
                date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, datetime):
                date_obj = value
            else:
                return str(value)
            
            return date_obj.strftime(format_string)
        except (ValueError, TypeError):
            return str(value)
    
    def _phone_format_filter(self, value: Any) -> str:
        """Format phone number."""
        try:
            # Remove non-digits
            digits = re.sub(r'\D', '', str(value))
            
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            else:
                return str(value)
        except:
            return str(value)
    
    # Built-in template content
    def _get_welcome_plaintiff_text(self) -> str:
        return """
Dear {{ plaintiff_name }},

Welcome to {{ company_name }}! We're here to help you navigate your {{ case_type }} case and provide the financial support you need during this challenging time.

Your case number is: {{ case_number }}

Your assigned attorney is {{ lawyer_name }}, who will be your primary point of contact throughout the process.

Next Steps:
{{ next_steps }}

If you have any questions or concerns, please don't hesitate to reach out to us at {{ company_phone }} or {{ company_email }}.

We're committed to providing you with excellent service and support.

Best regards,
The {{ company_name }} Team
        """.strip()
    
    def _get_welcome_plaintiff_html(self) -> str:
        return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c5aa0;">Welcome to {{ company_name }}!</h2>
        
        <p>Dear {{ plaintiff_name }},</p>
        
        <p>We're here to help you navigate your {{ case_type }} case and provide the financial support you need during this challenging time.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #2c5aa0; margin: 20px 0;">
            <strong>Your case number:</strong> {{ case_number }}<br>
            <strong>Your assigned attorney:</strong> {{ lawyer_name }}
        </div>
        
        <h3 style="color: #2c5aa0;">Next Steps:</h3>
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px;">
            {{ next_steps }}
        </div>
        
        <p>If you have any questions or concerns, please don't hesitate to reach out to us:</p>
        <ul>
            <li>Phone: {{ company_phone }}</li>
            <li>Email: <a href="mailto:{{ company_email }}">{{ company_email }}</a></li>
        </ul>
        
        <p>We're committed to providing you with excellent service and support.</p>
        
        <p>Best regards,<br>
        <strong>The {{ company_name }} Team</strong></p>
    </div>
</body>
</html>
        """.strip()
    
    def _get_document_request_text(self) -> str:
        return """
Dear {{ plaintiff_name }},

We need some additional documents to move forward with your case ({{ case_number }}).

Required Documents:
{{ documents_needed }}

Please submit these documents by {{ deadline }} using our secure upload portal: {{ upload_link }}

If you have any questions about the required documents or need assistance with the upload process, please contact us at {{ contact_info }}.

Thank you for your prompt attention to this matter.

Best regards,
The Case Management Team
        """.strip()
    
    def _get_document_request_html(self) -> str:
        return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c5aa0;">Document Request</h2>
        
        <p>Dear {{ plaintiff_name }},</p>
        
        <p>We need some additional documents to move forward with your case <strong>{{ case_number }}</strong>.</p>
        
        <h3 style="color: #2c5aa0;">Required Documents:</h3>
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
            {{ documents_needed }}
        </div>
        
        <p><strong>Deadline:</strong> {{ deadline }}</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ upload_link }}" style="background-color: #2c5aa0; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Upload Documents</a>
        </div>
        
        <p>If you have any questions about the required documents or need assistance with the upload process, please contact us at {{ contact_info }}.</p>
        
        <p>Thank you for your prompt attention to this matter.</p>
        
        <p>Best regards,<br>
        <strong>The Case Management Team</strong></p>
    </div>
</body>
</html>
        """.strip()
    
    def _get_case_update_text(self) -> str:
        return """
Dear {{ plaintiff_name }},

We have an important update regarding your case {{ case_number }}.

Update: {{ update_type }}

{{ update_details }}

Next Steps:
{{ next_steps }}

If you have any questions about this update, please don't hesitate to contact us at {{ contact_info }}.

Best regards,
Your Case Management Team
        """.strip()
    
    def _get_case_update_html(self) -> str:
        return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c5aa0;">Case Update</h2>
        
        <p>Dear {{ plaintiff_name }},</p>
        
        <p>We have an important update regarding your case <strong>{{ case_number }}</strong>.</p>
        
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #155724;">{{ update_type }}</h3>
            <p style="margin-bottom: 0;">{{ update_details }}</p>
        </div>
        
        <h3 style="color: #2c5aa0;">Next Steps:</h3>
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px;">
            {{ next_steps }}
        </div>
        
        <p>If you have any questions about this update, please don't hesitate to contact us at {{ contact_info }}.</p>
        
        <p>Best regards,<br>
        <strong>Your Case Management Team</strong></p>
    </div>
</body>
</html>
        """.strip()
    
    def _get_funding_approval_text(self) -> str:
        return """
Dear {{ plaintiff_name }},

Congratulations! Your funding request for case {{ case_number }} has been APPROVED!

Approved Amount: {{ approved_amount | currency }}
Disbursement Timeline: {{ disbursement_timeline }}

You can review the complete terms and conditions at: {{ terms_link }}

We'll begin processing your disbursement immediately. You should receive your funds within the timeline specified above.

If you have any questions, please contact us at {{ contact_info }}.

Congratulations again, and thank you for choosing our services.

Best regards,
The Funding Team
        """.strip()
    
    def _get_funding_approval_html(self) -> str:
        return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; background-color: #d4edda; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h1 style="color: #155724; margin: 0;">🎉 APPROVED! 🎉</h1>
            <h2 style="color: #155724; margin: 10px 0 0 0;">Your Funding Request Has Been Approved</h2>
        </div>
        
        <p>Dear {{ plaintiff_name }},</p>
        
        <p>Congratulations! Your funding request for case <strong>{{ case_number }}</strong> has been <strong style="color: #28a745;">APPROVED</strong>!</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>Approved Amount:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #dee2e6; color: #28a745; font-size: 1.2em; font-weight: bold;">{{ approved_amount | currency }}</td>
                </tr>
                <tr>
                    <td style="padding: 10px;"><strong>Disbursement Timeline:</strong></td>
                    <td style="padding: 10px;">{{ disbursement_timeline }}</td>
                </tr>
            </table>
        </div>
        
        <p>You can review the complete terms and conditions <a href="{{ terms_link }}" style="color: #2c5aa0;">here</a>.</p>
        
        <p>We'll begin processing your disbursement immediately. You should receive your funds within the timeline specified above.</p>
        
        <p>If you have any questions, please contact us at {{ contact_info }}.</p>
        
        <p><strong>Congratulations again, and thank you for choosing our services.</strong></p>
        
        <p>Best regards,<br>
        <strong>The Funding Team</strong></p>
    </div>
</body>
</html>
        """.strip()
    
    def _get_payment_reminder_text(self) -> str:
        return """
Dear {{ plaintiff_name }},

This is a friendly reminder regarding your case {{ case_number }}.

Outstanding Amount: {{ outstanding_amount | currency }}
Due Date: {{ due_date | date_format }}

To make a payment, please visit: {{ payment_link }}

If you have any questions about your account or need to discuss payment arrangements, please contact us at {{ contact_info }}.

Thank you for your attention to this matter.

Best regards,
The Billing Department
        """.strip()
    
    def _get_payment_reminder_html(self) -> str:
        return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #856404;">Payment Reminder</h2>
        
        <p>Dear {{ plaintiff_name }},</p>
        
        <p>This is a friendly reminder regarding your case <strong>{{ case_number }}</strong>.</p>
        
        <div style="background-color: #fff3cd; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ffeaa7;"><strong>Outstanding Amount:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ffeaa7; color: #856404; font-size: 1.1em; font-weight: bold;">{{ outstanding_amount | currency }}</td>
                </tr>
                <tr>
                    <td style="padding: 10px;"><strong>Due Date:</strong></td>
                    <td style="padding: 10px; color: #856404; font-weight: bold;">{{ due_date | date_format }}</td>
                </tr>
            </table>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ payment_link }}" style="background-color: #2c5aa0; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Make Payment</a>
        </div>
        
        <p>If you have any questions about your account or need to discuss payment arrangements, please contact us at {{ contact_info }}.</p>
        
        <p>Thank you for your attention to this matter.</p>
        
        <p>Best regards,<br>
        <strong>The Billing Department</strong></p>
    </div>
</body>
</html>
        """.strip()
    
    async def _initialize_builtin_templates(self) -> None:
        """Initialize built-in templates by saving them to files."""
        for template_name, template_data in self.builtin_templates.items():
            template_file = self.templates_dir / f"{template_name}.json"
            
            if not template_file.exists():
                try:
                    # Add metadata
                    save_data = {
                        **template_data,
                        "type": "builtin",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "version": "1.0",
                    }
                    
                    with open(template_file, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Initialized built-in template: {template_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize template {template_name}: {e}")
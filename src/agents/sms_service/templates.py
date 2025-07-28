"""SMS template management and rendering system."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Environment, Template, TemplateError

from ...config.settings import get_settings
from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SMSTemplateEngine:
    """
    SMS template management and rendering engine.
    
    Handles SMS template storage, rendering with Jinja2,
    and AI-powered template generation for SMS-optimized content.
    """
    
    def __init__(self, ai_client: Optional[OpenAIClient] = None):
        """
        Initialize SMS template engine.
        
        Args:
            ai_client: OpenAI client for AI-powered template generation.
        """
        self.ai_client = ai_client or OpenAIClient()
        
        # Setup template directory
        self.templates_dir = Path(settings.SMS_TEMPLATES_PATH)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # SMS-specific constraints
        self.max_sms_length = 160
        self.max_segments = 3  # Maximum SMS segments for long messages
        
        # Built-in SMS templates
        self.builtin_templates = {
            "welcome_plaintiff": {
                "name": "Welcome Plaintiff SMS",
                "description": "Welcome SMS for new plaintiffs",
                "message": "Welcome to {{ company_name }}! Your case {{ case_number }} is being processed. We'll keep you updated. Reply STOP to opt out.",
                "variables": ["company_name", "case_number"],
                "max_length": 160,
            },
            "document_request": {
                "name": "Document Request SMS",
                "description": "Request documents from plaintiff via SMS",
                "message": "Hi {{ plaintiff_name }}, we need documents for case {{ case_number }}. Upload at {{ upload_link }}. Questions? Call {{ phone }}. Reply STOP to opt out.",
                "variables": ["plaintiff_name", "case_number", "upload_link", "phone"],
                "max_length": 160,
            },
            "appointment_reminder": {
                "name": "Appointment Reminder",
                "description": "Remind plaintiff of upcoming appointment",
                "message": "Reminder: Your appointment is {{ appointment_date }} at {{ appointment_time }}. Location: {{ location }}. Reply STOP to opt out.",
                "variables": ["appointment_date", "appointment_time", "location"],
                "max_length": 160,
            },
            "case_update": {
                "name": "Case Update SMS",
                "description": "Brief case status update",
                "message": "Case {{ case_number }} update: {{ status }}. {{ next_step }}. Questions? Call {{ phone }}. Reply STOP to opt out.",
                "variables": ["case_number", "status", "next_step", "phone"],
                "max_length": 160,
            },
            "funding_approved": {
                "name": "Funding Approved SMS",
                "description": "Funding approval notification",
                "message": "Great news! Your funding for case {{ case_number }} is approved: {{ amount }}. Expect funds in {{ timeline }}. Reply STOP to opt out.",
                "variables": ["case_number", "amount", "timeline"],
                "max_length": 160,
            },
            "payment_reminder": {
                "name": "Payment Due SMS",
                "description": "Payment reminder notification",
                "message": "Payment reminder: {{ amount }} due {{ due_date }} for case {{ case_number }}. Pay at {{ payment_link }}. Reply STOP to opt out.",
                "variables": ["amount", "due_date", "case_number", "payment_link"],
                "max_length": 160,
            },
            "opt_in_confirmation": {
                "name": "Opt-in Confirmation",
                "description": "Confirm SMS opt-in",
                "message": "You've successfully opted in to SMS updates from {{ company_name }}. Reply STOP anytime to unsubscribe.",
                "variables": ["company_name"],
                "max_length": 160,
            },
            "opt_out_confirmation": {
                "name": "Opt-out Confirmation",
                "description": "Confirm SMS opt-out",
                "message": "You've been unsubscribed from SMS messages. You will not receive further texts from us.",
                "variables": [],
                "max_length": 160,
            },
        }
        
        # Initialize built-in templates
        # Note: In production, this should be done during application startup
        # asyncio.create_task(self._initialize_builtin_templates())
    
    async def create_template(
        self,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new SMS template.
        
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
                    "error": f"SMS template '{template_name}' already exists",
                }
            
            # Validate template data
            validation_result = self._validate_sms_template(template_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"SMS template validation failed: {validation_result['errors']}",
                }
            
            # Add metadata
            template_data["created_at"] = datetime.utcnow().isoformat()
            template_data["updated_at"] = datetime.utcnow().isoformat()
            template_data["version"] = "1.0"
            template_data["type"] = "sms"
            
            # Save template
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"SMS template created: {template_name}")
            
            return {
                "success": True,
                "template_name": template_name,
                "template_path": str(template_file),
            }
            
        except Exception as e:
            logger.error(f"Failed to create SMS template {template_name}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get an SMS template by name."""
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
            logger.error(f"Failed to get SMS template {template_name}: {e}")
            return None
    
    async def list_templates(self) -> List[Dict[str, Any]]:
        """List all available SMS templates."""
        templates = []
        
        # Add built-in templates
        for name, template in self.builtin_templates.items():
            templates.append({
                "name": name,
                "display_name": template["name"],
                "description": template["description"],
                "type": "builtin",
                "variables": template.get("variables", []),
                "max_length": template.get("max_length", 160),
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
                    "max_length": template_data.get("max_length", 160),
                    "created_at": template_data.get("created_at"),
                    "updated_at": template_data.get("updated_at"),
                })
                
            except Exception as e:
                logger.warning(f"Failed to load SMS template {template_file}: {e}")
        
        return templates
    
    async def render_template(
        self,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Render an SMS template with provided data.
        
        Args:
            template_name: Name of the template to render.
            template_data: Data to use for rendering.
            
        Returns:
            dict: Rendered template content.
        """
        try:
            template = await self.get_template(template_name)
            if not template:
                raise ValueError(f"SMS template '{template_name}' not found")
            
            # Prepare template context
            context = {
                **template_data,
                "current_date": datetime.now().strftime("%m/%d/%Y"),
                "current_time": datetime.now().strftime("%I:%M %p"),
                "company_name": settings.COMPANY_NAME,
                "company_phone": settings.COMPANY_PHONE,
            }
            
            # Render message
            message_template = Template(template["message"])
            rendered_message = message_template.render(**context)
            
            # Check message length
            message_length = len(rendered_message)
            segments_needed = (message_length + 159) // 160
            
            # Validate length constraints
            max_allowed_length = template.get("max_length", self.max_sms_length)
            if message_length > max_allowed_length:
                return {
                    "success": False,
                    "error": f"Rendered message too long ({message_length} chars, max {max_allowed_length})",
                    "message": rendered_message,
                    "message_length": message_length,
                }
            
            return {
                "success": True,
                "template_name": template_name,
                "message": rendered_message,
                "message_length": message_length,
                "segments_needed": segments_needed,
                "estimated_cost": self._estimate_sms_cost(segments_needed),
                "context_used": context,
            }
            
        except TemplateError as e:
            logger.error(f"SMS template rendering error for {template_name}: {e}")
            return {
                "success": False,
                "error": f"Template rendering failed: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Failed to render SMS template {template_name}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def generate_sms_content(
        self,
        purpose: str,
        context: Dict[str, Any],
        tone: str = "professional",
        max_length: int = 160
    ) -> Dict[str, Any]:
        """
        Generate SMS content using AI.
        
        Args:
            purpose: Purpose of the SMS.
            context: Context information for the SMS.
            tone: Tone of the SMS (professional, friendly, urgent).
            max_length: Maximum length for the SMS.
            
        Returns:
            dict: Generated SMS content.
        """
        try:
            prompt = f"""
            Generate a concise SMS message for the following purpose: {purpose}
            
            Context information:
            {json.dumps(context, indent=2)}
            
            Requirements:
            - Tone: {tone}
            - Maximum length: {max_length} characters
            - Include "Reply STOP to opt out" if space allows
            - Be clear and actionable
            - Suitable for legal services/pre-settlement funding company
            - Use text-friendly abbreviations if needed
            
            Provide ONLY the SMS message text, nothing else.
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=100,
                temperature=0.7
            )
            
            generated_message = response.strip()
            
            # Validate length
            if len(generated_message) > max_length:
                # Try to truncate intelligently
                truncated = self._truncate_sms_message(generated_message, max_length)
                generated_message = truncated
            
            # Calculate segments and cost
            segments_needed = (len(generated_message) + 159) // 160
            
            return {
                "success": True,
                "message": generated_message,
                "message_length": len(generated_message),
                "segments_needed": segments_needed,
                "estimated_cost": self._estimate_sms_cost(segments_needed),
                "purpose": purpose,
                "tone": tone,
                "max_length": max_length,
            }
            
        except Exception as e:
            logger.error(f"Failed to generate SMS content: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def optimize_message_length(
        self,
        message: str,
        target_length: int = 160
    ) -> Dict[str, Any]:
        """
        Optimize SMS message length using AI.
        
        Args:
            message: Original message to optimize.
            target_length: Target character length.
            
        Returns:
            dict: Optimized message.
        """
        try:
            if len(message) <= target_length:
                return {
                    "success": True,
                    "original_message": message,
                    "optimized_message": message,
                    "original_length": len(message),
                    "optimized_length": len(message),
                    "optimization_needed": False,
                }
            
            prompt = f"""
            Shorten this SMS message to fit in {target_length} characters while preserving the key information and call-to-action:
            
            Original message ({len(message)} chars):
            {message}
            
            Requirements:
            - Maximum {target_length} characters
            - Keep the most important information
            - Maintain professional tone
            - Include opt-out instruction if present
            - Use common SMS abbreviations when appropriate
            
            Provide ONLY the shortened message text.
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=80,
                temperature=0.3
            )
            
            optimized_message = response.strip()
            
            # Ensure it's actually shorter
            if len(optimized_message) > target_length:
                optimized_message = self._truncate_sms_message(optimized_message, target_length)
            
            return {
                "success": True,
                "original_message": message,
                "optimized_message": optimized_message,
                "original_length": len(message),
                "optimized_length": len(optimized_message),
                "optimization_needed": True,
                "characters_saved": len(message) - len(optimized_message),
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize SMS message length: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_message": message,
            }
    
    def _validate_sms_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SMS template data structure."""
        errors = []
        
        # Required fields
        required_fields = ["name", "message"]
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate message length
        if template_data.get("message"):
            message = template_data["message"]
            max_length = template_data.get("max_length", self.max_sms_length)
            
            if len(message) > max_length:
                errors.append(f"Message template too long ({len(message)} chars, max {max_length})")
            
            # Check for opt-out instructions
            if "stop" not in message.lower():
                errors.append("Template should include opt-out instructions (Reply STOP to opt out)")
        
        # Validate Jinja2 syntax
        if template_data.get("message"):
            try:
                Template(template_data["message"])
            except TemplateError as e:
                errors.append(f"Invalid Jinja2 syntax in message: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
    
    def _truncate_sms_message(self, message: str, max_length: int) -> str:
        """Intelligently truncate SMS message to fit length limit."""
        if len(message) <= max_length:
            return message
        
        # Reserve space for ellipsis and opt-out
        opt_out_text = " Reply STOP to opt out."
        
        if opt_out_text.lower() in message.lower():
            # Message already has opt-out, just truncate
            return message[:max_length-3] + "..."
        else:
            # Need to add opt-out instructions
            available_length = max_length - len(opt_out_text) - 3  # 3 for "..."
            if available_length > 0:
                return message[:available_length] + "..." + opt_out_text
            else:
                # Just truncate without opt-out
                return message[:max_length-3] + "..."
    
    def _estimate_sms_cost(self, segments: int) -> float:
        """Estimate SMS cost based on number of segments."""
        # Default SMS pricing: ~$0.0075 per segment
        return round(segments * 0.0075, 4)
    
    async def _initialize_builtin_templates(self) -> None:
        """Initialize built-in SMS templates by saving them to files."""
        for template_name, template_data in self.builtin_templates.items():
            template_file = self.templates_dir / f"{template_name}.json"
            
            if not template_file.exists():
                try:
                    # Add metadata
                    save_data = {
                        **template_data,
                        "type": "builtin_sms",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "version": "1.0",
                    }
                    
                    with open(template_file, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Initialized built-in SMS template: {template_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize SMS template {template_name}: {e}")
    
    def get_sms_best_practices(self) -> Dict[str, Any]:
        """Get SMS best practices and guidelines."""
        return {
            "character_limits": {
                "single_sms": 160,
                "concatenated_sms": 153,  # Per segment in multi-part SMS
                "recommended_max": 160,
            },
            "compliance_requirements": [
                "Always include opt-out instructions (Reply STOP to opt out)",
                "Obtain explicit consent before sending marketing SMS",
                "Respect quiet hours (typically 9 PM - 8 AM)",
                "Limit frequency (no more than 3 messages per day)",
                "Include sender identification",
            ],
            "content_guidelines": [
                "Be concise and clear",
                "Include a clear call-to-action",
                "Use urgent tone sparingly",
                "Avoid excessive punctuation or capitalization",
                "Use common abbreviations to save space (w/ = with, u = you)",
            ],
            "formatting_tips": [
                "Use line breaks sparingly (they count as characters)",
                "Avoid special characters that may not display properly",
                "Test messages on different devices",
                "Consider character encoding for international characters",
            ],
        }
"""SMS compliance tracking and management system."""

import re
from datetime import datetime, timedelta, time
from typing import Any, Dict, List, Optional
import pytz

from ...utils.logging import get_logger

logger = get_logger(__name__)


class SMSComplianceTracker:
    """
    SMS compliance tracking system.
    
    Manages opt-in/opt-out status, tracks message frequency,
    enforces quiet hours, and ensures TCPA compliance.
    """
    
    def __init__(self):
        """Initialize compliance tracker."""
        # In-memory storage (should use Redis/database in production)
        self.opt_in_records = {}  # phone_number -> opt_in_data
        self.message_history = {}  # phone_number -> [message_records]
        self.opt_out_records = {}  # phone_number -> opt_out_data
        
        # Compliance settings
        self.default_timezone = pytz.timezone('US/Eastern')
        
        # Prohibited keywords for compliance
        self.prohibited_keywords = [
            # Financial/credit terms
            "guaranteed approval", "no credit check", "debt relief",
            "consolidate debt", "eliminate debt", "credit repair",
            
            # Urgent/pressure tactics
            "act now", "limited time", "expires today", "don't wait",
            "urgent", "immediate", "instant", "now or never",
            
            # Misleading claims
            "risk-free", "guaranteed", "100% approval", "no questions asked",
            "winner", "congratulations", "you've been selected",
            
            # Legal/regulatory
            "lawsuit", "settlement", "injury claim", "compensation guaranteed",
        ]
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\$\d+,?\d*\s*guaranteed',  # Money amounts with "guaranteed"
            r'call\s+now\s+\d{3}[-.]?\d{3}[-.]?\d{4}',  # "Call now" with phone
            r'reply\s+(yes|y)\s+to\s+claim',  # Reply to claim patterns
            r'limited\s+time\s+offer',  # Limited time offers
        ]
    
    async def check_compliance(
        self,
        phone_number: str,
        message: str,
        plaintiff_id: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if SMS complies with regulations and internal rules.
        
        Args:
            phone_number: Recipient phone number.
            message: Message content to check.
            plaintiff_id: Optional plaintiff ID.
            rules: Compliance rules to apply.
            
        Returns:
            dict: Compliance check result.
        """
        issues = []
        warnings = []
        
        # Default rules
        default_rules = {
            "require_opt_in": True,
            "respect_quiet_hours": True,
            "quiet_hours_start": "21:00",
            "quiet_hours_end": "08:00",
            "max_daily_messages": 3,
            "max_message_length": 160,
            "check_prohibited_content": True,
        }
        
        compliance_rules = {**default_rules, **(rules or {})}
        
        try:
            # 1. Check opt-in status
            if compliance_rules["require_opt_in"]:
                opt_in_status = await self.check_opt_in_status(phone_number)
                if not opt_in_status["opted_in"]:
                    issues.append("Recipient has not opted in to SMS communications")
            
            # 2. Check quiet hours
            if compliance_rules["respect_quiet_hours"]:
                quiet_hours_violation = self._check_quiet_hours(
                    compliance_rules["quiet_hours_start"],
                    compliance_rules["quiet_hours_end"]
                )
                if quiet_hours_violation:
                    issues.append(f"Message sent during quiet hours: {quiet_hours_violation}")
            
            # 3. Check daily message limit
            daily_count = await self._get_daily_message_count(phone_number)
            if daily_count >= compliance_rules["max_daily_messages"]:
                issues.append(f"Daily message limit exceeded ({daily_count}/{compliance_rules['max_daily_messages']})")
            
            # 4. Check message length
            if len(message) > compliance_rules["max_message_length"]:
                warnings.append(f"Message length ({len(message)}) exceeds recommended limit ({compliance_rules['max_message_length']})")
            
            # 5. Check prohibited content
            if compliance_rules["check_prohibited_content"]:
                content_issues = self._check_prohibited_content(message)
                issues.extend(content_issues)
            
            # 6. Check for missing opt-out instructions
            if not self._has_opt_out_instructions(message):
                warnings.append("Message lacks opt-out instructions")
            
            # 7. Check frequency (not more than 1 per hour)
            last_message_time = await self._get_last_message_time(phone_number)
            if last_message_time and (datetime.utcnow() - last_message_time).seconds < 3600:
                warnings.append("Message sent less than 1 hour after previous message")
            
            compliance_result = {
                "compliant": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "phone_number": phone_number,
                "check_timestamp": datetime.utcnow().isoformat(),
                "rules_applied": compliance_rules,
            }
            
            # Log compliance check
            if not compliance_result["compliant"]:
                logger.warning(
                    "SMS compliance violation detected",
                    phone_number=phone_number,
                    issues=issues,
                    message_preview=message[:50],
                )
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"SMS compliance check failed: {e}")
            return {
                "compliant": False,
                "issues": [f"Compliance check failed: {str(e)}"],
                "warnings": [],
                "error": str(e),
            }
    
    async def check_opt_in_status(self, phone_number: str) -> Dict[str, Any]:
        """Check opt-in status for phone number."""
        opt_in_data = self.opt_in_records.get(phone_number)
        
        if not opt_in_data:
            return {
                "opted_in": False,
                "phone_number": phone_number,
                "status": "no_record",
            }
        
        # Check if opt-out overrides opt-in
        opt_out_data = self.opt_out_records.get(phone_number)
        if opt_out_data and opt_out_data["timestamp"] > opt_in_data["timestamp"]:
            return {
                "opted_in": False,
                "phone_number": phone_number,
                "status": "opted_out",
                "opt_out_date": opt_out_data["timestamp"],
                "opt_out_reason": opt_out_data["reason"],
            }
        
        return {
            "opted_in": True,
            "phone_number": phone_number,
            "status": "opted_in",
            "opt_in_date": opt_in_data["timestamp"],
            "consent_method": opt_in_data["consent_method"],
        }
    
    async def handle_opt_in(
        self,
        phone_number: str,
        consent_method: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle opt-in consent."""
        try:
            opt_in_data = {
                "phone_number": phone_number,
                "timestamp": datetime.utcnow().isoformat(),
                "consent_method": consent_method,
                "metadata": metadata or {},
                "ip_address": metadata.get("ip_address") if metadata else None,
                "user_agent": metadata.get("user_agent") if metadata else None,
            }
            
            self.opt_in_records[phone_number] = opt_in_data
            
            # Remove from opt-out records if present
            if phone_number in self.opt_out_records:
                del self.opt_out_records[phone_number]
            
            logger.info(
                "SMS opt-in recorded",
                phone_number=phone_number,
                consent_method=consent_method,
            )
            
            return {
                "success": True,
                "phone_number": phone_number,
                "opt_in_timestamp": opt_in_data["timestamp"],
                "consent_method": consent_method,
            }
            
        except Exception as e:
            logger.error(f"Failed to handle opt-in: {e}")
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number,
            }
    
    async def handle_opt_out(
        self,
        phone_number: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle opt-out request."""
        try:
            opt_out_data = {
                "phone_number": phone_number,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason,
                "metadata": metadata or {},
            }
            
            self.opt_out_records[phone_number] = opt_out_data
            
            logger.info(
                "SMS opt-out recorded",
                phone_number=phone_number,
                reason=reason,
            )
            
            return {
                "success": True,
                "phone_number": phone_number,
                "opt_out_timestamp": opt_out_data["timestamp"],
                "reason": reason,
            }
            
        except Exception as e:
            logger.error(f"Failed to handle opt-out: {e}")
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number,
            }
    
    async def track_outbound_message(
        self,
        phone_number: str,
        message: str,
        plaintiff_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> None:
        """Track outbound SMS message for compliance monitoring."""
        message_record = {
            "phone_number": phone_number,
            "message": message,
            "plaintiff_id": plaintiff_id,
            "message_id": message_id,
            "timestamp": datetime.utcnow(),
            "direction": "outbound",
            "message_length": len(message),
        }
        
        if phone_number not in self.message_history:
            self.message_history[phone_number] = []
        
        self.message_history[phone_number].append(message_record)
        
        # Keep only last 100 messages per phone number
        if len(self.message_history[phone_number]) > 100:
            self.message_history[phone_number] = self.message_history[phone_number][-100:]
    
    async def get_compliance_report(
        self,
        phone_number: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate compliance report."""
        try:
            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "from": date_from.isoformat() if date_from else None,
                    "to": date_to.isoformat() if date_to else None,
                },
                "total_opt_ins": len(self.opt_in_records),
                "total_opt_outs": len(self.opt_out_records),
                "active_opt_ins": 0,
                "compliance_issues": [],
            }
            
            # Calculate active opt-ins (not opted out)
            for phone, opt_in_data in self.opt_in_records.items():
                opt_out_data = self.opt_out_records.get(phone)
                if not opt_out_data or opt_out_data["timestamp"] < opt_in_data["timestamp"]:
                    report["active_opt_ins"] += 1
            
            # Filter by phone number if specified
            phone_numbers = [phone_number] if phone_number else list(self.message_history.keys())
            
            message_count = 0
            for phone in phone_numbers:
                messages = self.message_history.get(phone, [])
                
                for message_record in messages:
                    # Apply date filters
                    if date_from and message_record["timestamp"] < date_from:
                        continue
                    if date_to and message_record["timestamp"] > date_to:
                        continue
                    
                    message_count += 1
            
            report["total_messages"] = message_count
            report["opt_out_rate"] = (
                report["total_opt_outs"] / (report["total_opt_ins"] or 1) * 100
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat(),
            }
    
    def _check_quiet_hours(
        self,
        quiet_start: str,
        quiet_end: str,
        timezone: Optional[pytz.BaseTzInfo] = None
    ) -> Optional[str]:
        """Check if current time is within quiet hours."""
        try:
            tz = timezone or self.default_timezone
            current_time = datetime.now(tz).time()
            
            # Parse quiet hours
            start_time = time.fromisoformat(quiet_start)
            end_time = time.fromisoformat(quiet_end)
            
            # Handle overnight quiet hours (e.g., 21:00 to 08:00)
            if start_time > end_time:
                if current_time >= start_time or current_time <= end_time:
                    return f"Current time {current_time} is within quiet hours {quiet_start}-{quiet_end}"
            else:
                if start_time <= current_time <= end_time:
                    return f"Current time {current_time} is within quiet hours {quiet_start}-{quiet_end}"
            
            return None
            
        except Exception as e:
            logger.error(f"Quiet hours check failed: {e}")
            return f"Quiet hours check error: {str(e)}"
    
    async def _get_daily_message_count(self, phone_number: str) -> int:
        """Get number of messages sent to phone number today."""
        messages = self.message_history.get(phone_number, [])
        today = datetime.utcnow().date()
        
        daily_count = 0
        for message_record in messages:
            if message_record["timestamp"].date() == today:
                daily_count += 1
        
        return daily_count
    
    async def _get_last_message_time(self, phone_number: str) -> Optional[datetime]:
        """Get timestamp of last message sent to phone number."""
        messages = self.message_history.get(phone_number, [])
        
        if not messages:
            return None
        
        # Messages are stored in chronological order
        return messages[-1]["timestamp"]
    
    def _check_prohibited_content(self, message: str) -> List[str]:
        """Check message content for prohibited terms and patterns."""
        issues = []
        message_lower = message.lower()
        
        # Check prohibited keywords
        for keyword in self.prohibited_keywords:
            if keyword.lower() in message_lower:
                issues.append(f"Contains prohibited keyword: '{keyword}'")
        
        # Check suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, message_lower):
                issues.append(f"Contains suspicious pattern: {pattern}")
        
        # Check for excessive capitalization
        if len(re.findall(r'[A-Z]', message)) > len(message) * 0.5:
            issues.append("Excessive use of capital letters")
        
        # Check for excessive punctuation
        if len(re.findall(r'[!?]{2,}', message)) > 0:
            issues.append("Excessive use of exclamation marks or question marks")
        
        return issues
    
    def _has_opt_out_instructions(self, message: str) -> bool:
        """Check if message contains opt-out instructions."""
        opt_out_patterns = [
            r'reply\s+stop',
            r'text\s+stop',
            r'stop\s+to\s+opt\s*out',
            r'stop\s+to\s+unsubscribe',
            r'opt\s*out',
        ]
        
        message_lower = message.lower()
        
        return any(re.search(pattern, message_lower) for pattern in opt_out_patterns)
    
    def cleanup_old_records(self, days: int = 365) -> Dict[str, Any]:
        """Clean up old compliance records."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Clean up message history
            cleaned_messages = 0
            for phone_number in list(self.message_history.keys()):
                messages = self.message_history[phone_number]
                original_count = len(messages)
                
                # Keep only recent messages
                self.message_history[phone_number] = [
                    msg for msg in messages 
                    if msg["timestamp"] > cutoff_date
                ]
                
                cleaned_messages += original_count - len(self.message_history[phone_number])
                
                # Remove empty message histories
                if not self.message_history[phone_number]:
                    del self.message_history[phone_number]
            
            logger.info(f"Cleaned up {cleaned_messages} old message records")
            
            return {
                "success": True,
                "cleaned_messages": cleaned_messages,
                "cutoff_date": cutoff_date.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup compliance records: {e}")
            return {
                "success": False,
                "error": str(e),
            }
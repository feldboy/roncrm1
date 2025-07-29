"""Lead parsing utilities for different input formats."""

import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ...utils.logging import get_logger

logger = get_logger(__name__)

class BaseLeadParser:
    """Base class for lead parsers."""
    
    def __init__(self):
        self.name = "base_parser"
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse lead content and return structured data."""
        raise NotImplementedError
    
    def validate_parsed_data(self, data: Dict[str, Any]) -> bool:
        """Validate that parsed data contains required fields."""
        required_fields = ['first_name', 'last_name', 'phone', 'email']
        return all(field in data and data[field] for field in required_fields)

class EmailLeadParser(BaseLeadParser):
    """Parser for email-based leads."""
    
    def __init__(self):
        super().__init__()
        self.name = "email_parser"
        
        # Patterns for extracting information from email
        self.patterns = {
            'name': re.compile(r'(?:name|client|plaintiff):\s*([^\n\r]+)', re.IGNORECASE),
            'phone': re.compile(r'(?:phone|tel|telephone|mobile|cell):\s*([+\d\s\-\(\)]+)', re.IGNORECASE),
            'email': re.compile(r'(?:email|e-mail):\s*([^\s\n\r]+@[^\s\n\r]+)', re.IGNORECASE),
            'incident_date': re.compile(r'(?:incident|accident|date of accident):\s*([^\n\r]+)', re.IGNORECASE),
            'description': re.compile(r'(?:description|details|incident details):\s*([^\n\r]+(?:\n[^\n\r]+)*)', re.IGNORECASE),
            'case_type': re.compile(r'(?:case type|type of case|injury type):\s*([^\n\r]+)', re.IGNORECASE),
            'medical_treatment': re.compile(r'(?:medical treatment|hospital|doctor):\s*([^\n\r]+)', re.IGNORECASE),
        }
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse email content for lead information."""
        try:
            # If content is raw email, parse it
            if content.startswith('From:') or content.startswith('Subject:'):
                parsed_email = email.message_from_string(content)
                email_body = self._extract_email_body(parsed_email)
                subject = parsed_email.get('Subject', '')
                sender = parsed_email.get('From', '')
            else:
                email_body = content
                subject = ''
                sender = ''
            
            # Extract structured data using patterns
            extracted_data = {}
            
            for field, pattern in self.patterns.items():
                match = pattern.search(email_body)
                if match:
                    extracted_data[field] = match.group(1).strip()
            
            # Process name field to split into first/last name
            if 'name' in extracted_data:
                name_parts = extracted_data['name'].split()
                if len(name_parts) >= 2:
                    extracted_data['first_name'] = name_parts[0]
                    extracted_data['last_name'] = ' '.join(name_parts[1:])
                elif len(name_parts) == 1:
                    extracted_data['first_name'] = name_parts[0]
                    extracted_data['last_name'] = ''
                del extracted_data['name']
            
            # Clean phone number
            if 'phone' in extracted_data:
                extracted_data['phone'] = self._clean_phone_number(extracted_data['phone'])
            
            # Process incident date
            if 'incident_date' in extracted_data:
                extracted_data['incident_date'] = self._parse_date(extracted_data['incident_date'])
            
            # Add metadata
            extracted_data.update({
                'source_type': 'email',
                'source_subject': subject,
                'source_sender': sender,
                'raw_content': email_body,
                'parsed_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Email lead parsed successfully", extracted_fields=list(extracted_data.keys()))
            return extracted_data
            
        except Exception as e:
            logger.error(f"Failed to parse email lead: {e}")
            return {
                'source_type': 'email',
                'raw_content': content,
                'parse_error': str(e),
                'parsed_at': datetime.utcnow().isoformat()
            }
    
    def _extract_email_body(self, msg) -> str:
        """Extract body text from email message."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # If it starts with 1 and is 11 digits, format as US number
        if cleaned.startswith('1') and len(cleaned) == 11:
            return f"+{cleaned}"
        elif len(cleaned) == 10:
            return f"+1{cleaned}"
        
        return cleaned
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string into ISO format."""
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD format
                        year, month, day = groups
                    else:  # MM/DD/YYYY or MM-DD-YYYY format
                        month, day, year = groups
                    
                    parsed_date = datetime(int(year), int(month), int(day))
                    return parsed_date.date().isoformat()
                except ValueError:
                    continue
        
        return None

class FormLeadParser(BaseLeadParser):
    """Parser for web form submissions."""
    
    def __init__(self):
        super().__init__()
        self.name = "form_parser"
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse form data (JSON or form-encoded)."""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                data = json.loads(content)
            else:
                # Parse as form-encoded data
                data = self._parse_form_encoded(content)
            
            # Normalize field names
            normalized_data = self._normalize_field_names(data)
            
            # Clean and validate data
            cleaned_data = self._clean_form_data(normalized_data)
            
            # Add metadata
            cleaned_data.update({
                'source_type': 'web_form',
                'raw_content': content,
                'parsed_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Form lead parsed successfully", extracted_fields=list(cleaned_data.keys()))
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Failed to parse form lead: {e}")
            return {
                'source_type': 'web_form',
                'raw_content': content,
                'parse_error': str(e),
                'parsed_at': datetime.utcnow().isoformat()
            }
    
    def _parse_form_encoded(self, content: str) -> Dict[str, Any]:
        """Parse form-encoded data."""
        from urllib.parse import parse_qs
        
        data = {}
        for key, values in parse_qs(content).items():
            data[key] = values[0] if len(values) == 1 else values
        
        return data
    
    def _normalize_field_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field names to standard format."""
        field_mapping = {
            'fname': 'first_name',
            'firstname': 'first_name',
            'first': 'first_name',
            'lname': 'last_name',
            'lastname': 'last_name',
            'last': 'last_name',
            'phone_number': 'phone',
            'telephone': 'phone',
            'mobile': 'phone',
            'email_address': 'email',
            'e_mail': 'email',
            'incident_description': 'description',
            'accident_description': 'description',
            'details': 'description',
            'accident_date': 'incident_date',
            'date_of_accident': 'incident_date',
            'injury_type': 'case_type',
            'case_category': 'case_type',
        }
        
        normalized = {}
        for key, value in data.items():
            # Convert key to lowercase and replace spaces/dashes with underscores
            normalized_key = key.lower().replace(' ', '_').replace('-', '_')
            
            # Map to standard field name if mapping exists
            final_key = field_mapping.get(normalized_key, normalized_key)
            normalized[final_key] = value
        
        return normalized
    
    def _clean_form_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate form data."""
        cleaned = {}
        
        for key, value in data.items():
            if value and str(value).strip():
                # Clean string values
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    
                    # Special handling for specific fields
                    if key == 'phone':
                        cleaned_value = self._clean_phone_number(cleaned_value)
                    elif key == 'email':
                        cleaned_value = cleaned_value.lower()
                    elif key == 'incident_date':
                        cleaned_value = self._parse_date(cleaned_value)
                    
                    if cleaned_value:
                        cleaned[key] = cleaned_value
                else:
                    cleaned[key] = value
        
        return cleaned
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # If it starts with 1 and is 11 digits, format as US number
        if cleaned.startswith('1') and len(cleaned) == 11:
            return f"+{cleaned}"
        elif len(cleaned) == 10:
            return f"+1{cleaned}"
        
        return cleaned
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string into ISO format."""
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{1,2})-(\d{1,2})-(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:
                        year, month, day = groups
                    else:
                        month, day, year = groups
                    
                    parsed_date = datetime(int(year), int(month), int(day))
                    return parsed_date.date().isoformat()
                except ValueError:
                    continue
        
        return None

class LeadParserFactory:
    """Factory for creating appropriate lead parsers."""
    
    def __init__(self):
        self.parsers = {
            'email': EmailLeadParser(),
            'form': FormLeadParser(),
            'web_form': FormLeadParser(),
        }
    
    def get_parser(self, source_type: str) -> BaseLeadParser:
        """Get appropriate parser for source type."""
        return self.parsers.get(source_type.lower(), self.parsers['form'])
    
    def parse_lead(self, content: str, source_type: str = 'form') -> Dict[str, Any]:
        """Parse lead content using appropriate parser."""
        parser = self.get_parser(source_type)
        return parser.parse(content)

# Global factory instance
lead_parser_factory = LeadParserFactory()

# Export commonly used items
__all__ = [
    'BaseLeadParser',
    'EmailLeadParser', 
    'FormLeadParser',
    'LeadParserFactory',
    'lead_parser_factory'
]
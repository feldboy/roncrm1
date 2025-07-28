"""Document validation utilities for verifying document completeness and accuracy."""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger

logger = get_logger(__name__)


class DocumentValidator:
    """
    Document validation service for verifying document completeness and accuracy.
    
    Validates documents based on type-specific requirements and uses AI
    to detect inconsistencies and missing information.
    """
    
    def __init__(self, ai_client: Optional[OpenAIClient] = None):
        """
        Initialize document validator.
        
        Args:
            ai_client: OpenAI client for AI-powered validation.
        """
        self.ai_client = ai_client or OpenAIClient()
        
        # Validation rules for different document types
        self.validation_rules = {
            "medical_record": {
                "required_fields": [
                    "patient_name", "date_of_birth", "medical_record_number",
                    "provider_name", "date_of_service", "diagnosis"
                ],
                "optional_fields": [
                    "insurance_info", "treatment_plan", "medications",
                    "vital_signs", "allergies", "emergency_contact"
                ],
                "format_checks": [
                    ("date_format", r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'),
                    ("mrn_format", r'\bMRN[\s#:]*\d+'),
                    ("provider_format", r'\bDr\.?\s+[A-Z][a-z]+'),
                ],
                "consistency_checks": [
                    "date_logic", "age_consistency", "provider_credentials"
                ],
                "completeness_weight": 0.4,
                "accuracy_weight": 0.3,
                "consistency_weight": 0.3,
            },
            "police_report": {
                "required_fields": [
                    "incident_number", "date_time", "location", "officer_name",
                    "badge_number", "incident_type", "narrative"
                ],
                "optional_fields": [
                    "witness_info", "vehicle_info", "property_damage",
                    "citations_issued", "evidence_collected"
                ],
                "format_checks": [
                    ("incident_number", r'\b(?:Case|Report|Incident)[\s#:]*\d+'),
                    ("badge_number", r'\bBadge[\s#:]*\d+'),
                    ("date_format", r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'),
                ],
                "consistency_checks": [
                    "date_logic", "location_consistency", "officer_verification"
                ],
                "completeness_weight": 0.5,
                "accuracy_weight": 0.3,
                "consistency_weight": 0.2,
            },
            "legal_contract": {
                "required_fields": [
                    "parties", "effective_date", "terms", "signatures",
                    "governing_law", "consideration"
                ],
                "optional_fields": [
                    "termination_clause", "dispute_resolution", "amendments",
                    "notarization", "witness_signatures"
                ],
                "format_checks": [
                    ("signature_line", r'\b(?:Signature|Signed)[\s:]*_+'),
                    ("date_format", r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'),
                    ("party_designation", r'\bParty of the (?:First|Second) Part'),
                ],
                "consistency_checks": [
                    "date_logic", "party_consistency", "legal_formatting"
                ],
                "completeness_weight": 0.4,
                "accuracy_weight": 0.4,
                "consistency_weight": 0.2,
            },
            "insurance_document": {
                "required_fields": [
                    "policy_number", "insured_name", "coverage_amounts",
                    "effective_date", "expiration_date", "insurer_name"
                ],
                "optional_fields": [
                    "deductible", "beneficiaries", "exclusions", "riders",
                    "premium_amount", "payment_schedule"
                ],
                "format_checks": [
                    ("policy_number", r'\bPolicy[\s#:]*[A-Z0-9]+'),
                    ("coverage_amount", r'\$[\d,]+(?:\.\d{2})?'),
                    ("date_format", r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'),
                ],
                "consistency_checks": [
                    "date_logic", "coverage_consistency", "premium_calculation"
                ],
                "completeness_weight": 0.4,
                "accuracy_weight": 0.3,
                "consistency_weight": 0.3,
            },
            "financial_document": {
                "required_fields": [
                    "account_holder", "account_number", "statement_period",
                    "financial_institution", "amounts"
                ],
                "optional_fields": [
                    "routing_number", "interest_rate", "fees", "contact_info",
                    "tax_id", "account_type"
                ],
                "format_checks": [
                    ("account_number", r'\bAccount[\s#:]*\d+'),
                    ("amount_format", r'\$[\d,]+\.?\d{0,2}'),
                    ("routing_number", r'\bRouting[\s#:]*\d{9}'),
                ],
                "consistency_checks": [
                    "date_logic", "amount_consistency", "calculation_accuracy"
                ],
                "completeness_weight": 0.3,
                "accuracy_weight": 0.5,
                "consistency_weight": 0.2,
            },
        }
        
        # Common validation patterns
        self.common_patterns = {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "zip_code": r'\b\d{5}(?:-\d{4})?\b',
            "state": r'\b[A-Z]{2}\b',
        }
        
        # Red flags that indicate potential issues
        self.red_flags = {
            "inconsistent_dates": [
                "dates that don't make logical sense",
                "future dates for past events",
                "birth dates after incident dates"
            ],
            "missing_signatures": [
                "signature lines without signatures",
                "unsigned legal documents",
                "missing witness signatures"
            ],
            "incomplete_information": [
                "blank required fields",
                "partial addresses",
                "incomplete names"
            ],
            "format_issues": [
                "incorrect date formats",
                "invalid phone numbers",
                "malformed email addresses"
            ],
        }
    
    async def validate_document(
        self,
        text: str,
        document_type: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate document completeness, accuracy, and consistency.
        
        Args:
            text: Document text.
            document_type: Type of document.
            entities: Extracted entities.
            
        Returns:
            dict: Validation results with score and issues.
        """
        if not text:
            return {
                "success": False,
                "error": "No text provided for validation",
                "is_valid": False,
                "score": 0.0,
            }
        
        try:
            # Get validation rules for document type
            rules = self.validation_rules.get(document_type, {})
            
            if not rules:
                # For unknown document types, perform basic validation
                return await self._validate_unknown_document(text, entities)
            
            # Perform structured validation
            validation_result = {
                "document_type": document_type,
                "validation_components": {},
                "issues": [],
                "warnings": [],
                "red_flags": [],
                "score": 0.0,
                "is_valid": False,
            }
            
            # 1. Completeness check
            completeness_result = self._check_completeness(text, entities, rules)
            validation_result["validation_components"]["completeness"] = completeness_result
            
            # 2. Format check
            format_result = self._check_format(text, rules)
            validation_result["validation_components"]["format"] = format_result
            
            # 3. Consistency check
            consistency_result = await self._check_consistency(text, entities, rules)
            validation_result["validation_components"]["consistency"] = consistency_result
            
            # 4. AI-powered validation
            ai_result = await self._ai_validate_document(text, document_type)
            validation_result["validation_components"]["ai_analysis"] = ai_result
            
            # Calculate overall score
            overall_score = self._calculate_validation_score(
                completeness_result, format_result, consistency_result, ai_result, rules
            )
            
            validation_result["score"] = overall_score
            validation_result["is_valid"] = overall_score >= 0.7  # 70% threshold
            
            # Compile issues
            all_components = [completeness_result, format_result, consistency_result, ai_result]
            for component in all_components:
                validation_result["issues"].extend(component.get("issues", []))
                validation_result["warnings"].extend(component.get("warnings", []))
                validation_result["red_flags"].extend(component.get("red_flags", []))
            
            return {
                "success": True,
                **validation_result,
            }
            
        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "is_valid": False,
                "score": 0.0,
            }
    
    def _check_completeness(
        self,
        text: str,
        entities: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check document completeness based on required fields."""
        required_fields = rules.get("required_fields", [])
        optional_fields = rules.get("optional_fields", [])
        
        found_required = []
        missing_required = []
        found_optional = []
        
        text_lower = text.lower()
        
        # Check required fields
        for field in required_fields:
            field_patterns = self._get_field_patterns(field)
            field_found = False
            
            for pattern in field_patterns:
                if re.search(pattern, text_lower) or self._check_entities_for_field(field, entities):
                    found_required.append(field)
                    field_found = True
                    break
            
            if not field_found:
                missing_required.append(field)
        
        # Check optional fields
        for field in optional_fields:
            field_patterns = self._get_field_patterns(field)
            
            for pattern in field_patterns:
                if re.search(pattern, text_lower) or self._check_entities_for_field(field, entities):
                    found_optional.append(field)
                    break
        
        # Calculate completeness score
        required_score = len(found_required) / len(required_fields) if required_fields else 1.0
        optional_score = len(found_optional) / len(optional_fields) if optional_fields else 0.5
        
        completeness_score = required_score * 0.8 + optional_score * 0.2
        
        issues = []
        warnings = []
        
        if missing_required:
            issues.extend([f"Missing required field: {field}" for field in missing_required])
        
        if len(found_optional) < len(optional_fields) * 0.5:
            warnings.append("Document missing many optional fields")
        
        return {
            "score": completeness_score,
            "found_required": found_required,
            "missing_required": missing_required,
            "found_optional": found_optional,
            "issues": issues,
            "warnings": warnings,
            "red_flags": [],
        }
    
    def _check_format(self, text: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Check document format compliance."""
        format_checks = rules.get("format_checks", [])
        
        passed_checks = []
        failed_checks = []
        issues = []
        warnings = []
        
        for check_name, pattern in format_checks:
            if re.search(pattern, text, re.IGNORECASE):
                passed_checks.append(check_name)
            else:
                failed_checks.append(check_name)
                warnings.append(f"Format check failed: {check_name}")
        
        # Check common patterns
        common_issues = self._check_common_formats(text)
        issues.extend(common_issues)
        
        # Calculate format score
        if format_checks:
            format_score = len(passed_checks) / len(format_checks)
        else:
            format_score = 1.0 if not common_issues else 0.8
        
        # Penalty for common format issues
        if common_issues:
            format_score *= (1.0 - len(common_issues) * 0.1)
        
        return {
            "score": max(format_score, 0.0),
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "issues": issues,
            "warnings": warnings,
            "red_flags": [],
        }
    
    async def _check_consistency(
        self,
        text: str,
        entities: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check document consistency."""
        consistency_checks = rules.get("consistency_checks", [])
        
        issues = []
        warnings = []
        red_flags = []
        
        # Date logic consistency
        if "date_logic" in consistency_checks:
            date_issues = self._check_date_consistency(text, entities)
            issues.extend(date_issues)
        
        # Age consistency
        if "age_consistency" in consistency_checks:
            age_issues = self._check_age_consistency(text, entities)
            issues.extend(age_issues)
        
        # Name consistency
        if "name_consistency" in consistency_checks:
            name_issues = self._check_name_consistency(text, entities)
            warnings.extend(name_issues)
        
        # Amount/calculation consistency
        if "calculation_accuracy" in consistency_checks:
            calc_issues = self._check_calculation_consistency(text, entities)
            issues.extend(calc_issues)
        
        # Calculate consistency score
        total_checks = len(consistency_checks)
        failed_checks = len(issues)
        
        if total_checks > 0:
            consistency_score = max(0.0, 1.0 - (failed_checks / total_checks))
        else:
            consistency_score = 1.0
        
        # Major inconsistencies are red flags
        if failed_checks > 0:
            red_flags.extend([f"Consistency issue: {issue}" for issue in issues[:2]])
        
        return {
            "score": consistency_score,
            "issues": issues,
            "warnings": warnings,
            "red_flags": red_flags,
        }
    
    async def _ai_validate_document(
        self,
        text: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Use AI to validate document."""
        try:
            # Limit text for AI processing
            text_sample = text[:2000] if len(text) > 2000 else text
            
            prompt = f"""
            Review this {document_type} for validation issues:
            
            Document text:
            {text_sample}
            
            Identify any:
            1. Missing critical information
            2. Inconsistencies or contradictions
            3. Format or structural issues
            4. Potential red flags or concerns
            5. Overall document quality (1-10 scale)
            
            Respond in this format:
            Missing: [list any missing critical info]
            Inconsistencies: [list any inconsistencies]
            Format Issues: [list format problems]
            Red Flags: [list any concerns]
            Quality Score: [1-10]
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=300,
                temperature=0.2
            )
            
            # Parse AI response
            ai_issues = self._parse_ai_validation_response(response)
            
            # Calculate AI validation score
            quality_score = ai_issues.get("quality_score", 5) / 10.0
            
            return {
                "score": quality_score,
                "issues": ai_issues.get("missing", []) + ai_issues.get("format_issues", []),
                "warnings": ai_issues.get("inconsistencies", []),
                "red_flags": ai_issues.get("red_flags", []),
                "ai_response": response,
            }
            
        except Exception as e:
            logger.error(f"AI validation failed: {e}")
            return {
                "score": 0.5,  # Default score if AI fails
                "issues": [],
                "warnings": ["AI validation unavailable"],
                "red_flags": [],
                "error": str(e),
            }
    
    def _get_field_patterns(self, field: str) -> List[str]:
        """Get regex patterns for a field type."""
        field_patterns = {
            "patient_name": [r'\bpatient[\s:]+[A-Z][a-z]+', r'\bname[\s:]+[A-Z][a-z]+'],
            "date_of_birth": [r'\b(?:DOB|Date of Birth)[\s:]*\d{1,2}[/-]\d{1,2}[/-]\d{4}'],
            "medical_record_number": [r'\bMRN[\s#:]*\d+', r'\bMedical Record[\s#:]*\d+'],
            "provider_name": [r'\bDr\.?\s+[A-Z][a-z]+', r'\bPhysician[\s:]+[A-Z][a-z]+'],
            "incident_number": [r'\b(?:Case|Report|Incident)[\s#:]*\d+'],
            "officer_name": [r'\bOfficer\s+[A-Z][a-z]+'],
            "badge_number": [r'\bBadge[\s#:]*\d+'],
            "policy_number": [r'\bPolicy[\s#:]*[A-Z0-9]+'],
            "account_number": [r'\bAccount[\s#:]*\d+'],
            "signatures": [r'\b(?:Signature|Signed)[\s:]*[A-Z]', r'_+\s*(?:Signature|Date)'],
        }
        
        return field_patterns.get(field, [f'\\b{field.replace("_", "\\s+")}\\b'])
    
    def _check_entities_for_field(self, field: str, entities: Dict[str, Any]) -> bool:
        """Check if field is present in extracted entities."""
        field_entity_mapping = {
            "patient_name": ["people", "names"],
            "provider_name": ["people", "providers"],
            "date_of_birth": ["dates"],
            "incident_number": ["case_numbers", "incident_numbers"],
            "policy_number": ["policy_numbers"],
            "account_number": ["account_numbers"],
        }
        
        entity_types = field_entity_mapping.get(field, [])
        
        for entity_type in entity_types:
            if entity_type in entities and entities[entity_type]:
                return True
        
        return False
    
    def _check_common_formats(self, text: str) -> List[str]:
        """Check for common format issues."""
        issues = []
        
        # Check for malformed phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        potential_phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{1,3}\b', text)
        valid_phones = re.findall(phone_pattern, text)
        
        if len(potential_phones) > len(valid_phones):
            issues.append("Malformed phone numbers detected")
        
        # Check for malformed emails
        potential_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\b', text)
        valid_emails = re.findall(self.common_patterns["email"], text)
        
        if len(potential_emails) > len(valid_emails):
            issues.append("Malformed email addresses detected")
        
        return issues
    
    def _check_date_consistency(self, text: str, entities: Dict[str, Any]) -> List[str]:
        """Check for date logic issues."""
        issues = []
        
        # Extract dates
        dates = entities.get("dates", [])
        if not dates:
            dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text)
        
        # Parse dates and check for logical consistency
        parsed_dates = []
        for date_str in dates:
            try:
                # Try different date formats
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        parsed_dates.append(parsed_date)
                        break
                    except ValueError:
                        continue
            except:
                continue
        
        # Check for future dates in historical documents
        now = datetime.now()
        for date in parsed_dates:
            if date > now:
                issues.append(f"Future date found: {date.strftime('%m/%d/%Y')}")
        
        return issues
    
    def _check_age_consistency(self, text: str, entities: Dict[str, Any]) -> List[str]:
        """Check for age-related consistency issues."""
        issues = []
        
        # This would implement age consistency checks
        # For example, birth date vs. current age, incident age, etc.
        
        return issues
    
    def _check_name_consistency(self, text: str, entities: Dict[str, Any]) -> List[str]:
        """Check for name consistency issues."""
        warnings = []
        
        # Extract names from entities
        people = entities.get("people", [])
        
        # Check for potential name variations or inconsistencies
        if len(set(people)) < len(people):
            warnings.append("Potential name variations detected")
        
        return warnings
    
    def _check_calculation_consistency(self, text: str, entities: Dict[str, Any]) -> List[str]:
        """Check for calculation or amount consistency."""
        issues = []
        
        # Extract amounts
        amounts = entities.get("amounts", [])
        if not amounts:
            amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
        
        # Basic checks for amount consistency
        # This could be expanded with more sophisticated financial validation
        
        return issues
    
    def _calculate_validation_score(
        self,
        completeness: Dict[str, Any],
        format_check: Dict[str, Any],
        consistency: Dict[str, Any],
        ai_analysis: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> float:
        """Calculate overall validation score."""
        # Get weights from rules
        completeness_weight = rules.get("completeness_weight", 0.4)
        accuracy_weight = rules.get("accuracy_weight", 0.3)
        consistency_weight = rules.get("consistency_weight", 0.3)
        
        # Calculate weighted score
        weighted_score = (
            completeness["score"] * completeness_weight +
            format_check["score"] * accuracy_weight +
            consistency["score"] * consistency_weight
        )
        
        # Incorporate AI score (10% weight)
        final_score = weighted_score * 0.9 + ai_analysis["score"] * 0.1
        
        return min(max(final_score, 0.0), 1.0)
    
    def _parse_ai_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse AI validation response."""
        result = {
            "missing": [],
            "inconsistencies": [],
            "format_issues": [],
            "red_flags": [],
            "quality_score": 5,
        }
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Missing:"):
                current_section = "missing"
                content = line.replace("Missing:", "").strip()
                if content and content != "None":
                    result["missing"].append(content)
            elif line.startswith("Inconsistencies:"):
                current_section = "inconsistencies"
                content = line.replace("Inconsistencies:", "").strip()
                if content and content != "None":
                    result["inconsistencies"].append(content)
            elif line.startswith("Format Issues:"):
                current_section = "format_issues"
                content = line.replace("Format Issues:", "").strip()
                if content and content != "None":
                    result["format_issues"].append(content)
            elif line.startswith("Red Flags:"):
                current_section = "red_flags"
                content = line.replace("Red Flags:", "").strip()
                if content and content != "None":
                    result["red_flags"].append(content)
            elif line.startswith("Quality Score:"):
                score_text = line.replace("Quality Score:", "").strip()
                try:
                    result["quality_score"] = int(score_text)
                except ValueError:
                    result["quality_score"] = 5
            elif current_section and line:
                # Continue previous section
                result[current_section].append(line)
        
        return result
    
    async def _validate_unknown_document(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate document of unknown type using basic checks."""
        issues = []
        warnings = []
        
        # Basic completeness check
        if len(text) < 100:
            issues.append("Document appears to be very short")
        
        # Check for common format issues
        format_issues = self._check_common_formats(text)
        issues.extend(format_issues)
        
        # Basic date consistency
        date_issues = self._check_date_consistency(text, entities)
        issues.extend(date_issues)
        
        # Calculate basic score
        issue_penalty = len(issues) * 0.15
        score = max(0.5 - issue_penalty, 0.0)  # Start with medium score for unknown
        
        return {
            "success": True,
            "document_type": "unknown",
            "score": score,
            "is_valid": score >= 0.4,  # Lower threshold for unknown documents
            "issues": issues,
            "warnings": warnings,
            "red_flags": [],
            "validation_components": {
                "basic_validation": {
                    "score": score,
                    "issues": issues,
                }
            }
        }
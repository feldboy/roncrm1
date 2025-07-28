"""Document classification utilities for intelligent document type detection."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger

logger = get_logger(__name__)


class DocumentClassifier:
    """
    Document classification service for intelligent document type detection.
    
    Uses both rule-based classification and AI-powered classification
    to accurately determine document types.
    """
    
    def __init__(self, ai_client: Optional[OpenAIClient] = None):
        """
        Initialize document classifier.
        
        Args:
            ai_client: OpenAI client for AI-powered classification.
        """
        self.ai_client = ai_client or OpenAIClient()
        
        # Document type keywords and patterns
        self.classification_rules = {
            "medical_record": {
                "keywords": [
                    "patient", "diagnosis", "treatment", "physician", "doctor",
                    "hospital", "medical", "prescription", "medication", "surgery",
                    "clinic", "healthcare", "radiology", "laboratory", "pathology",
                    "vital signs", "blood pressure", "heart rate", "temperature",
                    "chief complaint", "history of present illness", "assessment",
                    "plan", "progress note", "discharge summary", "operative report"
                ],
                "headers": [
                    "medical record", "patient information", "clinical notes",
                    "physician notes", "nursing notes", "discharge summary",
                    "operative report", "laboratory results", "radiology report",
                    "pathology report", "emergency department", "admission note"
                ],
                "patterns": [
                    r'\b(?:DOB|Date of Birth):\s*\d{1,2}[/-]\d{1,2}[/-]\d{4}',
                    r'\bMRN[\s#:]*\d+',
                    r'\b(?:Chief Complaint|CC):\s*.+',
                    r'\b(?:Diagnosis|Dx):\s*.+',
                    r'\bDr\.?\s+[A-Z][a-z]+',
                ],
                "weight": 1.0
            },
            "police_report": {
                "keywords": [
                    "police", "officer", "badge", "incident", "report", "citation",
                    "arrest", "violation", "traffic", "accident", "collision",
                    "witness", "statement", "evidence", "investigation", "suspect",
                    "victim", "complaint", "dispatch", "unit", "patrol", "precinct"
                ],
                "headers": [
                    "police report", "incident report", "traffic citation",
                    "arrest report", "accident report", "complaint report",
                    "investigation report", "witness statement"
                ],
                "patterns": [
                    r'\b(?:Case|Report|Incident)[\s#:]*\d+',
                    r'\bOfficer\s+[A-Z][a-z]+',
                    r'\bBadge[\s#:]*\d+',
                    r'\b(?:Date|Time) of Incident:',
                    r'\bLocation of Incident:',
                ],
                "weight": 1.0
            },
            "legal_contract": {
                "keywords": [
                    "agreement", "contract", "party", "parties", "whereas",
                    "therefore", "consideration", "terms", "conditions", "breach",
                    "liability", "indemnify", "jurisdiction", "governing law",
                    "dispute resolution", "arbitration", "attorney", "counsel",
                    "executed", "effective date", "termination", "amendment"
                ],
                "headers": [
                    "service agreement", "employment contract", "lease agreement",
                    "purchase agreement", "settlement agreement", "retainer agreement",
                    "non-disclosure agreement", "licensing agreement"
                ],
                "patterns": [
                    r'\bWHEREAS,?\s+.+',
                    r'\bNOW,?\s+THEREFORE,?\s+.+',
                    r'\bParty of the (?:First|Second) Part',
                    r'\bIN WITNESS WHEREOF',
                    r'\bExecuted this \d+\w{0,2} day of',
                ],
                "weight": 1.0
            },
            "insurance_document": {
                "keywords": [
                    "policy", "coverage", "premium", "deductible", "claim",
                    "insured", "insurer", "beneficiary", "liability", "limits",
                    "effective date", "expiration", "renewal", "underwriter",
                    "adjuster", "settlement", "damages", "exclusions", "riders"
                ],
                "headers": [
                    "insurance policy", "certificate of insurance", "claims form",
                    "coverage verification", "policy declaration", "insurance card"
                ],
                "patterns": [
                    r'\bPolicy[\s#:]*[A-Z0-9]+',
                    r'\bClaim[\s#:]*[A-Z0-9]+',
                    r'\bCoverage[\s:]*\$[\d,]+',
                    r'\bDeductible[\s:]*\$[\d,]+',
                    r'\bEffective Date:',
                ],
                "weight": 1.0
            },
            "financial_document": {
                "keywords": [
                    "income", "salary", "wages", "earnings", "tax", "return",
                    "statement", "bank", "account", "balance", "deposit",
                    "withdrawal", "credit", "debit", "loan", "mortgage",
                    "payment", "receipt", "invoice", "billing"
                ],
                "headers": [
                    "bank statement", "pay stub", "tax return", "financial statement",
                    "income statement", "credit report", "loan documents"
                ],
                "patterns": [
                    r'\$[\d,]+\.?\d{0,2}',
                    r'\bAccount[\s#:]*\d+',
                    r'\bSSN[\s#:]*\d{3}-\d{2}-\d{4}',
                    r'\bRouting[\s#:]*\d{9}',
                    r'\bGross Pay:|Net Pay:',
                ],
                "weight": 1.0
            },
            "employment_document": {
                "keywords": [
                    "employee", "employer", "employment", "job", "position",
                    "salary", "benefits", "vacation", "sick leave", "termination",
                    "resignation", "performance", "evaluation", "supervisor",
                    "department", "human resources", "payroll", "schedule"
                ],
                "headers": [
                    "employment verification", "job description", "offer letter",
                    "employment contract", "performance review", "termination letter"
                ],
                "patterns": [
                    r'\bEmployee[\s#:]*\d+',
                    r'\bStart Date:|Hire Date:',
                    r'\bJob Title:|Position:',
                    r'\bSupervisor:|Manager:',
                    r'\bDepartment:',
                ],
                "weight": 1.0
            },
            "correspondence": {
                "keywords": [
                    "dear", "sincerely", "regards", "letter", "email", "memo",
                    "correspondence", "communication", "message", "reply",
                    "response", "follow up", "regarding", "concerning", "re:"
                ],
                "headers": [
                    "letter", "email", "memorandum", "correspondence", "communication"
                ],
                "patterns": [
                    r'\bDear\s+[A-Z][a-z]+',
                    r'\bSincerely,?\s*\n',
                    r'\bBest regards,?\s*\n',
                    r'\bFrom:\s*.+',
                    r'\bTo:\s*.+',
                    r'\bSubject:\s*.+',
                ],
                "weight": 0.8
            },
            "identification_document": {
                "keywords": [
                    "license", "identification", "passport", "id", "driver",
                    "social security", "birth certificate", "citizenship",
                    "green card", "visa", "permit", "registration"
                ],
                "headers": [
                    "driver license", "identification card", "passport", "birth certificate",
                    "social security card", "green card", "visa"
                ],
                "patterns": [
                    r'\bLicense[\s#:]*[A-Z0-9]+',
                    r'\bDOB[\s:]*\d{1,2}[/-]\d{1,2}[/-]\d{4}',
                    r'\bSSN[\s:]*\d{3}-\d{2}-\d{4}',
                    r'\bState of [A-Z][a-z]+',
                    r'\bExpires?:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{4}',
                ],
                "weight": 1.0
            },
        }
        
        # File extension hints
        self.extension_hints = {
            ".pdf": ["medical_record", "legal_contract", "insurance_document"],
            ".doc": ["correspondence", "legal_contract", "employment_document"],
            ".docx": ["correspondence", "legal_contract", "employment_document"],
            ".txt": ["correspondence", "police_report"],
            ".jpg": ["identification_document", "medical_record"],
            ".png": ["identification_document", "financial_document"],
        }
    
    async def classify_document(
        self,
        text: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify document type using multiple approaches.
        
        Args:
            text: Extracted text from document.
            file_path: Optional file path for additional context.
            
        Returns:
            dict: Classification result with type and confidence.
        """
        if not text:
            return {
                "success": False,
                "error": "No text provided for classification",
                "document_type": "unknown",
                "confidence": 0.0,
            }
        
        try:
            # Rule-based classification
            rule_results = self._classify_by_rules(text, file_path)
            
            # AI-powered classification
            ai_results = await self._classify_with_ai(text)
            
            # Combine results
            final_result = self._combine_classification_results(
                rule_results, ai_results
            )
            
            return {
                "success": True,
                "document_type": final_result["document_type"],
                "confidence": final_result["confidence"],
                "rule_based_result": rule_results,
                "ai_based_result": ai_results,
                "classification_details": final_result["details"],
            }
            
        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_type": "unknown",
                "confidence": 0.0,
            }
    
    def _classify_by_rules(
        self,
        text: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Classify document using rule-based approach."""
        text_lower = text.lower()
        scores = {}
        
        # Score each document type
        for doc_type, rules in self.classification_rules.items():
            score = 0.0
            matched_features = {
                "keywords": [],
                "headers": [],
                "patterns": [],
            }
            
            # Check keywords
            for keyword in rules["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1
                    matched_features["keywords"].append(keyword)
            
            # Check headers
            for header in rules["headers"]:
                if header.lower() in text_lower:
                    score += 3  # Headers are more important
                    matched_features["headers"].append(header)
            
            # Check patterns
            for pattern in rules["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 2  # Patterns are moderately important
                    matched_features["patterns"].append(pattern)
            
            # Apply document type weight
            weighted_score = score * rules["weight"]
            
            if weighted_score > 0:
                scores[doc_type] = {
                    "score": weighted_score,
                    "matched_features": matched_features,
                }
        
        # Add file extension hints
        if file_path:
            extension = Path(file_path).suffix.lower()
            hint_types = self.extension_hints.get(extension, [])
            
            for doc_type in hint_types:
                if doc_type in scores:
                    scores[doc_type]["score"] += 1  # Small bonus for extension match
                else:
                    scores[doc_type] = {
                        "score": 0.5,  # Small score for extension hint only
                        "matched_features": {"extension_hint": True},
                    }
        
        # Determine best match
        if scores:
            best_type = max(scores.keys(), key=lambda x: scores[x]["score"])
            total_score = sum(s["score"] for s in scores.values())
            confidence = min(scores[best_type]["score"] / total_score, 1.0) if total_score > 0 else 0.0
            
            return {
                "document_type": best_type,
                "confidence": confidence,
                "all_scores": scores,
                "method": "rule_based",
            }
        else:
            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "all_scores": {},
                "method": "rule_based",
            }
    
    async def _classify_with_ai(self, text: str) -> Dict[str, Any]:
        """Classify document using AI."""
        try:
            # Limit text length to avoid token limits
            text_sample = text[:2000] if len(text) > 2000 else text
            
            document_types = list(self.classification_rules.keys())
            types_list = ", ".join(document_types)
            
            prompt = f"""
            Classify this document into one of these types: {types_list}
            
            Document text:
            {text_sample}
            
            Based on the content, terminology, and structure, what type of document is this?
            
            Respond with just the document type and a confidence score (0-100).
            Format: "document_type: confidence_score"
            
            For example: "medical_record: 85"
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=50,
                temperature=0.1
            )
            
            # Parse response
            response = response.strip()
            if ":" in response:
                parts = response.split(":")
                doc_type = parts[0].strip()
                try:
                    confidence = float(parts[1].strip()) / 100.0
                except (ValueError, IndexError):
                    confidence = 0.5  # Default confidence
                
                # Validate document type
                if doc_type in document_types:
                    return {
                        "document_type": doc_type,
                        "confidence": confidence,
                        "method": "ai_based",
                        "raw_response": response,
                    }
            
            # If parsing fails, return unknown
            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "method": "ai_based",
                "raw_response": response,
                "error": "Failed to parse AI response",
            }
            
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "method": "ai_based",
                "error": str(e),
            }
    
    def _combine_classification_results(
        self,
        rule_results: Dict[str, Any],
        ai_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine rule-based and AI classification results."""
        # Weights for different methods
        rule_weight = 0.6
        ai_weight = 0.4
        
        rule_type = rule_results.get("document_type", "unknown")
        rule_confidence = rule_results.get("confidence", 0.0)
        
        ai_type = ai_results.get("document_type", "unknown")
        ai_confidence = ai_results.get("confidence", 0.0)
        
        # If both methods agree
        if rule_type == ai_type and rule_type != "unknown":
            combined_confidence = (
                rule_confidence * rule_weight + 
                ai_confidence * ai_weight
            )
            return {
                "document_type": rule_type,
                "confidence": min(combined_confidence * 1.2, 1.0),  # Boost for agreement
                "details": {
                    "methods_agree": True,
                    "rule_confidence": rule_confidence,
                    "ai_confidence": ai_confidence,
                },
            }
        
        # If methods disagree, use the one with higher weighted confidence
        rule_weighted = rule_confidence * rule_weight
        ai_weighted = ai_confidence * ai_weight
        
        if rule_weighted > ai_weighted:
            final_type = rule_type
            final_confidence = rule_confidence * 0.8  # Penalty for disagreement
        else:
            final_type = ai_type
            final_confidence = ai_confidence * 0.8  # Penalty for disagreement
        
        # If both are unknown or very low confidence, default to unknown
        if final_confidence < 0.3:
            final_type = "unknown"
            final_confidence = 0.0
        
        return {
            "document_type": final_type,
            "confidence": final_confidence,
            "details": {
                "methods_agree": False,
                "rule_result": {"type": rule_type, "confidence": rule_confidence},
                "ai_result": {"type": ai_type, "confidence": ai_confidence},
                "selected_method": "rule_based" if rule_weighted > ai_weighted else "ai_based",
            },
        }
    
    def get_document_type_info(self, document_type: str) -> Dict[str, Any]:
        """Get information about a document type."""
        if document_type in self.classification_rules:
            rules = self.classification_rules[document_type]
            return {
                "document_type": document_type,
                "keywords": rules["keywords"],
                "typical_headers": rules["headers"],
                "identifying_patterns": rules["patterns"],
                "classification_weight": rules["weight"],
            }
        else:
            return {
                "document_type": document_type,
                "error": "Unknown document type",
            }
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported document types."""
        return list(self.classification_rules.keys())
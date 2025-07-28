"""Document text extraction and entity extraction utilities."""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from ...services.ai.openai_client import OpenAIClient
from ...utils.logging import get_logger

logger = get_logger(__name__)


class DocumentExtractor:
    """
    Document text extraction and entity extraction service.
    
    Handles OCR, text extraction from various formats,
    and AI-powered entity extraction.
    """
    
    def __init__(self, ai_client: Optional[OpenAIClient] = None):
        """
        Initialize document extractor.
        
        Args:
            ai_client: OpenAI client for AI-powered extraction.
        """
        self.ai_client = ai_client or OpenAIClient()
        
        # Entity patterns for different document types
        self.entity_patterns = {
            "medical_record": {
                "dates": [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
                    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                    r'\b[A-Za-z]+ \d{1,2}, \d{4}\b',
                ],
                "medications": [
                    r'\b[A-Z][a-z]+(?:in|ol|ate|ide|ine|one)\b',
                    r'\bmg\b|\bml\b|\btablets?\b|\bcapsules?\b',
                ],
                "medical_terms": [
                    r'\b(?:diagnosis|diagnosed|condition|injury|fracture|surgery|treatment)\b',
                    r'\b(?:pain|swelling|inflammation|infection|bleeding)\b',
                ],
                "providers": [
                    r'\bDr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
                    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s+M\.?D\.?\b',
                ],
            },
            "police_report": {
                "incident_numbers": [
                    r'\b(?:Case|Report|Incident)[\s#:]*(\d{4,})\b',
                    r'\b\d{4}-\d{6,}\b',
                ],
                "locations": [
                    r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:St|Ave|Rd|Blvd|Dr|Ln)\b',
                    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s+[A-Z]{2}\b',
                ],
                "vehicles": [
                    r'\b\d{4}\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                    r'\b(?:License|Plate)[\s#:]*([A-Z0-9]{3,8})\b',
                ],
                "officers": [
                    r'\bOfficer\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
                    r'\bBadge[\s#:]*(\d+)\b',
                ],
            },
            "legal_contract": {
                "parties": [
                    r'\b(?:Party|Plaintiff|Defendant|Client)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                ],
                "amounts": [
                    r'\$[\d,]+(?:\.\d{2})?\b',
                    r'\b(?:dollars?|amount|sum)[\s:]+\$?([\d,]+(?:\.\d{2})?)\b',
                ],
                "dates": [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
                    r'\b[A-Za-z]+ \d{1,2}, \d{4}\b',
                ],
            },
            "insurance_document": {
                "policy_numbers": [
                    r'\b(?:Policy|Account)[\s#:]*([A-Z0-9]{6,})\b',
                ],
                "claim_numbers": [
                    r'\b(?:Claim)[\s#:]*([A-Z0-9]{6,})\b',
                ],
                "coverage_amounts": [
                    r'\$[\d,]+(?:\.\d{2})?\s*(?:coverage|limit|deductible)\b',
                ],
            },
        }
    
    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from document using appropriate method.
        
        Args:
            file_path: Path to the document file.
            
        Returns:
            dict: Extraction result with text and metadata.
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "text": "",
            }
        
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == ".pdf":
                return await self._extract_from_pdf(file_path)
            elif file_extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
                return await self._extract_from_image(file_path)
            elif file_extension in [".txt", ".rtf"]:
                return await self._extract_from_text(file_path)
            elif file_extension in [".doc", ".docx"]:
                return await self._extract_from_word(file_path)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_extension}",
                    "text": "",
                }
                
        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
            }
    
    async def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF file."""
        if not PYMUPDF_AVAILABLE:
            return {
                "success": False,
                "error": "PyMuPDF not available for PDF processing",
                "text": "",
            }
        
        try:
            doc = fitz.open(file_path)
            text_content = []
            metadata = {
                "pages": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "creator": doc.metadata.get("creator", ""),
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # If text extraction fails, try OCR on the page
                if not text.strip():
                    try:
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        
                        if TESSERACT_AVAILABLE:
                            from PIL import Image
                            import io
                            
                            image = Image.open(io.BytesIO(img_data))
                            text = pytesseract.image_to_string(image)
                    except Exception as ocr_e:
                        logger.warning(f"OCR failed for page {page_num}: {ocr_e}")
                        text = ""
                
                text_content.append(text)
            
            doc.close()
            
            full_text = "\n".join(text_content)
            confidence = self._calculate_text_confidence(full_text)
            
            return {
                "success": True,
                "text": full_text,
                "pages": len(text_content),
                "metadata": metadata,
                "confidence": confidence,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF extraction failed: {str(e)}",
                "text": "",
            }
    
    async def _extract_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image using OCR."""
        if not TESSERACT_AVAILABLE:
            return {
                "success": False,
                "error": "Tesseract not available for OCR",
                "text": "",
            }
        
        try:
            image = Image.open(file_path)
            
            # Get image metadata
            metadata = {
                "size": image.size,
                "format": image.format,
                "mode": image.mode,
            }
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Get OCR confidence data
            confidence_data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [
                int(conf) for conf in confidence_data["conf"]
                if int(conf) > 0
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "success": True,
                "text": text,
                "pages": 1,
                "metadata": metadata,
                "confidence": avg_confidence / 100.0,  # Convert to 0-1 scale
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Image OCR failed: {str(e)}",
                "text": "",
            }
    
    async def _extract_from_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Get file metadata
            file_stat = os.stat(file_path)
            metadata = {
                "size": file_stat.st_size,
                "encoding": "utf-8",
                "lines": text.count('\n') + 1,
            }
            
            return {
                "success": True,
                "text": text,
                "pages": 1,
                "metadata": metadata,
                "confidence": 1.0,  # Perfect confidence for text files
            }
            
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    
                    return {
                        "success": True,
                        "text": text,
                        "pages": 1,
                        "metadata": {"encoding": encoding},
                        "confidence": 0.9,  # Slightly lower confidence for encoding issues
                    }
                except UnicodeDecodeError:
                    continue
            
            return {
                "success": False,
                "error": "Could not decode text file with any encoding",
                "text": "",
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Text extraction failed: {str(e)}",
                "text": "",
            }
    
    async def _extract_from_word(self, file_path: str) -> Dict[str, Any]:
        """Extract text from Word document."""
        try:
            # Try to use python-docx if available
            try:
                from docx import Document
                
                doc = Document(file_path)
                text_content = []
                
                for paragraph in doc.paragraphs:
                    text_content.append(paragraph.text)
                
                full_text = "\n".join(text_content)
                
                return {
                    "success": True,
                    "text": full_text,
                    "pages": 1,
                    "metadata": {"paragraphs": len(text_content)},
                    "confidence": 1.0,
                }
                
            except ImportError:
                # Fallback: convert to text using other methods
                return {
                    "success": False,
                    "error": "python-docx not available for Word document processing",
                    "text": "",
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Word document extraction failed: {str(e)}",
                "text": "",
            }
    
    async def extract_entities(
        self,
        text: str,
        document_type: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Extract entities from text using patterns and AI.
        
        Args:
            text: Text to extract entities from.
            document_type: Type of document for targeted extraction.
            
        Returns:
            dict: Extracted entities and metadata.
        """
        if not text:
            return {
                "success": False,
                "error": "No text provided",
                "entities": {},
            }
        
        try:
            # Pattern-based extraction
            pattern_entities = self._extract_entities_by_patterns(text, document_type)
            
            # AI-powered extraction
            ai_entities = await self._extract_entities_with_ai(text, document_type)
            
            # Combine and deduplicate entities
            combined_entities = self._merge_entities(pattern_entities, ai_entities)
            
            return {
                "success": True,
                "entities": combined_entities,
                "extraction_methods": ["pattern_matching", "ai_extraction"],
                "document_type": document_type,
            }
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "entities": {},
            }
    
    def _extract_entities_by_patterns(
        self,
        text: str,
        document_type: str
    ) -> Dict[str, List[str]]:
        """Extract entities using predefined patterns."""
        entities = {}
        
        # Get patterns for document type
        patterns = self.entity_patterns.get(document_type, {})
        
        # Add common patterns for all document types
        common_patterns = {
            "phone_numbers": [r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'],
            "emails": [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            "ssn": [r'\b\d{3}-\d{2}-\d{4}\b'],
            "zip_codes": [r'\b\d{5}(?:-\d{4})?\b'],
        }
        
        patterns.update(common_patterns)
        
        # Extract entities for each pattern type
        for entity_type, pattern_list in patterns.items():
            matches = []
            for pattern in pattern_list:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            
            # Remove duplicates and clean matches
            unique_matches = list(set(match.strip() for match in matches if match.strip()))
            if unique_matches:
                entities[entity_type] = unique_matches
        
        return entities
    
    async def _extract_entities_with_ai(
        self,
        text: str,
        document_type: str
    ) -> Dict[str, List[str]]:
        """Extract entities using AI."""
        try:
            prompt = f"""
            Extract key entities from this {document_type} document:
            
            Text:
            {text[:2000]}  # Limit text to avoid token limits
            
            Extract and return in JSON format:
            {{
                "people": ["list of person names"],
                "organizations": ["list of organization names"],
                "locations": ["list of locations"],
                "dates": ["list of dates"],
                "amounts": ["list of monetary amounts"],
                "case_numbers": ["list of case/reference numbers"],
                "key_terms": ["list of important terms specific to document type"]
            }}
            
            Only return the JSON, no other text.
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=400,
                temperature=0.1
            )
            
            # Parse JSON response
            try:
                entities = json.loads(response.strip())
                return entities
            except json.JSONDecodeError:
                # If JSON parsing fails, return empty dict
                logger.warning("AI entity extraction returned invalid JSON")
                return {}
                
        except Exception as e:
            logger.error(f"AI entity extraction failed: {e}")
            return {}
    
    def _merge_entities(
        self,
        pattern_entities: Dict[str, List[str]],
        ai_entities: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Merge entities from different extraction methods."""
        merged = {}
        
        # Start with pattern entities
        for entity_type, values in pattern_entities.items():
            merged[entity_type] = values.copy()
        
        # Add AI entities
        for entity_type, values in ai_entities.items():
            if entity_type in merged:
                # Merge and deduplicate
                combined = merged[entity_type] + values
                merged[entity_type] = list(set(combined))
            else:
                merged[entity_type] = values
        
        # Clean up empty entity types
        return {k: v for k, v in merged.items() if v}
    
    def _calculate_text_confidence(self, text: str) -> float:
        """Calculate confidence score for extracted text."""
        if not text:
            return 0.0
        
        # Basic heuristics for text quality
        total_chars = len(text)
        alpha_chars = sum(1 for c in text if c.isalpha())
        digit_chars = sum(1 for c in text if c.isdigit())
        space_chars = sum(1 for c in text if c.isspace())
        
        # Calculate ratios
        alpha_ratio = alpha_chars / total_chars if total_chars > 0 else 0
        readable_ratio = (alpha_chars + digit_chars + space_chars) / total_chars if total_chars > 0 else 0
        
        # Penalize excessive special characters
        special_chars = total_chars - alpha_chars - digit_chars - space_chars
        special_ratio = special_chars / total_chars if total_chars > 0 else 0
        
        # Calculate confidence (0.0 to 1.0)
        confidence = (
            alpha_ratio * 0.5 +  # 50% weight for alphabetic content
            readable_ratio * 0.3 +  # 30% weight for overall readability
            max(0, 1 - special_ratio * 2) * 0.2  # 20% penalty for special chars
        )
        
        return min(max(confidence, 0.0), 1.0)
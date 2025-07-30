"""OpenAI API client service."""

import asyncio
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI
from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass

class OpenAIClient:
    """OpenAI API client with async support and error handling."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0,
            max_retries=3
        )
        self.default_model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> str:
        """Generate chat completion with error handling."""
        try:
            model = model or self.default_model
            max_tokens = max_tokens or self.max_tokens
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            content = response.choices[0].message.content
            logger.info(
                "OpenAI chat completion successful",
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else None
            )
            return content
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {e}")
            raise
    
    async def analyze_document(self, text: str, document_type: str = "legal") -> Dict[str, Any]:
        """Analyze document content using AI."""
        try:
            prompt = f"""
            Analyze the following {document_type} document and extract key information:
            
            Document Text:
            {text[:4000]}  # Limit to avoid token limits
            
            Please provide:
            1. Document classification
            2. Key entities (names, dates, amounts, addresses)
            3. Summary of main points
            4. Confidence score (0-100)
            5. Any legal or medical terms identified
            
            Respond in JSON format with the following structure:
            {{
                "classification": "document type",
                "entities": [
                    {{"text": "entity", "type": "person|date|money|location|organization", "confidence": 0.95}}
                ],
                "summary": "brief summary",
                "confidence_score": 85,
                "legal_terms": ["term1", "term2"],
                "medical_terms": ["term1", "term2"]
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are an expert legal document analyzer."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.1)
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response from OpenAI")
                return {
                    "classification": "unknown",
                    "entities": [],
                    "summary": response[:200] + "..." if len(response) > 200 else response,
                    "confidence_score": 50,
                    "legal_terms": [],
                    "medical_terms": []
                }
                
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            raise
    
    async def assess_case_risk(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for a legal case using AI."""
        try:
            prompt = f"""
            Analyze the following legal case data and provide a comprehensive risk assessment:
            
            Case Information:
            - Case Type: {case_data.get('case_type', 'Unknown')}
            - Incident Date: {case_data.get('incident_date', 'Unknown')}
            - Description: {case_data.get('description', 'No description')}
            - Medical Treatment: {case_data.get('medical_treatment', 'Unknown')}
            - Insurance Coverage: {case_data.get('insurance_coverage', 'Unknown')}
            - Prior Claims: {case_data.get('prior_claims', 'Unknown')}
            - Employment Status: {case_data.get('employment_status', 'Unknown')}
            
            Provide risk assessment covering:
            1. Overall risk score (0-100, where 100 is lowest risk)
            2. Financial risk factors
            3. Legal risk factors
            4. Medical risk factors
            5. Behavioral risk factors
            6. Specific concerns or red flags
            7. Recommendations
            
            Respond in JSON format:
            {{
                "overall_score": 75,
                "financial_risk": 85,
                "legal_risk": 70,
                "medical_risk": 80,
                "behavioral_risk": 90,
                "risk_factors": [
                    {{"factor": "factor name", "severity": "low|medium|high", "description": "explanation"}}
                ],
                "red_flags": ["flag1", "flag2"],
                "recommendations": ["rec1", "rec2"],
                "confidence": 85
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are an expert risk analyst for pre-settlement funding cases."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.2)
            
            import json
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse risk assessment JSON response")
                return {
                    "overall_score": 50,
                    "financial_risk": 50,
                    "legal_risk": 50,
                    "medical_risk": 50,
                    "behavioral_risk": 50,
                    "risk_factors": [],
                    "red_flags": [],
                    "recommendations": [],
                    "confidence": 30
                }
                
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            raise
    
    async def generate_communication_content(
        self,
        template_type: str,
        context: Dict[str, Any],
        communication_type: str = "email"
    ) -> Dict[str, str]:
        """Generate personalized communication content."""
        try:
            if communication_type == "email":
                prompt = f"""
                Generate a professional email for {template_type} communication.
                
                Context:
                - Recipient Name: {context.get('recipient_name', 'Client')}
                - Case Type: {context.get('case_type', 'legal matter')}
                - Company: {context.get('company_name', 'Legal Funding Company')}
                
                Generate subject line and body that is:
                - Professional and empathetic
                - Clear and concise
                - Legally appropriate
                - Personalized to the context
                
                Respond in JSON format:
                {{
                    "subject": "Email subject line",
                    "content": "Email body content"
                }}
                """
            else:  # SMS
                prompt = f"""
                Generate a brief SMS message for {template_type} communication.
                
                Context:
                - Recipient Name: {context.get('recipient_name', 'Client')}
                - Case Type: {context.get('case_type', 'legal matter')}
                
                Generate SMS content that is:
                - Under 160 characters
                - Professional but friendly
                - Clear call to action if needed
                - TCPA compliant
                
                Respond in JSON format:
                {{
                    "content": "SMS message content"
                }}
                """
            
            messages = [
                {"role": "system", "content": "You are a professional legal communication specialist."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, temperature=0.4)
            
            import json
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse communication content JSON response")
                if communication_type == "email":
                    return {
                        "subject": f"Regarding your {context.get('case_type', 'case')}",
                        "content": f"Dear {context.get('recipient_name', 'Client')},\n\nWe hope this message finds you well. We wanted to follow up regarding your case.\n\nBest regards,\n{context.get('company_name', 'Legal Funding Team')}"
                    }
                else:
                    return {
                        "content": f"Hi {context.get('recipient_name', 'Client')}, this is an update on your case. Please call us back."
                    }
                    
        except Exception as e:
            logger.error(f"Communication content generation failed: {e}")
            raise

# Singleton instance
_openai_client = None

def get_openai_client() -> OpenAIClient:
    """Get OpenAI client singleton."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
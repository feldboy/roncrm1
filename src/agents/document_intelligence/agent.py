"""Document Intelligence Agent implementation."""

import asyncio
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database import Document, Plaintiff, Case
from ...services.ai.openai_client import OpenAIClient
from ...services.storage.file_storage import FileStorageService
from ..base.agent import BaseAgent, AgentTask, AgentResponse
from ..base.communication import agent_communication
from .extraction import DocumentExtractor
from .classification import DocumentClassifier
from .validation import DocumentValidator


class DocumentIntelligenceAgent(BaseAgent):
    """
    Document Intelligence Agent for AI-powered document processing.
    
    Handles OCR, document classification, data extraction,
    validation, and intelligent document analysis.
    """
    
    def __init__(self, config):
        """Initialize the Document Intelligence Agent."""
        super().__init__(config)
        
        # Initialize AI client and document processing components
        self.ai_client = OpenAIClient()
        self.extractor = DocumentExtractor(self.ai_client)
        self.classifier = DocumentClassifier(self.ai_client)
        self.validator = DocumentValidator(self.ai_client)
        self.file_storage = FileStorageService()
        
        # Operation handlers
        self._handlers = {
            "process_document": self._process_document,
            "extract_text": self._extract_text,
            "classify_document": self._classify_document,
            "extract_entities": self._extract_entities,
            "validate_document": self._validate_document,
            "analyze_medical_records": self._analyze_medical_records,
            "analyze_legal_documents": self._analyze_legal_documents,
            "batch_process_documents": self._batch_process_documents,
            "search_documents": self._search_documents,
            "get_document_summary": self._get_document_summary,
        }
        
        # Processing statistics
        self.processing_stats = {
            "total_documents": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_pages_processed": 0,
            "average_processing_time_ms": 0,
            "document_types": {},
            "last_processed": None,
        }
        
        # Supported file types
        self.supported_types = {
            ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif",
            ".doc", ".docx", ".txt", ".rtf"
        }
        
        self.logger.info("Document Intelligence Agent initialized")
    
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
            self.processing_stats["total_documents"] += 1
            self.processing_stats["last_processed"] = datetime.utcnow().isoformat()
            
            if result.get("success", True):
                self.processing_stats["successful_extractions"] += 1
                
                # Track document type
                doc_type = result.get("document_type", "unknown")
                self.processing_stats["document_types"][doc_type] = (
                    self.processing_stats["document_types"].get(doc_type, 0) + 1
                )
                
                # Track pages processed
                pages = result.get("pages_processed", 1)
                self.processing_stats["total_pages_processed"] += pages
            else:
                self.processing_stats["failed_extractions"] += 1
            
            # Calculate execution time
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Update average processing time
            total_time = (
                self.processing_stats["average_processing_time_ms"] * 
                (self.processing_stats["total_documents"] - 1) + 
                execution_time
            )
            self.processing_stats["average_processing_time_ms"] = (
                total_time / self.processing_stats["total_documents"]
            )
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=True,
                data=result,
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            self.processing_stats["failed_extractions"] += 1
            
            self.logger.error(
                f"Document processing task failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            return self.create_error_response(task.id, str(e))
    
    async def _process_document(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a document with full AI analysis pipeline.
        
        Args:
            task: Task containing document processing parameters.
            
        Returns:
            dict: Comprehensive document processing result.
        """
        document_id = task.payload.get("document_id")
        file_path = task.payload.get("file_path")
        plaintiff_id = task.payload.get("plaintiff_id")
        processing_options = task.payload.get("options", {})
        
        if not document_id and not file_path:
            raise ValueError("Either document_id or file_path must be provided")
        
        self.logger.info(
            "Starting comprehensive document processing",
            document_id=document_id,
            file_path=file_path,
            plaintiff_id=plaintiff_id,
        )
        
        # Get or create document record
        if document_id:
            document = await self._get_document(UUID(document_id))
            if not document:
                raise ValueError(f"Document {document_id} not found")
            file_path = await self.file_storage.get_file_path(document.file_url)
        else:
            # Create new document record
            document = await self._create_document_record(
                file_path, plaintiff_id, processing_options
            )
        
        # Validate file type
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        processing_result = {
            "document_id": str(document.id),
            "file_path": file_path,
            "success": False,
            "processing_stages": {},
            "extracted_data": {},
            "validation_results": {},
            "errors": [],
            "warnings": [],
        }
        
        try:
            # Stage 1: Text Extraction (OCR)
            self.logger.info("Starting text extraction", document_id=str(document.id))
            extraction_result = await self.extractor.extract_text(file_path)
            
            processing_result["processing_stages"]["text_extraction"] = {
                "success": extraction_result["success"],
                "pages_processed": extraction_result.get("pages", 1),
                "confidence_score": extraction_result.get("confidence", 0.0),
            }
            
            if not extraction_result["success"]:
                processing_result["errors"].append("Text extraction failed")
                return processing_result
            
            extracted_text = extraction_result["text"]
            
            # Stage 2: Document Classification
            self.logger.info("Starting document classification", document_id=str(document.id))
            classification_result = await self.classifier.classify_document(
                extracted_text, file_path
            )
            
            processing_result["processing_stages"]["classification"] = {
                "success": classification_result["success"],
                "document_type": classification_result.get("document_type"),
                "confidence": classification_result.get("confidence", 0.0),
            }
            
            document_type = classification_result.get("document_type", "unknown")
            
            # Stage 3: Entity Extraction
            self.logger.info("Starting entity extraction", document_id=str(document.id))
            entity_result = await self.extractor.extract_entities(
                extracted_text, document_type
            )
            
            processing_result["processing_stages"]["entity_extraction"] = {
                "success": entity_result["success"],
                "entities_found": len(entity_result.get("entities", {})),
            }
            
            # Stage 4: Document Validation
            self.logger.info("Starting document validation", document_id=str(document.id))
            validation_result = await self.validator.validate_document(
                extracted_text, document_type, entity_result.get("entities", {})
            )
            
            processing_result["processing_stages"]["validation"] = {
                "success": validation_result["success"],
                "is_valid": validation_result.get("is_valid", False),
                "validation_score": validation_result.get("score", 0.0),
            }
            
            # Stage 5: AI Analysis (document-type specific)
            analysis_result = await self._perform_ai_analysis(
                extracted_text, document_type, entity_result.get("entities", {})
            )
            
            processing_result["processing_stages"]["ai_analysis"] = {
                "success": analysis_result["success"],
                "insights_generated": len(analysis_result.get("insights", [])),
            }
            
            # Compile final results
            processing_result["extracted_data"] = {
                "text": extracted_text,
                "document_type": document_type,
                "entities": entity_result.get("entities", {}),
                "metadata": extraction_result.get("metadata", {}),
                "insights": analysis_result.get("insights", []),
                "summary": analysis_result.get("summary", ""),
            }
            
            processing_result["validation_results"] = validation_result
            processing_result["success"] = True
            
            # Update document record with results
            await self._update_document_with_results(document, processing_result)
            
            # Publish document processed event
            await agent_communication.publish(
                sender_id=self.agent_id,
                event_type="document_processed",
                payload={
                    "document_id": str(document.id),
                    "document_type": document_type,
                    "plaintiff_id": str(document.plaintiff_id) if document.plaintiff_id else None,
                    "processing_success": True,
                    "entities_found": len(entity_result.get("entities", {})),
                    "validation_passed": validation_result.get("is_valid", False),
                }
            )
            
        except Exception as e:
            self.logger.error(
                f"Document processing failed: {e}",
                document_id=str(document.id),
            )
            processing_result["errors"].append(str(e))
            processing_result["success"] = False
        
        return processing_result
    
    async def _extract_text(self, task: AgentTask) -> Dict[str, Any]:
        """Extract text from document using OCR."""
        file_path = task.payload.get("file_path")
        if not file_path:
            raise ValueError("Missing file_path in task payload")
        
        result = await self.extractor.extract_text(file_path)
        return result
    
    async def _classify_document(self, task: AgentTask) -> Dict[str, Any]:
        """Classify document type using AI."""
        text = task.payload.get("text")
        file_path = task.payload.get("file_path")
        
        if not text and not file_path:
            raise ValueError("Either text or file_path must be provided")
        
        if not text:
            extraction_result = await self.extractor.extract_text(file_path)
            text = extraction_result.get("text", "")
        
        result = await self.classifier.classify_document(text, file_path)
        return result
    
    async def _extract_entities(self, task: AgentTask) -> Dict[str, Any]:
        """Extract entities from document text."""
        text = task.payload.get("text")
        document_type = task.payload.get("document_type", "unknown")
        
        if not text:
            raise ValueError("Missing text in task payload")
        
        result = await self.extractor.extract_entities(text, document_type)
        return result
    
    async def _validate_document(self, task: AgentTask) -> Dict[str, Any]:
        """Validate document content and structure."""
        text = task.payload.get("text")
        document_type = task.payload.get("document_type", "unknown")
        entities = task.payload.get("entities", {})
        
        if not text:
            raise ValueError("Missing text in task payload")
        
        result = await self.validator.validate_document(text, document_type, entities)
        return result
    
    async def _analyze_medical_records(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze medical records for case-relevant information."""
        document_id = task.payload.get("document_id")
        
        if not document_id:
            raise ValueError("Missing document_id in task payload")
        
        document = await self._get_document(UUID(document_id))
        if not document or document.document_type != "medical_record":
            raise ValueError("Document is not a medical record")
        
        # Perform specialized medical record analysis
        analysis_result = await self._perform_medical_analysis(document)
        return analysis_result
    
    async def _analyze_legal_documents(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze legal documents for case-relevant information."""
        document_id = task.payload.get("document_id")
        
        if not document_id:
            raise ValueError("Missing document_id in task payload")
        
        document = await self._get_document(UUID(document_id))
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Perform specialized legal document analysis
        analysis_result = await self._perform_legal_analysis(document)
        return analysis_result
    
    async def _batch_process_documents(self, task: AgentTask) -> Dict[str, Any]:
        """Process multiple documents in batch."""
        document_ids = task.payload.get("document_ids", [])
        file_paths = task.payload.get("file_paths", [])
        batch_size = task.payload.get("batch_size", 5)
        
        if not document_ids and not file_paths:
            raise ValueError("Either document_ids or file_paths must be provided")
        
        # Convert file_paths to document processing tasks
        all_items = []
        all_items.extend([(doc_id, "document_id") for doc_id in document_ids])
        all_items.extend([(file_path, "file_path") for file_path in file_paths])
        
        results = {
            "total": len(all_items),
            "successful": 0,
            "failed": 0,
            "results": [],
            "errors": [],
        }
        
        # Process in batches
        for i in range(0, len(all_items), batch_size):
            batch = all_items[i:i + batch_size]
            
            # Create processing tasks
            tasks = []
            for item, item_type in batch:
                process_task = AgentTask(
                    agent_type=self.agent_type,
                    operation="process_document",
                    payload={item_type: item}
                )
                tasks.append(self._process_document(process_task))
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append(str(result))
                elif result.get("success"):
                    results["successful"] += 1
                    results["results"].append(result)
                else:
                    results["failed"] += 1
                    results["errors"].extend(result.get("errors", []))
            
            # Small delay between batches
            await asyncio.sleep(2)
        
        return results
    
    async def _search_documents(self, task: AgentTask) -> Dict[str, Any]:
        """Search documents by content."""
        query = task.payload.get("query")
        plaintiff_id = task.payload.get("plaintiff_id")
        document_type = task.payload.get("document_type")
        limit = task.payload.get("limit", 10)
        
        if not query:
            raise ValueError("Missing query in task payload")
        
        # This would implement semantic search using embeddings
        # For now, implementing basic text search
        
        async with get_database_session() as session:
            stmt = select(Document)
            
            if plaintiff_id:
                stmt = stmt.where(Document.plaintiff_id == UUID(plaintiff_id))
            
            if document_type:
                stmt = stmt.where(Document.document_type == document_type)
            
            stmt = stmt.limit(limit)
            
            result = await session.execute(stmt)
            documents = result.scalars().all()
            
            search_results = []
            for doc in documents:
                # Basic text matching in extracted_text
                if doc.extracted_text and query.lower() in doc.extracted_text.lower():
                    search_results.append({
                        "document_id": str(doc.id),
                        "title": doc.title,
                        "document_type": doc.document_type,
                        "confidence": 0.8,  # Placeholder for semantic similarity
                        "snippet": self._extract_snippet(doc.extracted_text, query),
                    })
        
        return {
            "query": query,
            "total_results": len(search_results),
            "results": search_results,
        }
    
    async def _get_document_summary(self, task: AgentTask) -> Dict[str, Any]:
        """Generate AI-powered document summary."""
        document_id = task.payload.get("document_id")
        
        if not document_id:
            raise ValueError("Missing document_id in task payload")
        
        document = await self._get_document(UUID(document_id))
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        if not document.extracted_text:
            raise ValueError("Document has no extracted text")
        
        # Generate AI summary
        prompt = f"""
        Analyze the following document and provide a comprehensive summary:
        
        Document Type: {document.document_type}
        Title: {document.title}
        
        Content:
        {document.extracted_text[:4000]}  # Limit text to avoid token limits
        
        Provide:
        1. A 2-3 sentence executive summary
        2. Key points and findings
        3. Important dates, names, and entities
        4. Any red flags or notable concerns
        5. Relevance to legal case (if applicable)
        """
        
        try:
            summary_response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            return {
                "document_id": str(document.id),
                "summary": summary_response.strip(),
                "generated_at": datetime.utcnow().isoformat(),
                "success": True,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate document summary: {e}")
            return {
                "document_id": str(document.id),
                "error": str(e),
                "success": False,
            }
    
    async def _perform_ai_analysis(
        self,
        text: str,
        document_type: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform AI-powered document analysis."""
        try:
            # Document-type specific analysis
            if document_type == "medical_record":
                analysis = await self._analyze_medical_content(text, entities)
            elif document_type in ["police_report", "accident_report"]:
                analysis = await self._analyze_incident_report(text, entities)
            elif document_type == "legal_contract":
                analysis = await self._analyze_legal_contract(text, entities)
            else:
                analysis = await self._analyze_general_document(text, entities)
            
            return {
                "success": True,
                "insights": analysis.get("insights", []),
                "summary": analysis.get("summary", ""),
                "risk_factors": analysis.get("risk_factors", []),
                "key_findings": analysis.get("key_findings", []),
            }
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": [],
                "summary": "",
            }
    
    async def _analyze_medical_content(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze medical record content."""
        prompt = f"""
        Analyze this medical record for legal case relevance:
        
        Medical Record Content:
        {text[:3000]}
        
        Extracted Entities:
        {json.dumps(entities, indent=2)}
        
        Provide analysis including:
        1. Primary injuries and conditions
        2. Treatment timeline
        3. Causal relationships mentioned
        4. Pain and suffering indicators
        5. Disability or impairment mentions
        6. Pre-existing conditions
        7. Legal case relevance score (1-10)
        """
        
        response = await self.ai_client.generate_completion(
            prompt=prompt,
            max_tokens=400,
            temperature=0.2
        )
        
        return {
            "insights": [response.strip()],
            "summary": "Medical record analysis completed",
            "analysis_type": "medical",
        }
    
    async def _get_document(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        async with get_database_session() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def _create_document_record(
        self,
        file_path: str,
        plaintiff_id: Optional[str],
        options: Dict[str, Any]
    ) -> Document:
        """Create new document record in database."""
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)
        
        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        async with get_database_session() as session:
            document = Document(
                title=file_name,
                file_url=file_path,
                file_name=file_name,
                file_size=file_size,
                file_hash=file_hash,
                plaintiff_id=UUID(plaintiff_id) if plaintiff_id else None,
                processing_status="pending",
            )
            
            session.add(document)
            await session.commit()
            await session.refresh(document)
            
            return document
    
    async def _update_document_with_results(
        self,
        document: Document,
        results: Dict[str, Any]
    ) -> None:
        """Update document record with processing results."""
        async with get_database_session() as session:
            stmt = select(Document).where(Document.id == document.id)
            result = await session.execute(stmt)
            doc = result.scalar_one()
            
            doc.extracted_text = results["extracted_data"].get("text", "")
            doc.document_type = results["extracted_data"].get("document_type", "unknown")
            doc.extracted_entities = results["extracted_data"].get("entities", {})
            doc.processing_status = "completed" if results["success"] else "failed"
            doc.ai_summary = results["extracted_data"].get("summary", "")
            
            await session.commit()
    
    def _extract_snippet(self, text: str, query: str, snippet_length: int = 200) -> str:
        """Extract text snippet around query match."""
        query_lower = query.lower()
        text_lower = text.lower()
        
        index = text_lower.find(query_lower)
        if index == -1:
            return text[:snippet_length]
        
        start = max(0, index - snippet_length // 2)
        end = min(len(text), index + len(query) + snippet_length // 2)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        total = self.processing_stats["total_documents"]
        
        return {
            **self.processing_stats,
            "success_rate": (
                self.processing_stats["successful_extractions"] / total * 100
                if total > 0 else 0
            ),
            "average_pages_per_doc": (
                self.processing_stats["total_pages_processed"] / total
                if total > 0 else 0
            ),
        }
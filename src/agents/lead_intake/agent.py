"""Lead Intake Coordinator Agent implementation."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ...models.database.plaintiff import Plaintiff, CaseType, CaseStatus
from ...models.schemas.plaintiff import PlaintiffCreate
from ...config.database import get_database_session
from ..base.agent import BaseAgent, AgentTask, AgentResponse, AgentType
from ..base.communication import agent_communication
from .parsers import EmailLeadParser, FormLeadParser, GenericLeadParser
from .validators import LeadDataValidator


class LeadIntakeCoordinatorAgent(BaseAgent):
    """
    Lead Intake Coordinator Agent for processing new leads.
    
    Manages complete lead intake process from submission to first contact,
    handling various input formats and routing to appropriate downstream agents.
    """
    
    def __init__(self, config):
        """Initialize the Lead Intake Coordinator Agent."""
        super().__init__(config)
        
        # Initialize parsers
        self.email_parser = EmailLeadParser()
        self.form_parser = FormLeadParser()
        self.generic_parser = GenericLeadParser()
        
        # Initialize validator
        self.validator = LeadDataValidator()
        
        # Operation handlers
        self._handlers = {
            "process_lead_submission": self._process_lead_submission,
            "enrich_lead_data": self._enrich_lead_data,
            "validate_lead": self._validate_lead,
            "create_plaintiff_record": self._create_plaintiff_record,
            "route_to_downstream": self._route_to_downstream,
        }
        
        self.logger.info("Lead Intake Coordinator Agent initialized")
    
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
            self.logger.error(
                f"Task processing failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            return self.create_error_response(task.id, str(e))
    
    async def _process_lead_submission(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a complete lead submission workflow.
        
        Args:
            task: Task containing lead submission data.
            
        Returns:
            dict: Processing result with plaintiff ID and next steps.
        """
        lead_data = task.payload.get("lead_data")
        source = task.payload.get("source", "unknown")
        
        if not lead_data:
            raise ValueError("Missing lead_data in task payload")
        
        self.logger.info(
            "Processing lead submission",
            source=source,
            task_id=task.id,
        )
        
        # Step 1: Parse lead data based on source
        parsed_data = await self._parse_lead_data(lead_data, source)
        
        # Step 2: Validate lead data
        validated_data = await self._validate_lead_data(parsed_data)
        
        # Step 3: Enrich lead data
        enriched_data = await self._enrich_lead_data_internal(validated_data)
        
        # Step 4: Create plaintiff record
        plaintiff = await self._create_plaintiff_record_internal(enriched_data)
        
        # Step 5: Route to downstream agents
        await self._route_to_downstream_agents(plaintiff.id, enriched_data)
        
        # Step 6: Sync with Pipedrive
        await self._sync_with_pipedrive(plaintiff.id, enriched_data)
        
        # Step 7: Trigger initial communication
        await self._trigger_initial_contact(plaintiff.id, enriched_data)
        
        self.logger.info(
            "Lead submission processed successfully",
            plaintiff_id=str(plaintiff.id),
            source=source,
        )
        
        return {
            "plaintiff_id": str(plaintiff.id),
            "status": "processed",
            "source": source,
            "next_steps": [
                "risk_assessment",
                "initial_contact",
                "document_collection",
                "pipedrive_sync"
            ],
            "processing_timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _parse_lead_data(self, lead_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Parse lead data based on source.
        
        Args:
            lead_data: Raw lead data.
            source: Data source type.
            
        Returns:
            dict: Parsed lead data.
        """
        self.logger.debug(f"Parsing lead data from source: {source}")
        
        if source == "email":
            return await self.email_parser.parse(lead_data)
        elif source == "web_form":
            return await self.form_parser.parse(lead_data)
        else:
            return await self.generic_parser.parse(lead_data)
    
    async def _validate_lead_data(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean lead data.
        
        Args:
            lead_data: Parsed lead data.
            
        Returns:
            dict: Validated lead data.
        """
        return await self.validator.validate(lead_data)
    
    async def _enrich_lead_data(self, task: AgentTask) -> Dict[str, Any]:
        """
        Enrich lead data with additional information.
        
        Args:
            task: Task containing lead data to enrich.
            
        Returns:
            dict: Enriched lead data.
        """
        lead_data = task.payload.get("lead_data", {})
        return await self._enrich_lead_data_internal(lead_data)
    
    async def _enrich_lead_data_internal(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to enrich lead data.
        
        Args:
            lead_data: Lead data to enrich.
            
        Returns:
            dict: Enriched lead data.
        """
        enriched = lead_data.copy()
        
        # Add metadata
        enriched["intake_timestamp"] = datetime.utcnow().isoformat()
        enriched["intake_agent_id"] = self.agent_id
        
        # Normalize phone numbers
        if "phone" in enriched and enriched["phone"]:
            enriched["phone"] = self._normalize_phone_number(enriched["phone"])
        
        if "secondary_phone" in enriched and enriched["secondary_phone"]:
            enriched["secondary_phone"] = self._normalize_phone_number(enriched["secondary_phone"])
        
        # Normalize email
        if "email" in enriched and enriched["email"]:
            enriched["email"] = enriched["email"].lower().strip()
        
        # Extract case type if not provided
        if "case_type" not in enriched or not enriched["case_type"]:
            enriched["case_type"] = self._extract_case_type(enriched)
        
        # Set initial case status
        enriched["case_status"] = CaseStatus.INITIAL.value
        
        # Generate lead source details
        enriched["lead_source_details"] = {
            "processed_by": self.agent_id,
            "processing_timestamp": enriched["intake_timestamp"],
            "original_payload_keys": list(lead_data.keys()),
        }
        
        self.logger.debug("Lead data enriched", enriched_fields=list(enriched.keys()))
        
        return enriched
    
    async def _create_plaintiff_record(self, task: AgentTask) -> Dict[str, Any]:
        """
        Create a plaintiff record from validated lead data.
        
        Args:
            task: Task containing validated lead data.
            
        Returns:
            dict: Created plaintiff information.
        """
        lead_data = task.payload.get("lead_data", {})
        plaintiff = await self._create_plaintiff_record_internal(lead_data)
        
        return {
            "plaintiff_id": str(plaintiff.id),
            "full_name": plaintiff.full_name,
            "email": plaintiff.email,
            "case_type": plaintiff.case_type.value,
            "created_at": plaintiff.created_at.isoformat(),
        }
    
    async def _create_plaintiff_record_internal(self, lead_data: Dict[str, Any]) -> Plaintiff:
        """
        Internal method to create plaintiff record.
        
        Args:
            lead_data: Validated and enriched lead data.
            
        Returns:
            Plaintiff: Created plaintiff instance.
        """
        # Create Pydantic model for validation
        plaintiff_data = PlaintiffCreate(
            first_name=lead_data.get("first_name", ""),
            last_name=lead_data.get("last_name", ""),
            middle_name=lead_data.get("middle_name"),
            email=lead_data.get("email", ""),
            phone=lead_data.get("phone"),
            secondary_phone=lead_data.get("secondary_phone"),
            date_of_birth=lead_data.get("date_of_birth"),
            address_line_1=lead_data.get("address_line_1"),
            address_line_2=lead_data.get("address_line_2"),
            city=lead_data.get("city"),
            state=lead_data.get("state"),
            zip_code=lead_data.get("zip_code"),
            case_type=CaseType(lead_data.get("case_type", CaseType.OTHER.value)),
            case_description=lead_data.get("case_description"),
            incident_date=lead_data.get("incident_date"),
            employment_status=lead_data.get("employment_status"),
            monthly_income=lead_data.get("monthly_income"),
            monthly_expenses=lead_data.get("monthly_expenses"),
            lead_source=lead_data.get("lead_source", "web"),
            notes=lead_data.get("notes"),
        )
        
        # Create database record
        async with get_database_session() as session:
            # Convert Pydantic model to SQLAlchemy model
            plaintiff = Plaintiff(
                first_name=plaintiff_data.first_name,
                last_name=plaintiff_data.last_name,
                middle_name=plaintiff_data.middle_name,
                email=plaintiff_data.email,
                phone=plaintiff_data.phone,
                secondary_phone=plaintiff_data.secondary_phone,
                date_of_birth=plaintiff_data.date_of_birth,
                address_line_1=plaintiff_data.address_line_1,
                address_line_2=plaintiff_data.address_line_2,
                city=plaintiff_data.city,
                state=plaintiff_data.state,
                zip_code=plaintiff_data.zip_code,
                case_type=plaintiff_data.case_type,
                case_description=plaintiff_data.case_description,
                incident_date=plaintiff_data.incident_date,
                employment_status=plaintiff_data.employment_status,
                monthly_income=plaintiff_data.monthly_income,
                monthly_expenses=plaintiff_data.monthly_expenses,
                lead_source=plaintiff_data.lead_source,
                notes=plaintiff_data.notes,
                lead_source_details=lead_data.get("lead_source_details", {}),
            )
            
            session.add(plaintiff)
            await session.commit()
            await session.refresh(plaintiff)
            
            self.logger.info(
                "Plaintiff record created",
                plaintiff_id=str(plaintiff.id),
                email=plaintiff.email,
                case_type=plaintiff.case_type.value,
            )
            
            return plaintiff
    
    async def _route_to_downstream(self, task: AgentTask) -> Dict[str, Any]:
        """
        Route lead to downstream agents for processing.
        
        Args:
            task: Task containing plaintiff ID and lead data.
            
        Returns:
            dict: Routing results.
        """
        plaintiff_id = task.payload.get("plaintiff_id")
        lead_data = task.payload.get("lead_data", {})
        
        if not plaintiff_id:
            raise ValueError("Missing plaintiff_id in task payload")
        
        return await self._route_to_downstream_agents(plaintiff_id, lead_data)
    
    async def _route_to_downstream_agents(
        self,
        plaintiff_id: str,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route plaintiff to appropriate downstream agents.
        
        Args:
            plaintiff_id: ID of the created plaintiff.
            lead_data: Original lead data.
            
        Returns:
            dict: Routing results.
        """
        routing_results = {}
        
        # Route to Classification Agent
        try:
            await agent_communication.send_task(
                sender_id=self.agent_id,
                agent_type=AgentType.CLASSIFICATION,
                operation="classify_case",
                payload={
                    "plaintiff_id": plaintiff_id,
                    "case_description": lead_data.get("case_description", ""),
                    "case_type": lead_data.get("case_type"),
                }
            )
            routing_results["classification"] = "submitted"
        except Exception as e:
            self.logger.error(f"Failed to route to classification agent: {e}")
            routing_results["classification"] = f"failed: {e}"
        
        # Route to Risk Assessment Agent
        try:
            await agent_communication.send_task(
                sender_id=self.agent_id,
                agent_type=AgentType.RISK_ASSESSMENT,
                operation="assess_risk",
                payload={
                    "plaintiff_id": plaintiff_id,
                    "financial_info": {
                        "monthly_income": lead_data.get("monthly_income"),
                        "monthly_expenses": lead_data.get("monthly_expenses"),
                        "employment_status": lead_data.get("employment_status"),
                    },
                    "case_info": {
                        "case_type": lead_data.get("case_type"),
                        "incident_date": lead_data.get("incident_date"),
                        "case_description": lead_data.get("case_description"),
                    },
                }
            )
            routing_results["risk_assessment"] = "submitted"
        except Exception as e:
            self.logger.error(f"Failed to route to risk assessment agent: {e}")
            routing_results["risk_assessment"] = f"failed: {e}"
        
        # Route to Content Generation Agent for initial communication
        try:
            await agent_communication.send_task(
                sender_id=self.agent_id,
                agent_type=AgentType.CONTENT_GENERATION,
                operation="generate_welcome_email",
                payload={
                    "plaintiff_id": plaintiff_id,
                    "first_name": lead_data.get("first_name", ""),
                    "case_type": lead_data.get("case_type", ""),
                    "template_type": "initial_contact",
                }
            )
            routing_results["content_generation"] = "submitted"
        except Exception as e:
            self.logger.error(f"Failed to route to content generation agent: {e}")
            routing_results["content_generation"] = f"failed: {e}"
        
        self.logger.info(
            "Routed to downstream agents",
            plaintiff_id=plaintiff_id,
            routing_results=routing_results,
        )
        
        return routing_results
    
    async def _sync_with_pipedrive(
        self,
        plaintiff_id: str,
        lead_data: Dict[str, Any]
    ) -> None:
        """
        Sync plaintiff with Pipedrive CRM.
        
        Args:
            plaintiff_id: ID of the plaintiff.
            lead_data: Lead data for sync.
        """
        try:
            await agent_communication.send_task(
                sender_id=self.agent_id,
                agent_type=AgentType.PIPEDRIVE_SYNC,
                operation="sync_plaintiff",
                payload={
                    "plaintiff_id": plaintiff_id,
                    "sync_type": "create",
                    "priority": "high",
                }
            )
            
            self.logger.info(
                "Pipedrive sync initiated",
                plaintiff_id=plaintiff_id,
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initiate Pipedrive sync: {e}")
    
    async def _trigger_initial_contact(
        self,
        plaintiff_id: str,
        lead_data: Dict[str, Any]
    ) -> None:
        """
        Trigger initial contact communication.
        
        Args:
            plaintiff_id: ID of the plaintiff.
            lead_data: Lead data for personalization.
        """
        try:
            await agent_communication.send_task(
                sender_id=self.agent_id,
                agent_type=AgentType.EMAIL_SERVICE,
                operation="send_welcome_email",
                payload={
                    "plaintiff_id": plaintiff_id,
                    "email": lead_data.get("email"),
                    "first_name": lead_data.get("first_name", ""),
                    "template": "plaintiff_welcome",
                    "priority": "high",
                }
            )
            
            self.logger.info(
                "Initial contact triggered",
                plaintiff_id=plaintiff_id,
                email=lead_data.get("email"),
            )
            
        except Exception as e:
            self.logger.error(f"Failed to trigger initial contact: {e}")
    
    def _normalize_phone_number(self, phone: str) -> str:
        """
        Normalize phone number to standard format.
        
        Args:
            phone: Raw phone number.
            
        Returns:
            str: Normalized phone number.
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Handle US phone numbers
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"+{digits}"
        else:
            # Return as-is if not a standard US number
            return phone
    
    def _extract_case_type(self, lead_data: Dict[str, Any]) -> str:
        """
        Extract case type from lead description.
        
        Args:
            lead_data: Lead data.
            
        Returns:
            str: Detected case type.
        """
        description = (
            lead_data.get("case_description", "") + " " +
            lead_data.get("notes", "")
        ).lower()
        
        # Case type keywords
        case_type_keywords = {
            CaseType.AUTO_ACCIDENT: ["car accident", "auto accident", "vehicle accident", "car crash"],
            CaseType.SLIP_AND_FALL: ["slip and fall", "fall", "slip", "premises liability"],
            CaseType.MEDICAL_MALPRACTICE: ["medical malpractice", "doctor", "hospital", "medical"],
            CaseType.WORKERS_COMPENSATION: ["workers comp", "work injury", "workplace", "on the job"],
            CaseType.PRODUCT_LIABILITY: ["defective product", "product liability", "faulty"],
            CaseType.WRONGFUL_DEATH: ["wrongful death", "death", "fatal"],
            CaseType.EMPLOYMENT: ["employment", "workplace harassment", "discrimination"],
        }
        
        for case_type, keywords in case_type_keywords.items():
            if any(keyword in description for keyword in keywords):
                return case_type.value
        
        # Default to personal injury if no specific type detected
        return CaseType.PERSONAL_INJURY.value
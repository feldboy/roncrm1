"""Pipedrive synchronization service for bidirectional data sync."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database import Plaintiff, LawFirm, Lawyer, Case
from ...utils.logging import get_logger
from .client import PipedriveClient, PipedriveAPIError

logger = get_logger(__name__)


class PipedriveSyncService:
    """
    Service for synchronizing data between AI CRM and Pipedrive.
    
    Handles bidirectional synchronization with conflict resolution,
    field mapping, and error recovery.
    """
    
    def __init__(self, client: Optional[PipedriveClient] = None):
        """
        Initialize sync service.
        
        Args:
            client: Pipedrive client instance (creates new if not provided).
        """
        self.client = client or PipedriveClient()
        self.field_mappings = self._get_field_mappings()
        
    async def sync_plaintiff_to_pipedrive(
        self,
        plaintiff_id: UUID,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync plaintiff to Pipedrive as person and deal.
        
        Args:
            plaintiff_id: ID of the plaintiff to sync.
            force_update: Whether to force update even if already synced.
            
        Returns:
            dict: Sync result with person_id and deal_id.
        """
        async with get_database_session() as session:
            # Get plaintiff with relationships
            stmt = select(Plaintiff).where(Plaintiff.id == plaintiff_id)
            result = await session.execute(stmt)
            plaintiff = result.scalar_one_or_none()
            
            if not plaintiff:
                raise ValueError(f"Plaintiff {plaintiff_id} not found")
            
            sync_result = {
                "plaintiff_id": str(plaintiff_id),
                "success": False,
                "person_id": None,
                "deal_id": None,
                "errors": [],
                "warnings": [],
            }
            
            try:
                # Sync as person
                person_result = await self._sync_plaintiff_as_person(plaintiff, force_update)
                sync_result["person_id"] = person_result["person_id"]
                
                # Sync as deal
                deal_result = await self._sync_plaintiff_as_deal(plaintiff, person_result["person_id"], force_update)
                sync_result["deal_id"] = deal_result["deal_id"]
                
                # Update plaintiff with Pipedrive IDs
                plaintiff.pipedrive_person_id = person_result["person_id"]
                plaintiff.pipedrive_deal_id = deal_result["deal_id"]
                await session.commit()
                
                sync_result["success"] = True
                
                logger.info(
                    "Plaintiff synced to Pipedrive successfully",
                    plaintiff_id=str(plaintiff_id),
                    person_id=person_result["person_id"],
                    deal_id=deal_result["deal_id"],
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to sync plaintiff to Pipedrive: {e}",
                    plaintiff_id=str(plaintiff_id),
                )
                sync_result["errors"].append(str(e))
                await session.rollback()
            
            return sync_result
    
    async def sync_law_firm_to_pipedrive(
        self,
        law_firm_id: UUID,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync law firm to Pipedrive as organization.
        
        Args:
            law_firm_id: ID of the law firm to sync.
            force_update: Whether to force update even if already synced.
            
        Returns:
            dict: Sync result with organization_id.
        """
        async with get_database_session() as session:
            stmt = select(LawFirm).where(LawFirm.id == law_firm_id)
            result = await session.execute(stmt)
            law_firm = result.scalar_one_or_none()
            
            if not law_firm:
                raise ValueError(f"Law firm {law_firm_id} not found")
            
            sync_result = {
                "law_firm_id": str(law_firm_id),
                "success": False,
                "organization_id": None,
                "errors": [],
            }
            
            try:
                # Check if already synced
                if law_firm.pipedrive_org_id and not force_update:
                    # Verify organization still exists in Pipedrive
                    try:
                        await self.client.get_organization(law_firm.pipedrive_org_id)
                        sync_result["organization_id"] = law_firm.pipedrive_org_id
                        sync_result["success"] = True
                        return sync_result
                    except PipedriveAPIError:
                        # Organization doesn't exist, need to recreate
                        law_firm.pipedrive_org_id = None
                
                # Map law firm data to Pipedrive format
                org_data = self._map_law_firm_to_organization(law_firm)
                
                if law_firm.pipedrive_org_id:
                    # Update existing organization
                    response = await self.client.update_organization(
                        law_firm.pipedrive_org_id,
                        org_data
                    )
                    sync_result["organization_id"] = law_firm.pipedrive_org_id
                else:
                    # Create new organization
                    response = await self.client.create_organization(org_data)
                    organization_id = response["data"]["id"]
                    law_firm.pipedrive_org_id = organization_id
                    sync_result["organization_id"] = organization_id
                
                await session.commit()
                sync_result["success"] = True
                
                logger.info(
                    "Law firm synced to Pipedrive successfully",
                    law_firm_id=str(law_firm_id),
                    organization_id=sync_result["organization_id"],
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to sync law firm to Pipedrive: {e}",
                    law_firm_id=str(law_firm_id),
                )
                sync_result["errors"].append(str(e))
                await session.rollback()
            
            return sync_result
    
    async def sync_from_pipedrive(
        self,
        entity_type: str,
        pipedrive_id: int,
        last_sync: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Sync data from Pipedrive to AI CRM.
        
        Args:
            entity_type: Type of entity (person, organization, deal).
            pipedrive_id: Pipedrive entity ID.
            last_sync: Last sync timestamp for incremental sync.
            
        Returns:
            dict: Sync result.
        """
        sync_result = {
            "entity_type": entity_type,
            "pipedrive_id": pipedrive_id,
            "success": False,
            "ai_crm_id": None,
            "action": None,  # created, updated, skipped
            "errors": [],
        }
        
        try:
            if entity_type == "person":
                result = await self._sync_person_from_pipedrive(pipedrive_id, last_sync)
            elif entity_type == "organization":
                result = await self._sync_organization_from_pipedrive(pipedrive_id, last_sync)
            elif entity_type == "deal":
                result = await self._sync_deal_from_pipedrive(pipedrive_id, last_sync)
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            sync_result.update(result)
            sync_result["success"] = True
            
        except Exception as e:
            logger.error(
                f"Failed to sync {entity_type} from Pipedrive: {e}",
                pipedrive_id=pipedrive_id,
            )
            sync_result["errors"].append(str(e))
        
        return sync_result
    
    async def _sync_plaintiff_as_person(
        self,
        plaintiff: Plaintiff,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """Sync plaintiff as Pipedrive person."""
        # Map plaintiff data to person format
        person_data = self._map_plaintiff_to_person(plaintiff)
        
        if plaintiff.pipedrive_person_id and not force_update:
            # Update existing person
            response = await self.client.update_person(
                plaintiff.pipedrive_person_id,
                person_data
            )
            person_id = plaintiff.pipedrive_person_id
        else:
            # Create new person
            response = await self.client.create_person(person_data)
            person_id = response["data"]["id"]
        
        return {"person_id": person_id}
    
    async def _sync_plaintiff_as_deal(
        self,
        plaintiff: Plaintiff,
        person_id: int,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """Sync plaintiff case as Pipedrive deal."""
        # Map case data to deal format
        deal_data = self._map_plaintiff_to_deal(plaintiff, person_id)
        
        if plaintiff.pipedrive_deal_id and not force_update:
            # Update existing deal
            response = await self.client.update_deal(
                plaintiff.pipedrive_deal_id,
                deal_data
            )
            deal_id = plaintiff.pipedrive_deal_id
        else:
            # Create new deal
            response = await self.client.create_deal(deal_data)
            deal_id = response["data"]["id"]
        
        return {"deal_id": deal_id}
    
    async def _sync_person_from_pipedrive(
        self,
        person_id: int,
        last_sync: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync person from Pipedrive to plaintiff."""
        # Get person data from Pipedrive
        response = await self.client.get_person(person_id)
        person_data = response["data"]
        
        # Check if we need to update based on timestamp
        if last_sync:
            update_time = datetime.fromisoformat(person_data["update_time"].replace("Z", "+00:00"))
            if update_time <= last_sync:
                return {"action": "skipped", "reason": "no_changes"}
        
        async with get_database_session() as session:
            # Check if plaintiff already exists
            stmt = select(Plaintiff).where(Plaintiff.pipedrive_person_id == person_id)
            result = await session.execute(stmt)
            plaintiff = result.scalar_one_or_none()
            
            if plaintiff:
                # Update existing plaintiff
                self._update_plaintiff_from_person_data(plaintiff, person_data)
                action = "updated"
            else:
                # Create new plaintiff
                plaintiff = self._create_plaintiff_from_person_data(person_data)
                session.add(plaintiff)
                action = "created"
            
            await session.commit()
            
            return {
                "ai_crm_id": str(plaintiff.id),
                "action": action,
            }
    
    def _map_plaintiff_to_person(self, plaintiff: Plaintiff) -> Dict[str, Any]:
        """Map plaintiff data to Pipedrive person format."""
        return {
            "name": plaintiff.full_name,
            "email": [{"value": plaintiff.email, "primary": True}] if plaintiff.email else [],
            "phone": [{"value": plaintiff.phone, "primary": True}] if plaintiff.phone else [],
            "add_time": plaintiff.created_at.isoformat(),
            "visible_to": "3",  # Visible to entire company
            # Custom fields mapping would go here
        }
    
    def _map_plaintiff_to_deal(self, plaintiff: Plaintiff, person_id: int) -> Dict[str, Any]:
        """Map plaintiff case to Pipedrive deal format."""
        # Determine deal value based on case type
        deal_value = self._estimate_deal_value(plaintiff)
        
        return {
            "title": f"{plaintiff.full_name} - {plaintiff.case_type.value.replace('_', ' ').title()}",
            "person_id": person_id,
            "org_id": plaintiff.law_firm.pipedrive_org_id if plaintiff.law_firm else None,
            "value": deal_value,
            "currency": "USD",
            "add_time": plaintiff.created_at.isoformat(),
            "visible_to": "3",
            "status": "open",
            "stage_id": self._map_case_status_to_stage(plaintiff.case_status),
            # Custom fields for case-specific data
        }
    
    def _map_law_firm_to_organization(self, law_firm: LawFirm) -> Dict[str, Any]:
        """Map law firm data to Pipedrive organization format."""
        return {
            "name": law_firm.name,
            "visible_to": "3",
            "add_time": law_firm.created_at.isoformat(),
            # Custom fields mapping would go here
        }
    
    def _estimate_deal_value(self, plaintiff: Plaintiff) -> int:
        """Estimate deal value based on case type and other factors."""
        base_values = {
            "personal_injury": 25000,
            "medical_malpractice": 100000,
            "auto_accident": 30000,
            "slip_and_fall": 20000,
            "workers_compensation": 15000,
            "product_liability": 75000,
            "wrongful_death": 250000,
            "employment": 50000,
        }
        
        return base_values.get(plaintiff.case_type.value, 25000)
    
    def _map_case_status_to_stage(self, case_status) -> int:
        """Map case status to Pipedrive pipeline stage."""
        # This would map to actual Pipedrive pipeline stages
        stage_mapping = {
            "initial": 1,
            "qualifying": 2,
            "qualified": 3,
            "document_collection": 4,
            "underwriting": 5,
            "approved": 6,
            "funded": 7,
            "settled": 8,
            "closed": 9,
            "rejected": 10,
        }
        
        return stage_mapping.get(case_status.value, 1)
    
    def _create_plaintiff_from_person_data(self, person_data: Dict[str, Any]) -> Plaintiff:
        """Create plaintiff from Pipedrive person data."""
        # Extract name parts
        name_parts = person_data.get("name", "").split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Extract email
        emails = person_data.get("email", [])
        email = emails[0]["value"] if emails else ""
        
        # Extract phone
        phones = person_data.get("phone", [])
        phone = phones[0]["value"] if phones else ""
        
        return Plaintiff(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            pipedrive_person_id=person_data["id"],
            case_type="other",  # Default, would be determined later
            case_status="initial",
            lead_source="pipedrive",
        )
    
    def _update_plaintiff_from_person_data(
        self,
        plaintiff: Plaintiff,
        person_data: Dict[str, Any]
    ) -> None:
        """Update plaintiff with Pipedrive person data."""
        # Update name if changed
        name_parts = person_data.get("name", "").split()
        if name_parts:
            plaintiff.first_name = name_parts[0]
            plaintiff.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Update email if changed
        emails = person_data.get("email", [])
        if emails:
            plaintiff.email = emails[0]["value"]
        
        # Update phone if changed
        phones = person_data.get("phone", [])
        if phones:
            plaintiff.phone = phones[0]["value"]
    
    def _get_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """Get field mappings between AI CRM and Pipedrive."""
        return {
            "person": {
                "first_name": "name",  # Combined in Pipedrive
                "last_name": "name",   # Combined in Pipedrive
                "email": "email",
                "phone": "phone",
            },
            "organization": {
                "name": "name",
                "contact_email": "email",
                "contact_phone": "phone",
            },
            "deal": {
                "title": "title",
                "case_status": "stage_id",
                "estimated_value": "value",
            },
        }
    
    async def bulk_sync_to_pipedrive(
        self,
        entity_type: str,
        entity_ids: List[UUID],
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Bulk sync entities to Pipedrive.
        
        Args:
            entity_type: Type of entity to sync.
            entity_ids: List of entity IDs.
            batch_size: Number of entities to process concurrently.
            
        Returns:
            dict: Bulk sync results.
        """
        results = {
            "total": len(entity_ids),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(entity_ids), batch_size):
            batch = entity_ids[i:i + batch_size]
            
            # Create tasks for concurrent processing
            tasks = []
            for entity_id in batch:
                if entity_type == "plaintiff":
                    task = self.sync_plaintiff_to_pipedrive(entity_id)
                elif entity_type == "law_firm":
                    task = self.sync_law_firm_to_pipedrive(entity_id)
                else:
                    continue
                
                tasks.append(task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append(str(result))
                elif result.get("success"):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].extend(result.get("errors", []))
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        logger.info(
            f"Bulk sync completed",
            entity_type=entity_type,
            total=results["total"],
            successful=results["successful"],
            failed=results["failed"],
        )
        
        return results
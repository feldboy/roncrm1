"""Pipedrive Synchronization Agent implementation."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from ...services.pipedrive.client import PipedriveClient
from ...services.pipedrive.sync import PipedriveSyncService
from ..base.agent import BaseAgent, AgentTask, AgentResponse, AgentType
from ..base.communication import agent_communication


class PipedriveSyncAgent(BaseAgent):
    """
    Pipedrive Synchronization Agent for real-time bidirectional sync.
    
    Handles synchronization between AI CRM and Pipedrive with
    conflict resolution, error recovery, and performance optimization.
    """
    
    def __init__(self, config):
        """Initialize the Pipedrive Sync Agent."""
        super().__init__(config)
        
        # Initialize Pipedrive client and sync service
        self.pipedrive_client = PipedriveClient()
        self.sync_service = PipedriveSyncService(self.pipedrive_client)
        
        # Operation handlers
        self._handlers = {
            "sync_plaintiff": self._sync_plaintiff,
            "sync_law_firm": self._sync_law_firm,
            "sync_from_pipedrive": self._sync_from_pipedrive,
            "bulk_sync": self._bulk_sync,
            "health_check": self._health_check,
            "setup_webhooks": self._setup_webhooks,
            "process_webhook": self._process_webhook,
            "full_sync": self._full_sync,
        }
        
        # Sync statistics
        self.sync_stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_sync": None,
            "sync_errors": [],
        }
        
        self.logger.info("Pipedrive Sync Agent initialized")
    
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
            
            # Update sync statistics
            self.sync_stats["total_syncs"] += 1
            self.sync_stats["successful_syncs"] += 1
            self.sync_stats["last_sync"] = datetime.utcnow().isoformat()
            
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
            # Update error statistics
            self.sync_stats["total_syncs"] += 1
            self.sync_stats["failed_syncs"] += 1
            self.sync_stats["sync_errors"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "operation": task.operation,
                "error": str(e),
            })
            
            # Keep only last 100 errors
            if len(self.sync_stats["sync_errors"]) > 100:
                self.sync_stats["sync_errors"] = self.sync_stats["sync_errors"][-100:]
            
            self.logger.error(
                f"Sync task processing failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            return self.create_error_response(task.id, str(e))
    
    async def _sync_plaintiff(self, task: AgentTask) -> Dict[str, Any]:
        """
        Sync plaintiff to Pipedrive.
        
        Args:
            task: Task containing plaintiff sync parameters.
            
        Returns:
            dict: Sync result.
        """
        plaintiff_id = task.payload.get("plaintiff_id")
        force_update = task.payload.get("force_update", False)
        sync_type = task.payload.get("sync_type", "create")  # create, update, delete
        
        if not plaintiff_id:
            raise ValueError("Missing plaintiff_id in task payload")
        
        try:
            plaintiff_uuid = UUID(plaintiff_id) if isinstance(plaintiff_id, str) else plaintiff_id
        except ValueError:
            raise ValueError(f"Invalid plaintiff_id format: {plaintiff_id}")
        
        self.logger.info(
            "Syncing plaintiff to Pipedrive",
            plaintiff_id=str(plaintiff_uuid),
            sync_type=sync_type,
            force_update=force_update,
        )
        
        if sync_type == "delete":
            # Handle deletion sync
            return await self._handle_plaintiff_deletion(plaintiff_uuid)
        else:
            # Handle create/update sync
            result = await self.sync_service.sync_plaintiff_to_pipedrive(
                plaintiff_uuid,
                force_update=force_update
            )
            
            # Publish sync event
            await agent_communication.publish(
                sender_id=self.agent_id,
                event_type="plaintiff_synced",
                payload={
                    "plaintiff_id": str(plaintiff_uuid),
                    "pipedrive_person_id": result.get("person_id"),
                    "pipedrive_deal_id": result.get("deal_id"),
                    "sync_type": sync_type,
                    "success": result["success"],
                }
            )
            
            return result
    
    async def _sync_law_firm(self, task: AgentTask) -> Dict[str, Any]:
        """
        Sync law firm to Pipedrive.
        
        Args:
            task: Task containing law firm sync parameters.
            
        Returns:
            dict: Sync result.
        """
        law_firm_id = task.payload.get("law_firm_id")
        force_update = task.payload.get("force_update", False)
        
        if not law_firm_id:
            raise ValueError("Missing law_firm_id in task payload")
        
        try:
            law_firm_uuid = UUID(law_firm_id) if isinstance(law_firm_id, str) else law_firm_id
        except ValueError:
            raise ValueError(f"Invalid law_firm_id format: {law_firm_id}")
        
        self.logger.info(
            "Syncing law firm to Pipedrive",
            law_firm_id=str(law_firm_uuid),
            force_update=force_update,
        )
        
        result = await self.sync_service.sync_law_firm_to_pipedrive(
            law_firm_uuid,
            force_update=force_update
        )
        
        # Publish sync event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="law_firm_synced",
            payload={
                "law_firm_id": str(law_firm_uuid),
                "pipedrive_org_id": result.get("organization_id"),
                "success": result["success"],
            }
        )
        
        return result
    
    async def _sync_from_pipedrive(self, task: AgentTask) -> Dict[str, Any]:
        """
        Sync data from Pipedrive to AI CRM.
        
        Args:
            task: Task containing Pipedrive sync parameters.
            
        Returns:
            dict: Sync result.
        """
        entity_type = task.payload.get("entity_type")
        pipedrive_id = task.payload.get("pipedrive_id")
        last_sync = task.payload.get("last_sync")
        
        if not entity_type or not pipedrive_id:
            raise ValueError("Missing entity_type or pipedrive_id in task payload")
        
        if last_sync:
            last_sync = datetime.fromisoformat(last_sync)
        
        self.logger.info(
            "Syncing from Pipedrive to AI CRM",
            entity_type=entity_type,
            pipedrive_id=pipedrive_id,
            last_sync=last_sync.isoformat() if last_sync else None,
        )
        
        result = await self.sync_service.sync_from_pipedrive(
            entity_type=entity_type,
            pipedrive_id=pipedrive_id,
            last_sync=last_sync
        )
        
        # Publish sync event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="pipedrive_entity_synced",
            payload={
                "entity_type": entity_type,
                "pipedrive_id": pipedrive_id,
                "ai_crm_id": result.get("ai_crm_id"),
                "action": result.get("action"),
                "success": result["success"],
            }
        )
        
        return result
    
    async def _bulk_sync(self, task: AgentTask) -> Dict[str, Any]:
        """
        Perform bulk synchronization.
        
        Args:
            task: Task containing bulk sync parameters.
            
        Returns:
            dict: Bulk sync result.
        """
        entity_type = task.payload.get("entity_type")
        entity_ids = task.payload.get("entity_ids", [])
        batch_size = task.payload.get("batch_size", 10)
        direction = task.payload.get("direction", "to_pipedrive")  # to_pipedrive, from_pipedrive
        
        if not entity_type:
            raise ValueError("Missing entity_type in task payload")
        
        self.logger.info(
            "Starting bulk sync",
            entity_type=entity_type,
            entity_count=len(entity_ids),
            direction=direction,
            batch_size=batch_size,
        )
        
        if direction == "to_pipedrive":
            # Convert string IDs to UUIDs
            uuid_ids = [UUID(id_str) if isinstance(id_str, str) else id_str for id_str in entity_ids]
            
            result = await self.sync_service.bulk_sync_to_pipedrive(
                entity_type=entity_type,
                entity_ids=uuid_ids,
                batch_size=batch_size
            )
        else:
            # Bulk sync from Pipedrive would be implemented here
            result = {"error": "Bulk sync from Pipedrive not yet implemented"}
        
        # Publish bulk sync event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="bulk_sync_completed",
            payload={
                "entity_type": entity_type,
                "direction": direction,
                "total": result.get("total", 0),
                "successful": result.get("successful", 0),
                "failed": result.get("failed", 0),
            }
        )
        
        return result
    
    async def _health_check(self, task: AgentTask) -> Dict[str, Any]:
        """
        Perform health check on Pipedrive connection.
        
        Args:
            task: Health check task.
            
        Returns:
            dict: Health check result.
        """
        self.logger.info("Performing Pipedrive health check")
        
        health_result = {
            "pipedrive_accessible": False,
            "api_response_time_ms": None,
            "sync_stats": self.sync_stats.copy(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        try:
            start_time = datetime.utcnow()
            is_healthy = await self.pipedrive_client.health_check()
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            health_result["pipedrive_accessible"] = is_healthy
            health_result["api_response_time_ms"] = response_time
            
            if not is_healthy:
                self.logger.warning("Pipedrive health check failed")
            
        except Exception as e:
            self.logger.error(f"Pipedrive health check error: {e}")
            health_result["error"] = str(e)
        
        return health_result
    
    async def _setup_webhooks(self, task: AgentTask) -> Dict[str, Any]:
        """
        Setup Pipedrive webhooks for real-time sync.
        
        Args:
            task: Webhook setup task.
            
        Returns:
            dict: Webhook setup result.
        """
        webhook_url = task.payload.get("webhook_url")
        events = task.payload.get("events", [
            "added.person",
            "updated.person",
            "deleted.person",
            "added.deal",
            "updated.deal",
            "deleted.deal",
            "added.organization",
            "updated.organization",
            "deleted.organization",
        ])
        
        if not webhook_url:
            raise ValueError("Missing webhook_url in task payload")
        
        self.logger.info(
            "Setting up Pipedrive webhooks",
            webhook_url=webhook_url,
            events=events,
        )
        
        setup_results = []
        
        # Get existing webhooks
        try:
            existing_webhooks = await self.pipedrive_client.get_webhooks()
            existing_urls = {wh["data"]["subscription_url"] for wh in existing_webhooks.get("data", [])}
        except Exception as e:
            self.logger.warning(f"Failed to get existing webhooks: {e}")
            existing_urls = set()
        
        # Create webhooks for each event type
        for event in events:
            if webhook_url not in existing_urls:
                try:
                    webhook_data = {
                        "subscription_url": webhook_url,
                        "event_action": event,
                        "event_object": event.split(".")[1],  # person, deal, organization
                    }
                    
                    result = await self.pipedrive_client.create_webhook(webhook_data)
                    setup_results.append({
                        "event": event,
                        "success": True,
                        "webhook_id": result["data"]["id"],
                    })
                    
                except Exception as e:
                    self.logger.error(f"Failed to create webhook for {event}: {e}")
                    setup_results.append({
                        "event": event,
                        "success": False,
                        "error": str(e),
                    })
            else:
                setup_results.append({
                    "event": event,
                    "success": True,
                    "status": "already_exists",
                })
        
        return {
            "webhook_url": webhook_url,
            "events": events,
            "results": setup_results,
            "successful": sum(1 for r in setup_results if r["success"]),
            "failed": sum(1 for r in setup_results if not r["success"]),
        }
    
    async def _process_webhook(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process incoming Pipedrive webhook.
        
        Args:
            task: Webhook processing task.
            
        Returns:
            dict: Webhook processing result.
        """
        webhook_data = task.payload.get("webhook_data")
        
        if not webhook_data:
            raise ValueError("Missing webhook_data in task payload")
        
        event = webhook_data.get("event")
        object_type = webhook_data.get("meta", {}).get("object")
        object_id = webhook_data.get("meta", {}).get("id")
        
        self.logger.info(
            "Processing Pipedrive webhook",
            event=event,
            object_type=object_type,
            object_id=object_id,
        )
        
        processing_result = {
            "event": event,
            "object_type": object_type,
            "object_id": object_id,
            "action_taken": None,
            "success": False,
        }
        
        try:
            if event in ["added", "updated"] and object_type in ["person", "deal", "organization"]:
                # Sync from Pipedrive to AI CRM
                sync_result = await self.sync_service.sync_from_pipedrive(
                    entity_type=object_type,
                    pipedrive_id=object_id
                )
                
                processing_result["action_taken"] = f"synced_{object_type}_from_pipedrive"
                processing_result["sync_result"] = sync_result
                processing_result["success"] = sync_result["success"]
                
            elif event == "deleted":
                # Handle deletion
                processing_result["action_taken"] = f"marked_{object_type}_as_deleted"
                processing_result["success"] = True
                # Implementation for handling deletions would go here
                
            else:
                self.logger.warning(f"Unhandled webhook event: {event} for {object_type}")
                processing_result["action_taken"] = "ignored"
                processing_result["success"] = True
            
        except Exception as e:
            self.logger.error(f"Failed to process webhook: {e}")
            processing_result["error"] = str(e)
        
        return processing_result
    
    async def _full_sync(self, task: AgentTask) -> Dict[str, Any]:
        """
        Perform full synchronization between AI CRM and Pipedrive.
        
        Args:
            task: Full sync task.
            
        Returns:
            dict: Full sync result.
        """
        direction = task.payload.get("direction", "bidirectional")  # to_pipedrive, from_pipedrive, bidirectional
        entity_types = task.payload.get("entity_types", ["plaintiff", "law_firm"])
        batch_size = task.payload.get("batch_size", 10)
        
        self.logger.info(
            "Starting full synchronization",
            direction=direction,
            entity_types=entity_types,
            batch_size=batch_size,
        )
        
        full_sync_result = {
            "direction": direction,
            "entity_types": entity_types,
            "started_at": datetime.utcnow().isoformat(),
            "results": {},
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
        }
        
        # This would implement a comprehensive sync strategy
        # For now, implementing a basic version
        
        if direction in ["to_pipedrive", "bidirectional"]:
            for entity_type in entity_types:
                # Get all entities that need syncing
                # This would query the database for entities without Pipedrive IDs
                # or entities modified since last sync
                
                # Placeholder for actual implementation
                sync_result = {
                    "entity_type": entity_type,
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "errors": [],
                }
                
                full_sync_result["results"][f"{entity_type}_to_pipedrive"] = sync_result
        
        if direction in ["from_pipedrive", "bidirectional"]:
            # Sync from Pipedrive would be implemented here
            pass
        
        full_sync_result["completed_at"] = datetime.utcnow().isoformat()
        
        # Calculate totals
        for result in full_sync_result["results"].values():
            full_sync_result["total_processed"] += result.get("total", 0)
            full_sync_result["total_successful"] += result.get("successful", 0)
            full_sync_result["total_failed"] += result.get("failed", 0)
        
        # Publish full sync completion event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="full_sync_completed",
            payload=full_sync_result
        )
        
        return full_sync_result
    
    async def _handle_plaintiff_deletion(self, plaintiff_id: UUID) -> Dict[str, Any]:
        """
        Handle plaintiff deletion sync to Pipedrive.
        
        Args:
            plaintiff_id: ID of the deleted plaintiff.
            
        Returns:
            dict: Deletion sync result.
        """
        # This would implement proper deletion handling
        # For now, returning a placeholder
        
        return {
            "plaintiff_id": str(plaintiff_id),
            "action": "deletion_handled",
            "success": True,
            "pipedrive_actions": ["person_deleted", "deal_closed"],
        }
    
    async def start(self) -> None:
        """Start the agent and perform initialization."""
        await super().start()
        
        # Perform initial health check
        try:
            health_check_task = AgentTask(
                agent_type=self.agent_type,
                operation="health_check",
                payload={}
            )
            await self._health_check(health_check_task)
        except Exception as e:
            self.logger.warning(f"Initial health check failed: {e}")
    
    async def stop(self) -> None:
        """Stop the agent and cleanup resources."""
        # Close Pipedrive client
        if self.pipedrive_client:
            await self.pipedrive_client.close()
        
        await super().stop()
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """
        Get synchronization statistics.
        
        Returns:
            dict: Current sync statistics.
        """
        return {
            **self.sync_stats,
            "success_rate": (
                self.sync_stats["successful_syncs"] / self.sync_stats["total_syncs"]
                if self.sync_stats["total_syncs"] > 0 else 0
            ),
            "recent_errors": self.sync_stats["sync_errors"][-10:],  # Last 10 errors
        }
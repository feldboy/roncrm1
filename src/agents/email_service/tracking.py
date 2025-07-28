"""Email tracking and analytics system."""

import hashlib
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database import Communication
from ...utils.logging import get_logger

logger = get_logger(__name__)


class EmailTracker:
    """
    Email tracking service for monitoring email engagement.
    
    Tracks email opens, clicks, bounces, and unsubscribes
    to provide analytics and improve email effectiveness.
    """
    
    def __init__(self):
        """Initialize email tracker."""
        self.tracking_pixel_template = """
        <img src="{tracking_url}" width="1" height="1" style="border:0; display:none;" alt="" />
        """
        
        self.tracking_data = {}  # In-memory tracking store (should use Redis in production)
    
    def generate_tracking_id(self) -> str:
        """Generate unique tracking ID for email."""
        return str(uuid4())
    
    def add_tracking_pixel(self, html_content: str, tracking_id: str) -> str:
        """
        Add tracking pixel to HTML email content.
        
        Args:
            html_content: Original HTML content.
            tracking_id: Unique tracking ID.
            
        Returns:
            str: HTML content with tracking pixel added.
        """
        if not html_content:
            return html_content
        
        tracking_url = f"/api/email/track/open/{tracking_id}"
        tracking_pixel = self.tracking_pixel_template.format(tracking_url=tracking_url)
        
        # Try to insert before closing body tag
        if "</body>" in html_content.lower():
            return html_content.replace("</body>", f"{tracking_pixel}</body>")
        else:
            # If no body tag, append at the end
            return html_content + tracking_pixel
    
    def add_click_tracking(self, html_content: str, tracking_id: str) -> str:
        """
        Add click tracking to links in HTML email content.
        
        Args:
            html_content: Original HTML content.
            tracking_id: Unique tracking ID.
            
        Returns:
            str: HTML content with click tracking added.
        """
        import re
        
        if not html_content:
            return html_content
        
        # Find all links
        link_pattern = r'<a\s+([^>]*href=["\'])([^"\']+)(["\'][^>]*)>'
        
        def replace_link(match):
            prefix = match.group(1)
            original_url = match.group(2)
            suffix = match.group(3)
            
            # Skip tracking URLs and mailto links
            if original_url.startswith(('mailto:', '/api/email/track', '#')):
                return match.group(0)
            
            # Create tracked URL
            tracked_url = f"/api/email/track/click/{tracking_id}?url={original_url}"
            
            return f'<a {prefix}{tracked_url}{suffix}>'
        
        return re.sub(link_pattern, replace_link, html_content, flags=re.IGNORECASE)
    
    async def store_tracking_info(
        self,
        tracking_id: str,
        to_email: str,
        subject: str,
        plaintiff_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store tracking information for an email.
        
        Args:
            tracking_id: Unique tracking ID.
            to_email: Recipient email address.
            subject: Email subject.
            plaintiff_id: Optional plaintiff ID.
            metadata: Optional additional metadata.
        """
        tracking_data = {
            "tracking_id": tracking_id,
            "to_email": to_email,
            "subject": subject,
            "plaintiff_id": plaintiff_id,
            "sent_at": datetime.utcnow().isoformat(),
            "opened_at": None,
            "opened_count": 0,
            "clicked_at": None,
            "clicked_count": 0,
            "clicked_links": [],
            "bounced": False,
            "unsubscribed": False,
            "metadata": metadata or {},
        }
        
        self.tracking_data[tracking_id] = tracking_data
        
        # Store in database as well
        async with get_database_session() as session:
            try:
                # Update the communication record if plaintiff_id provided
                if plaintiff_id:
                    stmt = (
                        select(Communication)
                        .where(Communication.plaintiff_id == UUID(plaintiff_id))
                        .where(Communication.subject == subject)
                        .where(Communication.to_address == to_email)
                        .order_by(Communication.created_at.desc())
                    )
                    result = await session.execute(stmt)
                    communication = result.scalar_one_or_none()
                    
                    if communication:
                        comm_metadata = communication.metadata or {}
                        comm_metadata["tracking_id"] = tracking_id
                        comm_metadata["tracking_enabled"] = True
                        communication.metadata = comm_metadata
                        await session.commit()
                        
            except Exception as e:
                logger.error(f"Failed to store tracking info in database: {e}")
    
    async def track_open(
        self,
        tracking_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track email open event.
        
        Args:
            tracking_id: Unique tracking ID.
            user_agent: User agent string.
            ip_address: IP address of opener.
            
        Returns:
            dict: Tracking result.
        """
        try:
            if tracking_id not in self.tracking_data:
                return {
                    "success": False,
                    "error": "Tracking ID not found",
                }
            
            tracking_info = self.tracking_data[tracking_id]
            
            # Update tracking data
            if not tracking_info["opened_at"]:
                tracking_info["opened_at"] = datetime.utcnow().isoformat()
            
            tracking_info["opened_count"] += 1
            tracking_info["last_opened_at"] = datetime.utcnow().isoformat()
            
            # Store open event details
            open_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_agent": user_agent,
                "ip_address": ip_address,
            }
            
            if "open_events" not in tracking_info:
                tracking_info["open_events"] = []
            tracking_info["open_events"].append(open_event)
            
            logger.info(
                "Email open tracked",
                tracking_id=tracking_id,
                to_email=tracking_info["to_email"],
                open_count=tracking_info["opened_count"],
            )
            
            return {
                "success": True,
                "tracking_id": tracking_id,
                "open_count": tracking_info["opened_count"],
                "first_open": tracking_info["opened_count"] == 1,
            }
            
        except Exception as e:
            logger.error(f"Failed to track email open: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def track_click(
        self,
        tracking_id: str,
        clicked_url: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track email link click event.
        
        Args:
            tracking_id: Unique tracking ID.
            clicked_url: URL that was clicked.
            user_agent: User agent string.
            ip_address: IP address of clicker.
            
        Returns:
            dict: Tracking result.
        """
        try:
            if tracking_id not in self.tracking_data:
                return {
                    "success": False,
                    "error": "Tracking ID not found",
                }
            
            tracking_info = self.tracking_data[tracking_id]
            
            # Update tracking data
            if not tracking_info["clicked_at"]:
                tracking_info["clicked_at"] = datetime.utcnow().isoformat()
            
            tracking_info["clicked_count"] += 1
            tracking_info["last_clicked_at"] = datetime.utcnow().isoformat()
            
            # Store click event details
            click_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "url": clicked_url,
                "user_agent": user_agent,
                "ip_address": ip_address,
            }
            
            if "click_events" not in tracking_info:
                tracking_info["click_events"] = []
            tracking_info["click_events"].append(click_event)
            
            # Track unique clicked links
            if clicked_url not in tracking_info["clicked_links"]:
                tracking_info["clicked_links"].append(clicked_url)
            
            logger.info(
                "Email click tracked",
                tracking_id=tracking_id,
                to_email=tracking_info["to_email"],
                clicked_url=clicked_url,
                click_count=tracking_info["clicked_count"],
            )
            
            return {
                "success": True,
                "tracking_id": tracking_id,
                "clicked_url": clicked_url,
                "click_count": tracking_info["clicked_count"],
                "redirect_url": clicked_url,
            }
            
        except Exception as e:
            logger.error(f"Failed to track email click: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def track_bounce(
        self,
        tracking_id: str,
        bounce_type: str,
        bounce_reason: str
    ) -> Dict[str, Any]:
        """
        Track email bounce event.
        
        Args:
            tracking_id: Unique tracking ID.
            bounce_type: Type of bounce (hard, soft).
            bounce_reason: Reason for bounce.
            
        Returns:
            dict: Tracking result.
        """
        try:
            if tracking_id not in self.tracking_data:
                return {
                    "success": False,
                    "error": "Tracking ID not found",
                }
            
            tracking_info = self.tracking_data[tracking_id]
            
            # Update tracking data
            tracking_info["bounced"] = True
            tracking_info["bounced_at"] = datetime.utcnow().isoformat()
            tracking_info["bounce_type"] = bounce_type
            tracking_info["bounce_reason"] = bounce_reason
            
            logger.warning(
                "Email bounce tracked",
                tracking_id=tracking_id,
                to_email=tracking_info["to_email"],
                bounce_type=bounce_type,
                bounce_reason=bounce_reason,
            )
            
            return {
                "success": True,
                "tracking_id": tracking_id,
                "bounce_type": bounce_type,
                "bounce_reason": bounce_reason,
            }
            
        except Exception as e:
            logger.error(f"Failed to track email bounce: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def track_unsubscribe(
        self,
        tracking_id: str,
        unsubscribe_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track email unsubscribe event.
        
        Args:
            tracking_id: Unique tracking ID.
            unsubscribe_reason: Optional reason for unsubscribe.
            
        Returns:
            dict: Tracking result.
        """
        try:
            if tracking_id not in self.tracking_data:
                return {
                    "success": False,
                    "error": "Tracking ID not found",
                }
            
            tracking_info = self.tracking_data[tracking_id]
            
            # Update tracking data
            tracking_info["unsubscribed"] = True
            tracking_info["unsubscribed_at"] = datetime.utcnow().isoformat()
            tracking_info["unsubscribe_reason"] = unsubscribe_reason
            
            logger.info(
                "Email unsubscribe tracked",
                tracking_id=tracking_id,
                to_email=tracking_info["to_email"],
                unsubscribe_reason=unsubscribe_reason,
            )
            
            return {
                "success": True,
                "tracking_id": tracking_id,
                "unsubscribe_reason": unsubscribe_reason,
            }
            
        except Exception as e:
            logger.error(f"Failed to track email unsubscribe: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_tracking_info(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Get tracking information for an email."""
        return self.tracking_data.get(tracking_id)
    
    async def get_email_analytics(
        self,
        plaintiff_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get email analytics.
        
        Args:
            plaintiff_id: Optional filter by plaintiff ID.
            date_from: Optional start date filter.
            date_to: Optional end date filter.
            
        Returns:
            dict: Email analytics data.
        """
        try:
            filtered_data = []
            
            for tracking_info in self.tracking_data.values():
                # Apply filters
                if plaintiff_id and tracking_info.get("plaintiff_id") != plaintiff_id:
                    continue
                
                sent_at = datetime.fromisoformat(tracking_info["sent_at"])
                
                if date_from and sent_at < date_from:
                    continue
                
                if date_to and sent_at > date_to:
                    continue
                
                filtered_data.append(tracking_info)
            
            # Calculate analytics
            total_sent = len(filtered_data)
            total_opened = sum(1 for data in filtered_data if data["opened_at"])
            total_clicked = sum(1 for data in filtered_data if data["clicked_at"])
            total_bounced = sum(1 for data in filtered_data if data["bounced"])
            total_unsubscribed = sum(1 for data in filtered_data if data["unsubscribed"])
            
            # Calculate rates
            open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
            click_rate = (total_clicked / total_sent * 100) if total_sent > 0 else 0
            bounce_rate = (total_bounced / total_sent * 100) if total_sent > 0 else 0
            unsubscribe_rate = (total_unsubscribed / total_sent * 100) if total_sent > 0 else 0
            
            # Click-to-open rate
            click_to_open_rate = (total_clicked / total_opened * 100) if total_opened > 0 else 0
            
            return {
                "total_sent": total_sent,
                "total_opened": total_opened,
                "total_clicked": total_clicked,
                "total_bounced": total_bounced,
                "total_unsubscribed": total_unsubscribed,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "click_to_open_rate": round(click_to_open_rate, 2),
                "bounce_rate": round(bounce_rate, 2),
                "unsubscribe_rate": round(unsubscribe_rate, 2),
                "period": {
                    "from": date_from.isoformat() if date_from else None,
                    "to": date_to.isoformat() if date_to else None,
                },
            }
            
        except Exception as e:
            logger.error(f"Failed to get email analytics: {e}")
            return {
                "error": str(e),
            }
    
    async def get_top_clicked_links(
        self,
        limit: int = 10,
        plaintiff_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top clicked links from emails.
        
        Args:
            limit: Maximum number of links to return.
            plaintiff_id: Optional filter by plaintiff ID.
            
        Returns:
            list: Top clicked links with click counts.
        """
        try:
            link_clicks = {}
            
            for tracking_info in self.tracking_data.values():
                if plaintiff_id and tracking_info.get("plaintiff_id") != plaintiff_id:
                    continue
                
                for click_event in tracking_info.get("click_events", []):
                    url = click_event["url"]
                    if url not in link_clicks:
                        link_clicks[url] = {
                            "url": url,
                            "click_count": 0,
                            "unique_clickers": set(),
                        }
                    
                    link_clicks[url]["click_count"] += 1
                    link_clicks[url]["unique_clickers"].add(tracking_info["to_email"])
            
            # Convert to list and sort by click count
            top_links = []
            for link_data in link_clicks.values():
                top_links.append({
                    "url": link_data["url"],
                    "click_count": link_data["click_count"],
                    "unique_clickers": len(link_data["unique_clickers"]),
                })
            
            top_links.sort(key=lambda x: x["click_count"], reverse=True)
            
            return top_links[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top clicked links: {e}")
            return []
    
    def cleanup_old_tracking_data(self, days: int = 90) -> Dict[str, Any]:
        """
        Clean up tracking data older than specified days.
        
        Args:
            days: Number of days to retain data.
            
        Returns:
            dict: Cleanup result.
        """
        try:
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            cleaned_count = 0
            tracking_ids_to_remove = []
            
            for tracking_id, tracking_info in self.tracking_data.items():
                sent_at = datetime.fromisoformat(tracking_info["sent_at"])
                if sent_at < cutoff_date:
                    tracking_ids_to_remove.append(tracking_id)
            
            for tracking_id in tracking_ids_to_remove:
                del self.tracking_data[tracking_id]
                cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old tracking records")
            
            return {
                "success": True,
                "cleaned_count": cleaned_count,
                "cutoff_date": cutoff_date.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup tracking data: {e}")
            return {
                "success": False,
                "error": str(e),
            }
"""Pipedrive API client with rate limiting and error handling."""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class PipedriveAPIError(Exception):
    """Exception raised for Pipedrive API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AsyncRateLimiter:
    """Async rate limiter for API requests."""
    
    def __init__(self, max_calls: int, period: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed.
            period: Time period in seconds.
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire rate limit permission."""
        async with self.lock:
            now = datetime.utcnow()
            
            # Remove old calls outside the time window
            cutoff = now - timedelta(seconds=self.period)
            self.calls = [call_time for call_time in self.calls if call_time > cutoff]
            
            # Check if we can make a new call
            if len(self.calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_time = (oldest_call + timedelta(seconds=self.period) - now).total_seconds()
                
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # Record this call
            self.calls.append(now)


class PipedriveClient:
    """
    Pipedrive API client with comprehensive error handling and rate limiting.
    
    Implements the rate limiting requirements from the PRP (100 requests per 10 seconds)
    with proper retry logic and connection pooling.
    """
    
    def __init__(self, api_token: str = None, company_domain: str = None):
        """
        Initialize Pipedrive client.
        
        Args:
            api_token: Pipedrive API token (uses settings if not provided).
            company_domain: Company domain (uses settings if not provided).
        """
        settings = get_settings()
        
        self.api_token = api_token or settings.pipedrive.api_token
        self.company_domain = company_domain or settings.pipedrive.company_domain
        self.base_url = f"https://{self.company_domain}.pipedrive.com/api/v1"
        
        # Rate limiter - 90 requests per 10 seconds (buffer for safety)
        self.rate_limiter = AsyncRateLimiter(
            max_calls=settings.pipedrive.rate_limit_per_10_seconds,
            period=10
        )
        
        # HTTP session configuration
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=20,  # Connection pool size
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": "AI-CRM-Multi-Agent/1.0",
                "Accept": "application/json",
            }
        )
        
        logger.info(
            "Pipedrive client initialized",
            company_domain=self.company_domain,
            base_url=self.base_url,
        )
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to Pipedrive API with rate limiting and retries.
        
        Args:
            method: HTTP method.
            endpoint: API endpoint.
            params: Query parameters.
            data: Request body data.
            retry_count: Current retry attempt.
            max_retries: Maximum retry attempts.
            
        Returns:
            dict: API response data.
            
        Raises:
            PipedriveAPIError: For API errors.
            RateLimitError: For rate limiting errors.
        """
        # Acquire rate limit permission
        await self.rate_limiter.acquire()
        
        # Prepare request
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        request_params = params or {}
        request_params['api_token'] = self.api_token
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=request_params,
                json=data if data else None,
            ) as response:
                
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 10))
                    
                    if retry_count < max_retries:
                        logger.warning(
                            f"Rate limited, retrying after {retry_after}s",
                            retry_count=retry_count,
                            endpoint=endpoint,
                        )
                        await asyncio.sleep(retry_after)
                        return await self._make_request(
                            method, endpoint, params, data, retry_count + 1, max_retries
                        )
                    else:
                        raise RateLimitError(f"Rate limit exceeded after {max_retries} retries")
                
                # Handle authentication errors
                if response.status == 401:
                    raise PipedriveAPIError(
                        "Invalid API token or insufficient permissions",
                        status_code=401
                    )
                
                # Handle other client errors
                if 400 <= response.status < 500:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_message = error_data.get('error', f"Client error: {response.status}")
                    raise PipedriveAPIError(
                        error_message,
                        status_code=response.status,
                        response_data=error_data
                    )
                
                # Handle server errors with retry
                if response.status >= 500:
                    if retry_count < max_retries:
                        delay = 2 ** retry_count  # Exponential backoff
                        logger.warning(
                            f"Server error {response.status}, retrying in {delay}s",
                            retry_count=retry_count,
                            endpoint=endpoint,
                        )
                        await asyncio.sleep(delay)
                        return await self._make_request(
                            method, endpoint, params, data, retry_count + 1, max_retries
                        )
                    else:
                        raise PipedriveAPIError(
                            f"Server error: {response.status}",
                            status_code=response.status
                        )
                
                # Parse successful response
                if response.content_type == 'application/json':
                    result = await response.json()
                    
                    # Check for API-level errors
                    if not result.get('success', True):
                        error_message = result.get('error', 'Unknown API error')
                        raise PipedriveAPIError(error_message, response_data=result)
                    
                    return result
                else:
                    return {"success": True, "data": await response.text()}
                
        except aiohttp.ClientError as e:
            if retry_count < max_retries:
                delay = 2 ** retry_count
                logger.warning(
                    f"Connection error, retrying in {delay}s: {e}",
                    retry_count=retry_count,
                )
                await asyncio.sleep(delay)
                return await self._make_request(
                    method, endpoint, params, data, retry_count + 1, max_retries
                )
            else:
                raise PipedriveAPIError(f"Connection error: {e}")
    
    # Person API methods
    async def get_persons(
        self,
        limit: int = 100,
        start: int = 0,
        search_term: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get persons from Pipedrive."""
        params = {"limit": limit, "start": start}
        if search_term:
            params["term"] = search_term
        
        return await self._make_request("GET", "/persons", params=params)
    
    async def get_person(self, person_id: int) -> Dict[str, Any]:
        """Get a specific person by ID."""
        return await self._make_request("GET", f"/persons/{person_id}")
    
    async def create_person(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new person."""
        return await self._make_request("POST", "/persons", data=person_data)
    
    async def update_person(self, person_id: int, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing person."""
        return await self._make_request("PUT", f"/persons/{person_id}", data=person_data)
    
    async def delete_person(self, person_id: int) -> Dict[str, Any]:
        """Delete a person."""
        return await self._make_request("DELETE", f"/persons/{person_id}")
    
    # Organization API methods
    async def get_organizations(
        self,
        limit: int = 100,
        start: int = 0,
        search_term: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get organizations from Pipedrive."""
        params = {"limit": limit, "start": start}
        if search_term:
            params["term"] = search_term
        
        return await self._make_request("GET", "/organizations", params=params)
    
    async def get_organization(self, org_id: int) -> Dict[str, Any]:
        """Get a specific organization by ID."""
        return await self._make_request("GET", f"/organizations/{org_id}")
    
    async def create_organization(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization."""
        return await self._make_request("POST", "/organizations", data=org_data)
    
    async def update_organization(self, org_id: int, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing organization."""
        return await self._make_request("PUT", f"/organizations/{org_id}", data=org_data)
    
    # Deal API methods
    async def get_deals(
        self,
        limit: int = 100,
        start: int = 0,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get deals from Pipedrive."""
        params = {"limit": limit, "start": start}
        if status:
            params["status"] = status
        
        return await self._make_request("GET", "/deals", params=params)
    
    async def get_deal(self, deal_id: int) -> Dict[str, Any]:
        """Get a specific deal by ID."""
        return await self._make_request("GET", f"/deals/{deal_id}")
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal."""
        return await self._make_request("POST", "/deals", data=deal_data)
    
    async def update_deal(self, deal_id: int, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal."""
        return await self._make_request("PUT", f"/deals/{deal_id}", data=deal_data)
    
    # Activity API methods
    async def get_activities(
        self,
        limit: int = 100,
        start: int = 0,
        person_id: Optional[int] = None,
        deal_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get activities from Pipedrive."""
        params = {"limit": limit, "start": start}
        if person_id:
            params["person_id"] = person_id
        if deal_id:
            params["deal_id"] = deal_id
        
        return await self._make_request("GET", "/activities", params=params)
    
    async def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity."""
        return await self._make_request("POST", "/activities", data=activity_data)
    
    # Note API methods
    async def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new note."""
        return await self._make_request("POST", "/notes", data=note_data)
    
    # Custom fields API methods
    async def get_person_fields(self) -> Dict[str, Any]:
        """Get custom fields for persons."""
        return await self._make_request("GET", "/personFields")
    
    async def get_deal_fields(self) -> Dict[str, Any]:
        """Get custom fields for deals."""
        return await self._make_request("GET", "/dealFields")
    
    async def get_organization_fields(self) -> Dict[str, Any]:
        """Get custom fields for organizations."""
        return await self._make_request("GET", "/organizationFields")
    
    # Webhook API methods
    async def get_webhooks(self) -> Dict[str, Any]:
        """Get configured webhooks."""
        return await self._make_request("GET", "/webhooks")
    
    async def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook."""
        return await self._make_request("POST", "/webhooks", data=webhook_data)
    
    async def delete_webhook(self, webhook_id: int) -> Dict[str, Any]:
        """Delete a webhook."""
        return await self._make_request("DELETE", f"/webhooks/{webhook_id}")
    
    # Health check
    async def health_check(self) -> bool:
        """
        Check if Pipedrive API is accessible.
        
        Returns:
            bool: True if API is accessible.
        """
        try:
            result = await self._make_request("GET", "/users/me")
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Pipedrive health check failed: {e}")
            return False
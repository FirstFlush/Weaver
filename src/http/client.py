import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp
from aiohttp import ClientError
from .dataclasses import RequestConfig


logger = logging.getLogger(__name__)


class HttpClientError(Exception):
    """Custom exception for API client errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class HttpClient:
    """Async HTTP client with persistent session for API requests."""
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the HTTP session."""
        if not self.session.closed:
            await self.session.close()
    
    async def request(self, config: RequestConfig) -> Dict[str, Any]:
        """Make HTTP request using RequestConfig."""
        request_kwargs = {
            'headers': config.headers,
            'params': config.params,
            **config.kwargs
        }
        
        if config.json_data:
            request_kwargs['json'] = config.json_data
        if config.data:
            request_kwargs['data'] = config.data
        if config.timeout:
            request_kwargs['timeout'] = aiohttp.ClientTimeout(total=config.timeout)
        
        for attempt in range(config.max_retries + 1):
            try:
                logger.debug(f"Making {config.method} request to {config.url} (attempt {attempt + 1})")
                
                async with self.session.request(config.method, config.url, **request_kwargs) as response:
                    response_text = await response.text()
                    
                    response_data = {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'text': response_text,
                        'url': str(response.url)
                    }
                    
                    if response.status >= 400:
                        error_msg = f"HTTP {response.status} error for {config.method} {config.url}"
                        logger.error(f"{error_msg}: {response_text}")
                        raise HttpClientError(
                            error_msg,
                            status_code=response.status,
                            response_text=response_text
                        )
                    
                    logger.debug(f"Request successful: {config.method} {config.url} -> {response.status}")
                    return response_data
                    
            except (ClientError, asyncio.TimeoutError) as e:
                error_msg = f"Network error on {config.method} {config.url}: {str(e)}"
                
                if attempt == config.max_retries:
                    logger.error(f"{error_msg} (final attempt)")
                    raise HttpClientError(error_msg) from e
                
                logger.warning(f"{error_msg} (attempt {attempt + 1}/{config.max_retries + 1})")
                await asyncio.sleep(config.retry_delay * (2 ** attempt))
          
        msg = f"{self.__class__.__name__} failed due to an unexpected error"
        logger.error(msg)
        raise HttpClientError(msg)
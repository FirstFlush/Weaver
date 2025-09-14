import asyncio
import logging
import aiohttp
from aiohttp import ClientResponse
from aiohttp import ClientError
from .dataclasses import RequestConfig, HttpConfig
from .exc import HttpClientError


logger = logging.getLogger(__name__)


class HttpClient:
    """Async HTTP client with persistent session for API requests."""
    
    def __init__(self, config: HttpConfig):
        self.config = config
        self.session = aiohttp.ClientSession()
            
    async def close(self):
        """Close the HTTP session."""
        if self.session is not None and not self.session.closed:
            await self.session.close()
    
    async def request(self, config: RequestConfig) -> ClientResponse:
        """Make HTTP request using RequestConfig."""
        headers = config.headers if config.headers is not None else self.config.headers
        request_kwargs = {
            'headers': headers,
            'params': config.params,
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
                    if response.status >= 400:
                        response_text = await response.text()
                        error_msg = f"HTTP {response.status} error for {config.method} {config.url}"
                        logger.error(f"{error_msg}: {response_text}")
                        raise HttpClientError(
                            error_msg,
                            status_code=response.status,
                            response_text=response_text
                        )
                    logger.debug(f"Request successful: {config.method} {config.url} -> {response.status}")
                    return response
                    
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
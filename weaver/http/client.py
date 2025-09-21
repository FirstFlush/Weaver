import asyncio
import logging
from curl_cffi.requests import AsyncSession, Response, RequestsError
from .dataclasses import RequestConfig, HttpConfig
from .exc import HttpClientError
from ..proxy.manager import ProxyManager

logger = logging.getLogger(__name__)


class HttpClient:
    """Async HTTP client with persistent session for API requests."""
    
    def __init__(self, config: HttpConfig, proxy_manager: ProxyManager | None = None):
        self._config = config
        self._proxy_manager = proxy_manager 
        self._session = AsyncSession()

    async def request(self, config: RequestConfig) -> tuple[int, str]:
        """Convenience method that returns (status, text) and handles cleanup."""
        response = None
        try:
            response = await self.request_raw(config) 
        except HttpClientError:
            raise
        except Exception as e:
            msg = f"{self.__class__.__name__} can not complete request due to an unexpected error: {e}"
            logger.error(msg, exc_info=True)
            raise HttpClientError(msg) from e
        else:
            return response.status_code, response.text
        finally:
            if response is not None:
                response.close()

    async def request_raw(self, config: RequestConfig) -> Response:
        """Return raw aiohttp ClientResponse. User must manage closing."""        
        for attempt in range(config.max_retries + 1):
            try:
                logger.debug(f"Making {config.method} request to {config.url} (attempt {attempt + 1})")
                
                response = await self._make_single_request(config)
                
                logger.debug(f"Request successful: {config.method} {config.url} -> {response.status_code}")
                return response
                
            except (RequestsError, asyncio.TimeoutError) as e:
                self._handle_network_error(e, config, attempt)
                await asyncio.sleep(config.retry_delay * (2 ** attempt))
          
        msg = f"{self.__class__.__name__} failed due to an unexpected error"
        logger.error(msg)
        raise HttpClientError(msg)
    
    async def close(self):
        """Close the HTTP session."""
        if self._session is not None:
            await self._session.close()
    
    def _build_request_kwargs(self, config: RequestConfig) -> dict:
        """Build request kwargs from config expected by curl-cffi request."""
        headers = config.headers if config.headers is not None else self._config.headers
        cookies = config.cookies if config.cookies is not None else self._config.cookies
        timeout = config.timeout if config.timeout is not None else self._config.timeout
        impersonate = config.impersonate if config.impersonate is not None else self._config.impersonate
        request_kwargs = {
            'headers': headers,
            'cookies': cookies,
            'timeout': timeout,
            'impersonate': impersonate,
            'params': config.params,
            'data': config.data,
            'json': config.json,
        }
        return config.extra_kwargs | request_kwargs
    
    async def _handle_error_response(self, response: Response, config: RequestConfig):
        """Handle HTTP error responses."""
        error_msg = f"HTTP {response.status_code} error for {config.method} {config.url}"
        logger.error(f"{error_msg}: {response.text}")
        raise HttpClientError(
            error_msg,
            status_code=response.status_code,
            response_text=response.text,
        )
    
    def _handle_network_error(self, e: Exception, config: RequestConfig, attempt: int):
        """Handle network errors and retries."""
        error_msg = f"Network error on {config.method} {config.url}: {str(e)}"
        if attempt == config.max_retries:
            logger.error(f"{error_msg} (final attempt)")
            raise HttpClientError(error_msg) from e
        
        logger.warning(f"{error_msg} (attempt {attempt + 1}/{config.max_retries + 1})")
    
    async def _make_single_request(self, config: RequestConfig) -> Response:
        request_kwargs = self._build_request_kwargs(config)
        response: Response = await self._session.request(config.method, config.url, **request_kwargs)
        if response.status_code >= 400:
            await self._handle_error_response(response, config)
        
        return response


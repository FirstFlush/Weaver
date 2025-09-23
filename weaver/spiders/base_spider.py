from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager
import logging
import random
from ..browser.client import BrowserClient
from ..browser.dataclasses import BrowserConfig
from ..browser.exc import BrowserClientError
from ..http.client import HttpClient
from ..http.dataclasses import HttpConfig
from ..http.exc import HttpClientError
from ..proxy.dataclasses import ProxyPool
from ..proxy.exc import ProxyError
from ..proxy.manager import ProxyManager
from .exc import BaseSpiderError

logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    
    def __init__(
            self,
            browser_config: BrowserConfig | None = None,
            http_config: HttpConfig | None = None,
            proxy_pool: ProxyPool | None = None,
    ):
        """
        Abstract base class for web scrapers providing unified access to
        HTTP and browser automation clients. Designed to be subclassed by
        custom spiders, it manages the lifecycle of a BrowserClient and/or
        HttpClient, including asynchronous initialization and cleanup 
        via async context management.

        Subclasses implement the `run()` method to define scraping logic.
        The async context ensures that resources such as aiohttp sessions 
        and Playwright browsers are properly created and closed.

        Note:
            Must be used with an async context (`async with`) to ensure
            proper creation and cleanup of browser and HTTP resources.
        """
        self._browser_config = browser_config
        self._http_config = http_config
        self._proxy_pool = proxy_pool
        self._proxy_manager = self._create_proxy_manager() if self._proxy_pool else None

        self.browser_client: BrowserClient | None = None
        self.http_client: HttpClient | None = None
        
        if not self._browser_config and not self._http_config:
            msg = f"{self.__class__.__name__} did not receive either BrowserConfig or HttpConfig. At least 1 is required."
            logger.error(msg)
            raise BaseSpiderError(msg)

    @asynccontextmanager
    async def execute(self, **params):
        """
        Public method called by ScrapingService. Do not call this directly as it handles
        the lifecycle of the spider. Put scraping logic in the run() method.
        """
        await self._setup()
        try:
            result = await self.run(**params)
            yield result
        finally:
            await self._cleanup()

    @abstractmethod
    async def run(self, **kwargs):
        """
        Main entry point for the spider's scraping logic.

        Subclasses must implement this method to define how the spider
        interacts with the web, using the provided BrowserClient and/or
        HttpClient. It runs within the async context of the spider, so
        clients are guaranteed to be initialized and cleaned up properly.
        """
        pass

    async def jitter(self, low: float = 0.2, high: float = 1.2):
        await asyncio.sleep(random.uniform(low, high))


    def _create_proxy_manager(self) -> ProxyManager:
        if not self._proxy_pool:
            msg = f"{self.__class__.__name__} can not create ProxyManager. ProxyPool not found`{type(self._proxy_pool)}`"
            logger.error(msg, exc_info=True)
            raise ProxyError(msg)
        
        return ProxyManager(proxy_pool=self._proxy_pool)


    async def _setup(self):
        try:
            if self._browser_config is not None:
                self.browser_client = await BrowserClient.create(self._browser_config)
        except Exception as e:
            msg = f"Failed to start BrowserClient due to unexpected error: {e}"
            logger.error(msg, exc_info=True)
            raise BrowserClientError(msg)
        
        try:
            if self._http_config:
                self.http_client = HttpClient(self._http_config)
        except Exception as e:
            msg = f"Failed to start HttpClient due to unexpected error: {e}"
            logger.error(msg, exc_info=True)
            raise HttpClientError(msg)
        
    async def _cleanup(self):
        try:
            if self.browser_client:
                await self.browser_client.close()
        except Exception:
            logger.warning("BrowserClient.close() raised an error but was suppressed") 
       
        try:
            if self.http_client:
                await self.http_client.close()
        except Exception:
            logger.warning("HttpClient.close() raised an error but was suppressed")







    # async def __aenter__(self) -> "BaseSpider":
    #     try:
    #         if self._browser_config is not None:
    #             self.browser_client = await BrowserClient.create(self._browser_config)
    #     except Exception as e:
    #         msg = f"Failed to start BrowserClient due to unexpected error: {e}"
    #         logger.error(msg, exc_info=True)
    #         raise BrowserClientError(msg)
        
    #     try:
    #         if self._http_config:
    #             self.http_client = HttpClient(self._http_config)
    #     except Exception as e:
    #         msg = f"Failed to start HttpClient due to unexpected error: {e}"
    #         logger.error(msg, exc_info=True)
    #         raise HttpClientError(msg)
        
    #     return self
    
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #     try:
    #         if self.browser_client:
    #             await self.browser_client.close()
    #     except Exception:
    #         logger.warning("BrowserClient.close() raised an error but was suppressed") 
       
    #     try:
    #         if self.http_client:
    #             await self.http_client.close()
    #     except Exception:
    #         logger.warning("HttpClient.close() raised an error but was suppressed")
from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager
import logging
import random
from typing import Any, AsyncGenerator
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
    async def execute(self, **params) -> AsyncGenerator[Any, None]:
        """
        Entry point used by orchestration or job-runner services to perform a
        full scraping session. Handles resource lifecycle (setup / teardown)
        for the spider’s HTTP and browser clients, then yields the async
        generator returned by `run()`.

        Usage:
            async with spider.execute(**params) as results:
                async for record in results:
                    ...

        This method should never contain scraping logic itself—only the
        lifecycle control around `run()`.
        """
        await self._setup()
        try:
            yield self.run(**params)
        finally:
            await self._cleanup()

    @abstractmethod
    async def run(self, **kwargs) -> AsyncGenerator[Any, None]:
        """
        This is where you write the core scraping logic for a specific spider subclass.

        This coroutine should yield one record at a time as data is scraped.
        It is called within the `execute()` context, which handles setup and
        teardown of any resources the spider depends on.
        """
        raise NotImplementedError("Subclasses must override run() and yield an async generator object.")

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





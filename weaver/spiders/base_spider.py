from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager
import logging
import random
from typing import Any, AsyncGenerator
from ..browser.client import BrowserClient
from ..http.client import HttpClient
from ..proxy.manager import ProxyManager
from .exc import BaseSpiderError

logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    
    def __init__(
            self,
            browser_client: BrowserClient | None = None,
            http_client: HttpClient | None = None,
            proxy_manager: ProxyManager | None = None,
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
        self.browser_client = browser_client
        self.http_client = http_client
        self.proxy_manager = proxy_manager

        if not self.browser_client and not self.http_client:
            msg = f"{self.__class__.__name__} did not receive either BrowserClient or HttpClient. At least 1 is required."
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

    async def _setup(self):
        pass

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

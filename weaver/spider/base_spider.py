from abc import ABC, abstractmethod
import asyncio
import logging
import random
from typing import Any, AsyncGenerator
from ..browser.client import BrowserClient
from ..http.client import HttpClient
from ..proxy.manager import ProxyManager
from .exc import SpiderError
from .types import SpiderMode

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BaseSpider(ABC):
    
    MODE: SpiderMode

    def __init__(
            self,
            browser_client: BrowserClient | None = None,
            http_client: HttpClient | None = None,
            proxy_manager: ProxyManager | None = None,
    ):
        """
        Abstract base class for all web spiders.

        Provides a unified interface to optional HTTP and browser clients, allowing
        subclasses to focus purely on scraping logic. Each subclass implements `run()`,
        which asynchronously yields scraped records one at a time.

        The base class itself does not manage client lifecycles; that responsibility
        belongs to `SpiderRunner`, which constructs the spider, executes `run()`, and
        handles cleanup.
        """
        self.browser_client = browser_client
        self.http_client = http_client
        self.proxy_manager = proxy_manager

        if not self.browser_client and not self.http_client:
            msg = f"{self.__class__.__name__} did not receive either BrowserClient or HttpClient. At least 1 is required."
            logger.error(msg)
            raise SpiderError(msg)

    @abstractmethod
    async def run(self, **kwargs: Any) -> AsyncGenerator[Any, None]:
        """Should yield one record at a time."""
        if False:  # pragma: no cover
            yield None
        raise NotImplementedError

    async def jitter(self, low: float = 0.2, high: float = 1.2):
        await asyncio.sleep(random.uniform(low, high))

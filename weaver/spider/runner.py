from contextlib import asynccontextmanager
import logging
from typing import (
    Any, 
    Type, 
    TYPE_CHECKING, 
    get_args, 
    AsyncGenerator
)
from ..browser.client import BrowserClient
from ..browser.dataclasses import BrowserConfig
from ..browser.exc import BrowserClientError
from ..common.exc import WeaverError
from ..http.client import HttpClient
from ..http.dataclasses import HttpConfig
from ..http.exc import HttpClientError
from ..proxy.dataclasses import ProxyPool
from ..proxy.manager import ProxyManager
from .dataclasses import SpiderConfig
from .exc import SpiderError
from .types import SpiderMode

if TYPE_CHECKING:
    from .base_spider import BaseSpider

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SpiderRunner:
    """
    Orchestrates the full lifecycle of a spider.

    Responsible for constructing the appropriate clients (HTTP, browser, proxy),
    executing the spider’s `run()` coroutine, and streaming its results. Ensures
    that all resources are properly initialized and cleaned up, isolating lifecycle
    management from scraping logic.

    Typical usage:
        async for record in SpiderRunner().scrape(MySpider, **params):
            await queue.put(record)
    """
    def __init__(self, spider_config: SpiderConfig | None = None):
        self.spider_config = spider_config or SpiderConfig()

    async def scrape(
        self,
        spider_cls: Type[BaseSpider],
        **params: Any,
    ) -> AsyncGenerator[Any, None]:
        """
        Builds and runs the spider, yielding scraped records one at a time.
        Handles setup/teardown around the spider lifecycle.
        """
        try:
            spider = await self._build_spider(spider_cls)
        except Exception as e:
            msg = f"Failed to build spider for class {spider_cls.__name__} due to the following error {e}"
            logger.error(msg, exc_info=True)
            raise WeaverError(msg)

        try:
            async for record in spider.run(**params):
                yield record
        except Exception as e:
            msg = f"Scraping failed due to the following error: {e}"
            logger.error(msg, exc_info=True)
            raise WeaverError(msg) from e

        finally:
            try:
                await self._cleanup(spider)
            except Exception as e:
                msg = f"Failed cleanup for spider {spider.__class__.__name__} due to the following error: {e}"
                logger.error(msg, exc_info=True)
                raise WeaverError(msg)

    async def _build_spider(self, spider_cls: Type["BaseSpider"]) -> BaseSpider:
        mode = getattr(spider_cls, "MODE", None)
        if mode not in get_args(SpiderMode):
            raise SpiderError(f"{spider_cls.__name__} must define valid MODE attribute [ browser | http | hybrid ]")

        browser_client = None
        http_client = None
        proxy_manager = self._build_proxy()

        if mode in ("browser", "hybrid"):
            browser_client = await self._build_browser()

        if mode in ("http", "hybrid"):
            http_client = self._build_http()

        return spider_cls(
            browser_client=browser_client,
            http_client=http_client,
            proxy_manager=proxy_manager,
        )

    async def _build_browser(self) -> BrowserClient | None:
        cfg = self.spider_config.browser
        if not cfg:
            return None
        try:
            if isinstance(cfg, BrowserConfig):
                return await BrowserClient.create(cfg)
        except Exception as e:
            msg = f"Failed to start BrowserClient: {e}"
            logger.error(msg, exc_info=True)
            raise BrowserClientError(msg)

    def _build_http(self) -> HttpClient | None:
        cfg = self.spider_config.http
        if not cfg:
            return None
        try:
            if isinstance(cfg, HttpConfig):
                return HttpClient(cfg)
        except Exception as e:
            msg = f"Failed to start HttpClient: {e}"
            logger.error(msg, exc_info=True)
            raise HttpClientError(msg)

    def _build_proxy(self) -> ProxyManager | None:
        pool = self.spider_config.proxy_pool
        if isinstance(pool, ProxyPool):
            return ProxyManager(proxy_pool=pool)
        return None

    async def _cleanup(self, spider: BaseSpider):
        try:
            if spider.browser_client:
                await spider.browser_client.close()
        except BrowserClientError:
            raise
        except Exception as e:
            msg = f"Failed to close BrowserClient due to the following error: {e}"
            logger.error(msg, exc_info=True)
            raise BrowserClientError(msg) from e

        try:
            if spider.http_client:
                await spider.http_client.close()
        except HttpClientError:
            raise
        except Exception as e:
            msg = f"failed to close HttpClient due to the following error: {e}"
            logger.error(msg, exc_info=True)
            raise HttpClientError(msg) from e
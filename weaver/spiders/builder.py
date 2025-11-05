import logging
from typing import Type, TYPE_CHECKING, get_args
from ..browser.client import BrowserClient
from ..browser.dataclasses import BrowserConfig
from ..browser.exc import BrowserClientError
from ..http.client import HttpClient
from ..http.dataclasses import HttpConfig
from ..http.exc import HttpClientError
from ..proxy.dataclasses import ProxyPool
from ..proxy.manager import ProxyManager
from .dataclasses import SpiderConfig
from .exc import BaseSpiderError
from .types import SpiderMode

if TYPE_CHECKING:
    from .base_spider import BaseSpider

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SpiderBuilder:
    """Constructs spider instances with appropriate clients based on MODE."""

    def __init__(self, spider_config: SpiderConfig | None = None):
        self.spider_config = spider_config or SpiderConfig()

    async def build_spider(self, spider_cls: Type["BaseSpider"]) -> "BaseSpider":
        mode = getattr(spider_cls, "MODE", None)
        if mode not in get_args(SpiderMode):
            raise BaseSpiderError(f"{spider_cls.__name__} must define valid MODE attribute [ browser | http | hybrid ]")

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

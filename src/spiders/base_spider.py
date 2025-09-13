from abc import ABC
from ..http.client import HttpClient
from ..browser.client import BrowserClient
from ..browser.dataclasses import BrowserConfig


class BaseSpider(ABC):
    
    def __init__(
        self, 
        http_client: HttpClient | None = None,
        browser_config: BrowserConfig | None = None,
    ):
        if http_client is None:
            http_client = HttpClient()
        self.http_client = http_client

        self._browser_client: BrowserClient | None = None
        self._browser_config = browser_config or BrowserConfig()
        
    async def browser_client(self) -> BrowserClient:
        """Get browser client, initializing if needed."""
        if not self._browser_client:
            self._browser_client = await BrowserClient.create(self._browser_config)
        return self._browser_client

    async def cleanup(self):
        if self._browser_client is not None:
            await self._browser_client.close()
        await self.http_client.close()
        
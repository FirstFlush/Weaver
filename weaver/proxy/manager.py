import logging
from asyncio import Semaphore
from .exc import ProxyError
from .dataclasses import ProxyPool

logger = logging.getLogger(__name__)

class ProxyManager:

    _static_endpoint_pool: set[str] = set()

    def __init__(self, proxy_pool: ProxyPool):
        self.pool = proxy_pool
        self.semaphore = Semaphore(self.pool.max_connections)

    async def acquire_rotating(self) -> str:
        if self.pool.rotating_endpoint:
            await self._acquire(self.pool.rotating_endpoint)
            return self.pool.rotating_endpoint
        raise RuntimeError(f"Can not acquire rotating proxy endpoint. No rotating endpoint defined in {self.pool.__class__.__name__}!")

    async def acquire_static(self) -> str:
        if self.pool.static_endpoints:
            await self.semaphore.acquire()
            endpoint = self._get_static_endpoint()
            self._static_endpoint_pool.add(endpoint)
            return endpoint
        raise RuntimeError(f"Can not acquire static proxy endpoint. No static endpoints defined in {self.pool.__class__.__name__}!")

    async def _acquire(self, endpoint: str):
        await self.semaphore.acquire()
        logger.debug(f"Semaphore acquired for endpoint {endpoint}")

    def _get_static_endpoint(self) -> str:
        if self.pool.static_endpoints:
            for endpoint in self.pool.static_endpoints:
                if endpoint not in self._static_endpoint_pool:
                    logger.debug(f"Static endpoint selected: {endpoint}")
                    return endpoint
        msg = f"{self.__class__.__name__} could not find any available static endpoints! Static endpoint pool size: `{len(self._static_endpoint_pool)}`"
        logger.error(msg, exc_info=True)
        raise ProxyError(msg)

    def playwright_proxy_credentials(self, proxy_endpoint: str) -> dict[str, str]:
        """Build dict of proxy crendentials in the format Playwright expects"""
        return {
            "server": proxy_endpoint,
            "username": self.pool.username,
            "password": self.pool.password,
        }
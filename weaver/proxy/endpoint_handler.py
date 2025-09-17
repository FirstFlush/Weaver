import logging
from asyncio import Semaphore
from .exc import ProxyError

logger = logging.getLogger(__name__)

class ProxyEndpointHandler:

    _static_endpoint_pool: set[str] = set()
    
    def __init__(self, semaphore: Semaphore):
        self.semaphore = semaphore
        
    async def request_rotating(self, endpoint: str):
        await self._acquire(endpoint)
        
    async def request_static(self, endpoints: list[str]):
        await self.semaphore.acquire()
        endpoint = self._get_static_endpoint(endpoints)
        self._static_endpoint_pool.add(endpoint)

    async def _acquire(self, endpoint: str):
        await self.semaphore.acquire()
        logger.debug(f"Semaphore acquired for endpoint {endpoint}")

    def _get_static_endpoint(self, endpoints: list[str]) -> str:
        for endpoint in endpoints:
            if endpoint not in self._static_endpoint_pool:
                logger.debug(f"Static endpoint selected: {endpoint}")
                return endpoint
        msg = f"{self.__class__.__name__} could not find any available static endpoints! Static endpoint pool size: `{len(self._static_endpoint_pool)}`"
        logger.error(msg, exc_info=True)
        raise ProxyError(msg)


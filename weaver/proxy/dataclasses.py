from asyncio import Semaphore
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProxyConfig:
    server: str
    username: str
    password: str
    # semaphore: Semaphore
    # rotating_endpoint: Optional[str] = None
    # static_endpoints: Optional[list[str]] = None
    

@dataclass
class ProxyPool:
    semaphore: Semaphore
    rotating_endpoint: Optional[str] = None
    static_endpoints: Optional[list[str]] = None

    def __post_init__(self):
        if not self.rotating_endpoint and not self.static_endpoints:
            raise ValueError(f"Must specify at least one of rotating_endpoint or static_endpoints for {self.__class__.__name__}")

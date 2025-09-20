from dataclasses import dataclass, field
from typing import Optional


# @dataclass
# class ProxyEndpoint:
#     endpoint: str
#     # username: str = ""
#     # password: str = ""


@dataclass 
class ProxyPool:
    max_connections: int
    username: str = ""
    password: str = ""
    rotating_endpoint: Optional[str] = None
    static_endpoints: Optional[list[str]] = None

    def __post_init__(self):
        if not self.rotating_endpoint and not self.static_endpoints:
            raise ValueError(f"Must specify at least one of rotating_endpoint or static_endpoints for {self.__class__.__name__}")
        if self.max_connections < 1:
            raise ValueError(f"max_connections must be greater than 1 for {self.__class__.__name__}")



# @dataclass
# class ProxyRequest:
#     rotating: bool
    
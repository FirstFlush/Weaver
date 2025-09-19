import aiohttp
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..common.utils import generate_default_headers
from ..proxy.dataclasses import ProxyConfig


@dataclass
class HttpConfig:
    headers: Optional[Dict[str, str]] = field(default_factory=lambda: generate_default_headers())    # default headers for all requests within a session
    cookies: Optional[Dict[str, str]] = None
    timeout: Optional[aiohttp.ClientTimeout] = None
    connector: Optional[aiohttp.BaseConnector] = None
    trust_env: bool = True
    proxy_config: Optional[ProxyConfig] = None

@dataclass
class RequestConfig:
    """Configuration for an HTTP request."""
    url: str
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None    # set headers per request. If this is none, will default to headers in HttpConfig
    params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[float] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    proxy_config: Optional[ProxyConfig] = None  # Per-request ProxyConfig will override HttpConfig ProxyConfig

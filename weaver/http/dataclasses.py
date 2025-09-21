from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from curl_cffi.requests.impersonate import BrowserTypeLiteral, DEFAULT_CHROME
from curl_cffi.requests.session import HttpMethod
from ..common.utils import generate_default_headers

@dataclass
class HttpConfig:
    headers: Optional[Dict[str, str]] = field(default_factory=lambda: generate_default_headers())    # default headers for all requests within a session
    cookies: Optional[Dict[str, str]] = None
    timeout: float = 30
    impersonate: BrowserTypeLiteral = DEFAULT_CHROME

@dataclass
class RequestConfig:
    """Configuration for an HTTP request."""
    url: str
    method: HttpMethod = 'GET'
    impersonate: Optional[BrowserTypeLiteral] = None
    headers: Optional[Dict[str, str]] = None    # set headers per request. If this is none, will default to headers in HttpConfig
    cookies: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[float] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    extra_kwargs: dict[str, Any] = field(default_factory=dict)
    proxy_endpoint: Optional[str] = None
    # proxy_config: Optional[ProxyConfig] = None  # Per-request ProxyConfig will override HttpConfig ProxyConfig

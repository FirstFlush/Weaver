from dataclasses import dataclass
from typing import Optional
from ..browser.dataclasses import BrowserConfig
from ..http.dataclasses import HttpConfig
from ..proxy.dataclasses import ProxyPool


@dataclass
class SpiderConfig:

    browser: Optional[BrowserConfig] = None
    http: Optional[HttpConfig] = None
    proxy_pool: Optional[ProxyPool] = None

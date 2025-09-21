from dataclasses import dataclass, field
import random
from typing import Any
from .constants import VIEWPORTS


@dataclass
class BrowserConfig:
    """Configuration for browser launch."""
    browser_type: str = 'chromium'  # chromium, firefox, webkit
    headless: bool = True
    launch_options: dict[str, Any] = field(default_factory=dict) # additional kwargs to be passed into playwright's Browser.launch()
    # proxy_config: Optional[ProxyConfig] = None


@dataclass 
class ContextConfig:
    """Configuration for browser context creation."""
    user_agent: str
    viewport: tuple[int, int] = field(default_factory=lambda: random.choice(VIEWPORTS)) # width, height
    ignore_https_errors: bool = False
    java_script_enabled: bool = True
    # proxy_config: Optional[ProxyConfig] = None

@dataclass 
class BrowserOverrideConfig:
    """Configuration for overriding Browser APIs"""
    window_history: int = field(default=10)
    languages: list[str] = field(default_factory=lambda: [ "en-US", "en" ])
    language: str = field(default="en-US")
    platform: str = field(default="Win32")
    webdriver: bool = False


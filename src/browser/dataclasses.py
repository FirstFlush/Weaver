from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BrowserConfig:
    """Configuration for browser launch."""
    browser_type: str = 'chromium'  # chromium, firefox, webkit
    headless: bool = True
    launch_options: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ContextConfig:
    """Configuration for browser context."""
    viewport: Optional[Dict[str, int]] = None
    user_agent: Optional[str] = None
    extra_http_headers: Optional[Dict[str, str]] = None
    ignore_https_errors: bool = False
    java_script_enabled: bool = True
    context_options: Dict[str, Any] = field(default_factory=dict)
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class RequestConfig:
    """Configuration for an HTTP request."""
    url: str
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[float] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    kwargs: Dict[str, Any] = field(default_factory=dict)

from typing import Optional
from ..common.exc import WeaverError


class HttpClientError(WeaverError):
    """Custom exception for API client errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
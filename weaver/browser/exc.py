from typing import Optional


class BrowserClientError(Exception):
    """Custom exception for browser client errors."""
    
    def __init__(self, message: str, page_url: Optional[str] = None):
        super().__init__(message)
        self.page_url = page_url
import logging
from typing import List
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext

from .dataclasses import BrowserConfig, ContextConfig
from .exc import BrowserClientError

logger = logging.getLogger(__name__)

class BrowserClient:
    """Async browser client using Playwright."""
    
    def __init__(self, playwright: Playwright, browser: Browser):
        self.playwright = playwright
        self.browser = browser
        self._open_contexts: List[BrowserContext] = []

    
    @classmethod
    async def create(cls, config: BrowserConfig | None = None) -> "BrowserClient":
        """Factory method to create BrowserClient with initialized playwright and browser."""
        if config is None:
            config = BrowserConfig()
        
        playwright = await cls._start_playwright()
        browser = await cls._start_browser(playwright, config)
        
        return cls(playwright, browser)
    
    @staticmethod
    async def _start_playwright() -> Playwright:
        """Start Playwright."""
        try:
            logger = logging.getLogger(__name__)
            logger.debug("Starting Playwright")
            return await async_playwright().start()
        except Exception as e:
            raise BrowserClientError(f"Failed to start Playwright: {e}")
    
    @staticmethod
    async def _start_browser(playwright: Playwright, config: BrowserConfig) -> Browser:
        """Start browser."""
        try:
            logger = logging.getLogger(__name__)
            browser_launcher = getattr(playwright, config.browser_type)
            
            launch_options = {
                'headless': config.headless,
                **config.launch_options
            }
            
            logger.debug(f"Launching {config.browser_type} browser")
            return await browser_launcher.launch(**launch_options)
        except Exception as e:
            raise BrowserClientError(f"Failed to start browser: {e}")
    
    async def close(self) -> None:
        """Close all contexts, browser, and Playwright."""
        try:
            for context in self._open_contexts:
                logger.debug("Closing browser context")
                await context.close()
            self._open_contexts.clear()
            
            logger.debug("Closing browser")
            await self.browser.close()
            
            logger.debug("Stopping Playwright")
            await self.playwright.stop()
            
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    async def new_context(self, config: ContextConfig | None = None) -> BrowserContext:
        """Create a new browser context and track it."""
        if config is None:
            config = ContextConfig()
        
        context_options = {
            **config.context_options
        }
        
        if config.viewport:
            context_options['viewport'] = config.viewport
        if config.user_agent:
            context_options['user_agent'] = config.user_agent
        if config.extra_http_headers:
            context_options['extra_http_headers'] = config.extra_http_headers
        if config.ignore_https_errors:
            context_options['ignore_https_errors'] = config.ignore_https_errors
        if not config.java_script_enabled:
            context_options['java_script_enabled'] = config.java_script_enabled
        
        logger.debug("Creating new browser context")
        context = await self.browser.new_context(**context_options)
        self._open_contexts.append(context)
        
        return context

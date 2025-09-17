import logging
from playwright.async_api import Page
import json
import random
from .dataclasses import BrowserOverrideConfig

logger = logging.getLogger(__name__)

class BrowserOverrideService:
    """
    Provides a centralized utility to inject JavaScript overrides into a browser
    context or page, modifying browser internals to spoof environment properties 
    and enable stealth behavior. This includes altering navigator properties, 
    mimicking non-automation behavior, and other browser API tweaks to reduce 
    detection by scripts or anti-bot measures.
    """
    def __init__(self, page: Page, config: BrowserOverrideConfig | None = None):
        self.page = page
        self.config = config if isinstance(config, BrowserOverrideConfig) else BrowserOverrideConfig()

    async def inject_overrides(self):
        """Set various config settings for a new SpiderPage object."""
        await self._set_webdriver()
        await self._set_window_history_length()
        await self._set_languages()
        await self._set_platform()       

    async def _set_platform(self):
        await self.page.add_init_script(f"""
            Object.defineProperty(navigator, 'platform', {{
               get: () => {json.dumps(self.config.platform)}                      
            }});
        """)

    async def _set_window_history_length(self):
        """Sets the window.history.length property to a fixed value from config"""
        await self.page.add_init_script(f"""
            Object.defineProperty(window.history, 'length', {{
                get: () => {json.dumps(self.config.window_history)},
                configurable: true
            }});
        """)

    # async def _get_plugins(self) -> str:
    #     """Returns a serialized string of the browser's actual plugin values.
    #     Running page.evaluate("navigator.plugins") returns a mostly-empty object.
    #     """
    #     plugins_json = await self.page.evaluate("""
    #         JSON.stringify(Object.fromEntries(Array.from(navigator.plugins).map(
    #             p => [p.name, {
    #                 name: p.name,
    #                 filename: p.filename,
    #                 description: p.description,
    #                 mimeTypeCount: p.length,
    #                 mimeTypes: Object.fromEntries(Array.from(p).map(
    #                     m => [m.type, { type: m.type, suffixes: m.suffixes, description: m.description }]
    #                 ))
    #             }]
    #         )));
    #     """)
    #     return plugins_json


    # async def _set_plugins(self):
    #     """Sets the navigator.plugins value. Now in headless mode plugins
    #     will actually show up.
    #     """
    #     await self.page.add_init_script("""
    #         Object.defineProperty(navigator, 'plugins', {
    #             get: () => (""" + f"{PLUGINS}" + """)
    #         });"""
    #     )


    async def _set_languages(self):
        """Sets the navigator.language and navigator.languages values"""
        await self.page.add_init_script(f"""
            Object.defineProperty(navigator, 'languages', {{
               get: () => {json.dumps(self.config.languages)}                         
            }});
            Object.defineProperty(navigator, 'language', {{
               get: () => {json.dumps(self.config.language)}                         
            }});
        """)

    async def _set_webdriver(self):
        """Sets the 'navigator.webdriver' property"""
        await self.page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => {json.dumps(self.config.webdriver)} 
            }});
        """)
from playwright.async_api import Page
import random
from .constants import PLUGINS, VIEWPORTS
from .dataclasses import PageConfigOptions

class PageSetup:

    def __init__(self, page: Page, config: PageConfigOptions | None = None):
        self.config = config or self._build_config_options()
        self.page = page


    def _build_config_options(self) -> PageConfigOptions:
        
        return PageConfigOptions(
            viewport = random.choice(VIEWPORTS)
        )

    async def setup(self):
        """Set various config settings for a new SpiderPage object."""
        await self._set_viewport()
        await self._set_webdriver()
        await self._set_window_history_length()
        await self._set_languages()
        await self._set_platform()       


    async def _set_platform(self):
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'platform', {
               get: () => 'Win32'                      
            });
        """)


    async def _set_window_history_length(self):
        """Sets the window.history.length property to something greater than 1"""
        await self.page.add_init_script("""
            Object.defineProperty(window.history, 'length', {
                get: () => Math.floor(Math.random() * 10) + 3
            });
        """)


    async def _get_plugins(self) -> str:
        """Returns a serialized string of the browser's actual plugin values.
        Running page.evaluate("navigator.plugins") returns a mostly-empty object.
        """
        plugins_json = await self.page.evaluate("""
            JSON.stringify(Object.fromEntries(Array.from(navigator.plugins).map(
                p => [p.name, {
                    name: p.name,
                    filename: p.filename,
                    description: p.description,
                    mimeTypeCount: p.length,
                    mimeTypes: Object.fromEntries(Array.from(p).map(
                        m => [m.type, { type: m.type, suffixes: m.suffixes, description: m.description }]
                    ))
                }]
            )));
        """)

        return plugins_json


    async def _set_plugins(self):
        """Sets the navigator.plugins value. Now in headless mode plugins
        will actually show up.
        """
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => (""" + f"{PLUGINS}" + """)
            });"""
        )

    async def _set_viewport(self):
        """Sets the page's viewport to that of a standard desktop computer."""
        await self.page.set_viewport_size({"width": self.config.viewport[0], "height": self.config.viewport[1]})
        return


    async def _set_languages(self):
        """Sets the navigator.language and navigator.languages values"""
        await self.page.add_init_script(f"""
            Object.defineProperty(navigator, 'languages', {{
               get: () => {self.config.languages}                         
            }});
            Object.defineProperty(navigator, 'language', {{
               get: () => {self.config.language}                         
            }});
        """)

    async def _set_webdriver(self):
        """Sets the 'navigator.webdriver' property"""
        await self.page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => {self.config.webdriver} 
            }});
        """)
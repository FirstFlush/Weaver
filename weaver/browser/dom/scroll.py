from asyncio import sleep
from playwright.async_api import Page, ElementHandle
import random
import math

class Cursor:
    
    def __init__(self, page:Page):
        self.page = page

    def _generate_curved_path(
            self, 
            start_x: int, 
            start_y: int, 
            end_x: int, 
            end_y: int, 
            steps:int = 20
    ):
        """Generates a curve based on a sin wave."""
        path = []
        for i in range(steps):
            t = i / (steps - 1)
            x = (1 - t) * start_x + t * end_x
            y = (1 - t) * start_y + t * end_y + math.sin(t * math.pi) * 50  # Sin wave for curve
            # Adding randomness
            x += random.uniform(-5, 5)
            y += random.uniform(-5, 5)
            path.append((x, y))
        return path

    async def human_like_mouse_move(
        self, 
        start_x:int, 
        start_y:int, 
        end_x:int, 
        end_y:int,
        steps:int=20
    ):
        """Moves the mouse cursor in a sin-wave pattern to make the 
        webscraper appear more human-like.
        """
        path = self._generate_curved_path(start_x, start_y, end_x, end_y, steps)
        for x, y in path:
            await self.page.mouse.move(x, y)
            await sleep(random.uniform(0.05, 0.15))





class PageScroll:

    def __init__(self, page:Page):
        self.page = page

    async def _get_scroll_values(self, element_selector:str) -> dict:
        """Returns the values of the web browser's scrollTop & scrollHeight
        DOM properties. used in the self.infinite_scroll() method.
        """
        values = await self.page.evaluate(f"""
            const container = document.querySelector('{element_selector}');
            ({{
                scrollTop: container.scrollTop,
                scrollHeight: container.scrollHeight
            }});
        """)
        return values


    async def infinite_scroll(self, element_selector:str, timeout:int=3000):
        """Keep scrolling until we reach the bottom using Javascript:

        container.scrollHeight  -Check the height of the container
        container.scrollTop     -Set this to scrollHeight value to scroll to bottom
        """
        previous_scrollTop = None
        while True:
            await self.page.evaluate(f"""
            const container = document.querySelector('{element_selector}');
            container.scrollTop = container.scrollHeight;
            """)
            await self.page.wait_for_timeout(timeout)
            values = await self._get_scroll_values(element_selector)
            if values['scrollTop'] == previous_scrollTop:
                break
            previous_scrollTop = values['scrollTop']

        return


    async def scroll_into_view(self, element:ElementHandle, timeout:float=3000):
        """Scrolls the element into view. Used to appear more human when clicking on links.
            -Might be adding more functionality to this, like some small jitter time.
        """
        await element.scroll_into_view_if_needed(timeout=timeout)
        return


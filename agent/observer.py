from bs4 import BeautifulSoup
from loguru import logger
from browser.playwright_manager import PlaywrightManager

class Observer:
    """
    Parses browser state into a LLM-friendly format.
    """
    def __init__(self, browser: PlaywrightManager):
        self.browser = browser

    async def observe(self) -> dict:
        """
        Returns a structured observation of the current page.
        """
        if not self.browser.page:
            return {"error": "Browser not initialized"}

        try:
            # Get raw content
            content = await self.browser.page.content()
            state = await self.browser.get_state()
            
            # Simplify DOM for LLM (Reduce token usage)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove scripts, styles, svgs
            for tag in soup(['script', 'style', 'svg', 'path', 'noscript']):
                tag.decompose()

            # Extract interactive elements with selectors
            interactive_elements = []
            
            # Links
            for a in soup.find_all('a', href=True):
                 text = a.get_text(strip=True) or "[Image Link]"
                 interactive_elements.append(f"LINK: '{text}' -> {a['href']}")

            # Buttons
            for btn in soup.find_all('button'):
                text = btn.get_text(strip=True) or "[Icon Button]"
                interactive_elements.append(f"BUTTON: '{text}' -> class: {btn.get('class')}")
            
            # Inputs
            for inp in soup.find_all('input'):
                inp_type = inp.get('type', 'text')
                placeholder = inp.get('placeholder', '')
                inp_id = inp.get('id', '')
                interactive_elements.append(f"INPUT: [{inp_type}] id='{inp_id}' placeholder='{placeholder}'")

            # Clean text body (limit length)
            body_text = soup.body.get_text(separator=' ', strip=True)[:3000] if soup.body else ""

            observation = {
                "url": state.get("url"),
                "title": state.get("title"),
                "interactive_elements": interactive_elements[:50], # Limit to avoid context overflow
                "page_text_summary": body_text
            }
            
            logger.info(f"Observation captured for {state.get('url')}")
            return observation

        except Exception as e:
            logger.error(f"Observation failed: {e}")
            return {"error": str(e)}

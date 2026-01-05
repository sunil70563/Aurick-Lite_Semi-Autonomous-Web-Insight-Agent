from typing import Dict, Any, List
from loguru import logger
from browser.playwright_manager import PlaywrightManager

class Observer:
    """
    The Page Perception Layer.
    Extracts human-visible context using JavaScript execution in the browser.
    """
    def __init__(self, browser: PlaywrightManager):
        self.browser = browser

    async def observe(self) -> Dict[str, Any]:
        """
        Capture the current page state in a structured, LLM-friendly format.
        """
        if not self.browser.page:
            return {"error": "Browser not initialized"}
        
        page = self.browser.page

        try:
            logger.info(f"Observing page: {page.url}")

            # 1. Basic Metadata
            url = page.url
            title = await page.title()

            # 2. Visible Text (What the human sees)
            # using document.body.innerText is a good approximation of visible text
            visible_text = await page.evaluate("() => document.body.innerText")

            # 3. Interactive Elements Extraction via JS
            # We extract Buttons, Links, and Inputs with their properties
            
            # Buttons: text, disabled status
            buttons = await page.evaluate("""
                () => Array.from(document.querySelectorAll('button'))
                    .map(b => ({
                        text: b.innerText.trim(),
                        disabled: b.disabled,
                        id: b.id,
                        class: b.className
                    }))
                    .filter(b => b.text.length > 0)
            """)

            # Links: text, href
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a'))
                    .map(a => ({
                        text: a.innerText.trim(),
                        href: a.href
                    }))
                    .filter(a => a.text.length > 0 && a.href.length > 0)
            """)

            # Inputs: type, placeholder, name, label (heuristic)
            inputs = await page.evaluate("""
                () => Array.from(document.querySelectorAll('input, textarea, select'))
                    .map(i => ({
                        tag: i.tagName.toLowerCase(),
                        type: i.type || 'text',
                        placeholder: i.placeholder || "",
                        name: i.name || "",
                        id: i.id || "",
                        value: i.value || ""
                    }))
                    .filter(i => i.type !== 'hidden')
            """)

            # 4. Construct Structured Context
            # We cap the lists to avoid context window explosion
            observation = {
                "url": url,
                "title": title,
                "page_type_signal": "unknown", # To be filled by Reasoner or Heuristic later
                "visible_text_summary": visible_text[:1500] if visible_text else "", # Cap text
                "interactive_elements": {
                    "buttons": buttons[:15], # Top 15 buttons
                    "links": links[:15],     # Top 15 links
                    "inputs": inputs[:10]    # Top 10 inputs
                }
            }
            
            logger.info(f"Observation complete. Found {len(buttons)} text-buttons, {len(links)} text-links.")
            return observation

        except Exception as e:
            logger.error(f"Observation failed: {e}")
            return {"error": f"Observation failed: {str(e)}"}

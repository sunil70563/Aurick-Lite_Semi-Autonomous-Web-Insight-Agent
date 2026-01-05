from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import os
import datetime
from loguru import logger
from typing import Dict, Any, Optional, List
import asyncio

class PlaywrightManager:
    """
    Manages browser lifecycle, observations (screenshots, console), and interactions.
    """
    def __init__(self, headless=False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.console_logs: List[Dict[str, Any]] = []

    async def start(self):
        """Start the browser session."""
        logger.info(f"Starting browser (Headless: {self.headless})")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=500 # Added for visibility during demo
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = await self.context.new_page()
        
        # Capture console logs
        self.page.on("console", self._capture_console)

    async def open(self, url: str):
        """Navigate to a URL with retry logic."""
        if not self.page:
            await self.start()
        logger.info(f"Navigating to {url}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await self.page.wait_for_timeout(2000) # Give extra time for hydration
                return
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All navigation retries failed for {url}")
                    raise e
    
    # Alias for backward compatibility with Executor if needed, or we update Executor later
    async def open_url(self, url: str):
        await self.open(url)

    async def screenshot(self, name_prefix="step") -> str:
        """Capture and save a screenshot."""
        if not self.page: return ""
        
        directory = "logs/screenshots"
        os.makedirs(directory, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name_prefix}_{timestamp}.png"
        path = os.path.join(directory, filename)
        
        try:
            await self.page.screenshot(path=path)
            logger.info(f"Screenshot saved: {path}")
            return path
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ""

    def _capture_console(self, msg):
        """Handler for console events."""
        entry = {
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }
        self.console_logs.append(entry)
        # logger.debug(f"Console [{msg.type}]: {msg.text}")

    async def get_page_content(self):
        """Get raw HTML content."""
        if not self.page: return ""
        return await self.page.content()

    async def close(self):
        """Clean up resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped.")

    # --- Interaction Methods (Preserved for Step 4) ---

    async def get_state(self) -> Dict[str, Any]:
        """Capture current page state: URL, Title, and basic DOM text."""
        if not self.page: return {}
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "content": await self.page.evaluate("document.body.innerText")
        }

    async def click_element(self, selector: str):
        """Robust click."""
        if not self.page: return
        try:
            logger.info(f"Clicking: {selector}")
            await self.highlight(selector)
            await self.page.click(selector, timeout=5000)
        except Exception as e:
            logger.error(f"Click failed for {selector}: {e}")
            # Don't crash, just log, let the Agent Reflect
            raise e

    async def type_text(self, selector: str, text: str):
        """Robust type."""
        if not self.page: return
        try:
            logger.info(f"Typing '{text}' into {selector}")
            await self.highlight(selector)
            await self.page.fill(selector, text, timeout=5000)
        except Exception as e:
            logger.error(f"Type failed for {selector}: {e}")
            raise e

    async def highlight(self, selector: str):
        """Visual highlight script."""
        try:
            await self.page.evaluate(
                f"""(selector) => {{
                    const el = document.querySelector(selector);
                    if (el) {{
                        el.style.border = '2px solid red';
                        el.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                    }}
                }}""", selector
            )
            await asyncio.sleep(0.5)
        except Exception:
            pass

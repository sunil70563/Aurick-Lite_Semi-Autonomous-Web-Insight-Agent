import asyncio
from typing import Dict, Any
from loguru import logger
from browser.playwright_manager import PlaywrightManager

class ActionExecutor:
    """
    The Hands: Executes planned actions using robust, human-like heuristics.
    Prioritizes visible text matching over brittle CSS selectors.
    """
    async def execute(self, action: Dict[str, Any], browser: PlaywrightManager) -> Dict[str, Any]:
        
        page = browser.page
        if not page:
            return {"status": "error", "details": "Browser not initialized"}

        result = {
            "status": "success",
            "details": "",
            "action_type": action["type"]
        }

        logger.info(f"Executing Action: {action['type']} -> {action['target_description']}")

        try:
            if action["type"] == "click":
                await self._execute_click(action, page)

            elif action["type"] == "navigate":
                target = action.get("target_description")
                if target:
                    await browser.open(target)
                else:
                    raise Exception("Navigation target missing")

            elif action["type"] == "type":
                await self._execute_type(action, page)

            elif action["type"] == "stop":
                result["status"] = "stopped"
                result["details"] = f"Agent decided to stop: {action.get('reason')}"
            
            # Capture evidence of action
            await browser.screenshot(f"action_{action['type']}")

        except Exception as e:
            logger.error(f"Execution Failed: {e}")
            result["status"] = "error"
            result["details"] = str(e)
        
        return result

    async def _execute_click(self, action, page):
        """
        Click heuristic: Find element by text content (Button or Link).
        """
        description = action["target_description"].lower()
        if not description: return

        # 1. Try Buttons
        buttons = page.locator("button")
        count = await buttons.count()
        for i in range(count):
            btn = buttons.nth(i)
            text = await btn.inner_text()
            if description in text.lower():
                logger.info(f"Clicked button: '{text}'")
                await btn.click()
                return

        # 2. Try Links
        links = page.locator("a")
        count = await links.count()
        for i in range(count):
            link = links.nth(i)
            text = await link.inner_text()
            # Simple substring match for robustness
            if description in text.lower():
                 logger.info(f"Clicked link: '{text}'")
                 await link.click()
                 return
        
        raise Exception(f"No clickable element found matching '{description}'")

    async def _execute_type(self, action, page):
        """
        Type heuristic: Find first visible input.
        """
        inputs = page.locator("input:visible")
        count = await inputs.count()
        
        if count == 0:
            raise Exception("No visible input fields found")
            
        # For demo purposes, type into the first available input
        # Step 4 instructions explicitly asked for this simple behavior
        await inputs.first.fill("test@example.com")

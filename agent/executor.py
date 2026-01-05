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
            text = (await btn.inner_text()).lower()
            if description in text or text in description:
                logger.info(f"Clicked button: '{text}'")
                await btn.click()
                return

        # 2. Try Links
        links = page.locator("a")
        count = await links.count()
        for i in range(count):
            link = links.nth(i)
            text = (await link.inner_text()).lower()
            # Simple substring match for robustness
            if text and (description in text or text in description):
                 logger.info(f"Clicked link: '{text}'")
                 await link.click()
                 return
        
        # 3. Try Inputs (e.g. type="submit")
        inputs = page.locator("input[type='submit'], input[type='button']")
        count = await inputs.count()
        for i in range(count):
            inp = inputs.nth(i)
            # Match value attribute: strict containment is too brittle (e.g. "Login Button" vs "Login")
            # We'll check if the main word of the description is in the value
            value = await inp.get_attribute("value")
            if value:
                val_lower = value.lower()
                # Check exact containment or word split
                if description in val_lower or val_lower in description or description.split()[0] in val_lower:
                    logger.info(f"Clicked input button: '{value}'")
                    await inp.click()
                    return
        
        raise Exception(f"No clickable element found matching '{description}'")

    async def _execute_type(self, action, page):
        """
        Type heuristic: Find the most relevant input based on description.
        """
        target_desc = action.get("target_description", "").lower()
        input_value = action.get("input_value", "")
        
        if not input_value:
            logger.warning(f"No input_value provided for '{target_desc}'. Using empty string.")
            input_value = ""

        logger.info(f"Typing '{input_value}' into '{target_desc}'")

        inputs = page.locator("input:visible, textarea:visible")
        count = await inputs.count()
        
        if count == 0:
            raise Exception("No visible input fields found")

        # Smart Match: Check placeholders, names, ids
        for i in range(count):
            inp = inputs.nth(i)
            attrs = await inp.evaluate("el => (el.placeholder + ' ' + el.name + ' ' + el.id).toLowerCase()")
            
            # Simple keyword matching
            keywords = target_desc.split()
            if any(k in attrs for k in keywords if len(k) > 2):
                await inp.fill(input_value)
                return

        # Fallback: Type in first empty or just first input if no match found
        logger.warning(f"No specific match for '{target_desc}', typing in first input.")
        await inputs.first.fill(input_value)

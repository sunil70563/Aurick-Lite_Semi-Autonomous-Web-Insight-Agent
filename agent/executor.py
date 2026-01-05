from typing import Dict, Any
from loguru import logger
from browser.playwright_manager import PlaywrightManager

class Executor:
    """
    The Hands: Executes the planned action using the Browser Manager.
    """
    async def execute(self, action: Dict[str, Any], browser: PlaywrightManager) -> str:
        """
        Execute the action and return a result string.
        """
        action_type = action.get("type")
        target = action.get("target_selector")
        text = action.get("input_text")

        logger.info(f"Executing: {action_type} on {target or 'N/A'}")

        try:
            if action_type == "click":
                if not target: return "Error: No target for click."
                # Heuristic: If target starts with "LINK: ", extract href?
                # The observer returns "LINK: 'text' -> href". The LLM might return that whole string or just 'text'.
                # Ideally LLM returns a CSS selector. The Observer currently doesn't provide CSS selectors explicitly for all items, 
                # but we can try basic text matching if it's not a valid selector.
                
                # Check if it looks like a text match selector (Playwright supports text=...)
                if "text=" not in target and not target.startswith((".", "#", "//", "html")):
                    # Assume it's text
                     target = f"text={target}"
                
                await browser.click_element(target)
                return "Click successful"

            elif action_type == "type":
                if not target or not text: return "Error: Missing target or text for type."
                await browser.type_text(target, text)
                return f"Typed '{text}' successful"

            elif action_type == "navigate":
                if not target: return "Error: No url for navigate."
                await browser.open_url(target)
                return f"Navigated to {target}"

            elif action_type == "stop":
                return "Agent decided to STOP."

            else:
                return f"Unknown action type: {action_type}"

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return f"Execution Error: {str(e)}"

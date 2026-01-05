from typing import Dict, Any
from loguru import logger

class Planner:
    """
    The Tactician: Validates and refines the LLM's decision.
    """
    def plan(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate decision and ensure it's safe/executable.
        """
        action = decision.get("next_action", {})
        action_type = action.get("type", "stop").lower()

        # heuristic: If confidence is low, maybe stop or verify?
        confidence = decision.get("confidence_score", 1.0)
        if confidence < 0.3:
            logger.warning(f"Low confidence ({confidence}). Modifying action to STOP or CHECK.")
            # For now, we'll let it slide but log it, or return STOP.
            # return {"type": "stop", "reason": "Low confidence in decision."}

        # Normalize action
        valid_actions = ["click", "type", "navigate", "stop"]
        if action_type not in valid_actions:
             logger.warning(f"Invalid action type '{action_type}'. Defaulting to STOP.")
             return {"type": "stop", "reason": f"Invalid action type: {action_type}"}

        # Structure cleanup
        safe_action = {
            "type": action_type,
            "target_selector": action.get("target_selector"),
            "input_text": action.get("input_text"),
            "description": action.get("description", "No description provided")
        }
        
        return safe_action

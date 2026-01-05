from typing import Dict, Any

class ActionPlanner:
    """
    The Tactician: Validates abstract LLM decisions into executable plans.
    Ensures safety and correctness before execution.
    """
    def plan(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the LLM's next_action.
        """
        next_action = decision.get("next_action", {})
        
        # Normalize action type
        action_type = next_action.get("type", "stop").lower().strip()

        # Whitelist valid actions
        valid_actions = ["click", "type", "navigate", "stop"]
        
        if action_type not in valid_actions:
            return {
                "type": "stop",
                "reason": f"Unknown or unsafe action type: {action_type}"
            }

        # Construct safe plan
        return {
            "type": action_type,
            "target_description": next_action.get("target_description", "").strip(),
            "input_value": next_action.get("input_value", ""),
            "reason": next_action.get("reason", "No reason provided")
        }

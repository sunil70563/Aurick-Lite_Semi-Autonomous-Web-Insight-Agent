from typing import Dict, Any, List
from loguru import logger
from llm.groq_client import GroqClient
from llm.prompts import PAGE_REASONING_PROMPT

class Reasoner:
    """
    The Brain: Sends observations to Groq and gets a decision.
    """
    def __init__(self, client: GroqClient):
        self.client = client

    def reason(self, observation: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consult the LLM for the next action.
        """
        try:
            # Format history (limit to last 5 steps to save tokens)
            history_summary = [
                f"Step {h['step']}: Action={h['action'].get('type')} -> Result={h.get('result', 'Unknown')}" 
                for h in history[-5:]
            ]
            
            prompt = PAGE_REASONING_PROMPT.format(
                url=observation.get("url", "Unknown"),
                title=observation.get("title", "Unknown"),
                page_text=observation.get("page_text_summary", "")[:2000],
                interactive_elements="\n".join(observation.get("interactive_elements", [])),
                history="\n".join(history_summary) or "No history yet (Start of session)."
            )

            messages = [
                {"role": "system", "content": "You are a helpful QA AI agent."},
                {"role": "user", "content": prompt}
            ]

            logger.info("Thinking... (Querying Groq)")
            decision = self.client.get_json(messages)
            logger.info(f"Decision: {decision.get('next_action', {}).get('type')} - {decision.get('reasoning')}")
            
            return decision

        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            # Fallback safe action
            return {
                "next_action": {"type": "stop", "reason": f"Error in reasoning: {e}"},
                "potential_issues": ["Agent crashed during reasoning."]
            }

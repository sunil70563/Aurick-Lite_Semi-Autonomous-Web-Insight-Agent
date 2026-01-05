import json
from loguru import logger
from llm.prompts import PAGE_REASONING_PROMPT
from llm.groq_client import GroqLLM

class PageReasoner:
    """
    The Brain: Uses Groq to reason about the page state and decide the next action.
    """
    def __init__(self, llm: GroqLLM):
        self.llm = llm

    def reason(self, observation: dict, history: list) -> dict:
        """
        Send observation to LLM and parse the decision.
        """
        if "error" in observation:
             return {
                "page_summary": "Error in observation",
                "confidence": 0.0,
                "next_action": {"type": "stop", "reason": f"Observation failed: {observation.get('error')}"},
                "potential_issues": ["Observer Failure"]
            }

        try:
            # Prepare context for prompt
            # We dump the dict to a string, possibly filtering or truncating if needed
            # For now, pass the whole observation as it is structured and capped by Observer
            context_str = json.dumps(observation, indent=2, ensure_ascii=False)
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a careful and observant AI QA engineer."
                },
                {
                    "role": "user",
                    "content": PAGE_REASONING_PROMPT.format(
                        page_context=context_str
                    )
                }
            ]

            logger.info("Thinking... (Querying Groq)")
            raw_output = self.llm.chat(messages)
            
            # Defensive Parsing
            # Extract JSON if wrapped in markdown code blocks
            clean_output = raw_output.strip()
            if clean_output.startswith("```json"):
                clean_output = clean_output.replace("```json", "").replace("```", "")
            elif clean_output.startswith("```"):
                clean_output = clean_output.replace("```", "")
            
            parsed = json.loads(clean_output)
            logger.info(f"Decision: {parsed.get('next_action', {}).get('type')}")
            return parsed

        except json.JSONDecodeError:
            logger.error(f"JSON Parsing Failed. Raw Output: {raw_output}")
            # Graceful Fallback
            return {
                "page_summary": "Unable to parse page context",
                "confidence": 0.2,
                "next_action": {
                    "type": "stop",
                    "target_description": "",
                    "reason": "LLM output was invalid JSON"
                },
                "potential_issues": ["LLM JSON parsing failure"]
            }
        except Exception as e:
            logger.error(f"Reasoning Error: {e}")
            return {
                "page_summary": "Critical Reasoning Error",
                "confidence": 0.0,
                "next_action": {
                    "type": "stop",
                    "reason": f"System error: {str(e)}"
                },
                "potential_issues": ["System Exception"]
            }

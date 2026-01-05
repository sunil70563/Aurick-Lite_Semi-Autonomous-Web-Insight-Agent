from typing import List, Dict, Any
from loguru import logger

class Analyzer:
    """
    The Inspector: Critiques the session and flags issues.
    """
    def __init__(self):
        self.issues: List[Dict[str, Any]] = []

    def analyze(self, observation: Dict[str, Any], decision: Dict[str, Any], result: str) -> List[str]:
        """
        Analyze the step for anomalies.
        """
        current_issues = []

        # 1. Harvest issues from LLM reasoning
        llm_issues = decision.get("potential_issues", [])
        if llm_issues:
            for issue in llm_issues:
                self.issues.append({
                    "source": "LLM_Reasoning",
                    "description": issue,
                    "url": observation.get("url")
                })
                current_issues.append(f"[LLM] {issue}")

        # 2. Check for Execution Errors
        if "Error" in result or "Exception" in result:
             self.issues.append({
                 "source": "Execution_Failure",
                 "description": result,
                 "url": observation.get("url")
             })
             current_issues.append(f"[Exec] {result}")

        # 3. Check for 404/500 in Title (Heuristic)
        title = observation.get("title", "").lower()
        if "404" in title or "page not found" in title or "error" in title:
             msg = f"Potential Error Page detected: {title}"
             self.issues.append({"source": "Heuristic", "description": msg, "url": observation.get("url")})
             current_issues.append(f"[Heuristic] {msg}")

        if current_issues:
            logger.warning(f"Issues detected: {current_issues}")

        return current_issues

    def get_report(self) -> List[Dict[str, Any]]:
        return self.issues

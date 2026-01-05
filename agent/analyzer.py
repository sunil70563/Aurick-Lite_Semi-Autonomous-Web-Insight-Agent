from typing import List, Dict, Any, Optional
from loguru import logger
from browser.playwright_manager import PlaywrightManager

class IssueAnalyzer:
    """
    The QA Insight Engine: Detects and reports anomalies, errors, and UX issues.
    """
    def analyze(self, 
                observation: Dict[str, Any], 
                action: Dict[str, Any], 
                result: Dict[str, Any], 
                browser: PlaywrightManager) -> List[Dict[str, Any]]:
        
        issues = []
        url = observation.get("url", "unknown")

        # 1. Action Execution Failures (High Severity)
        if result.get("status") == "error":
            issues.append({
                "severity": "high",
                "title": "Action failed to execute",
                "description": result.get("details", "Unknown execution error"),
                "evidence": {
                    "url": url,
                    "action": action,
                    "screenshot": None # Screenshot handling is done by Executor/Agent linkage usually, or we can add logic here
                }
            })

        # 2. Console Errors (Medium Severity)
        # We need to filter for new errors since last step, but for simplicity we take recent ones
        # A more robust system would track timestamps. 
        # Here we just check if any exist and perhaps were not there before (simple approximation needed or just report all unique)
        if browser.console_logs:
            # Simple heuristic: report errors if they exist. In a real loop, clearing or diffing logs is better.
            # We'll just report the presence of errors in the recent logs (last 3).
            recent_errors = [
                log for log in browser.console_logs[-5:] 
                if log['type'] in ['error', 'warning']
            ]
            
            if recent_errors:
                issues.append({
                    "severity": "medium",
                    "title": "Console errors/warnings detected",
                    "description": "Browser console reported errors during interaction.",
                    "evidence": {
                        "url": url,
                        "errors": recent_errors
                    }
                })

        # 3. LLM-Detected Potential Issues (Low/Medium Severity)
        # These come from the 'potential_issues' field in the Reasoner's output (which is passed in 'action' usually or separate)
        # In our architecture, 'action' is the output of Planner which comes from Reasoner's decision.
        # But wait, Planner output is normalized action. We need the original Reasoner decision for 'potential_issues'.
        # The user instruction says: 'llm_issues = action.get("potential_issues", [])'
        # This implies we should pass the full decision dict to the analyzer, or the Planner should allow passing it through.
        # Let's assume the 'action' argument here is the full decision object from the LLM or a merged object.
        
        # Checking previous steps: Agent.py calls:
        # decision = self.reasoner.reason(...)
        # action = self.planner.plan(decision)
        # result = self.executor.execute(action, browser)
        # issues = self.analyzer.analyze(observation, decision, result) <--- Wait, in Step 5 instructions user says: 
        # analyze(self, observation, action, result, browser)
        # But in 5.6 user says: analyze(observation=observation, action=decision, result=result...)
        
        # So 'action' param in analyze actually receives the 'decision' dict from Reasoner (which contains 'potential_issues').
        
        llm_issues = action.get("potential_issues", [])
        if isinstance(llm_issues, list):
            for issue in llm_issues:
                issues.append({
                    "severity": "low",
                    "title": "Potential UX issue (AI Detected)",
                    "description": issue,
                    "evidence": {
                        "url": url
                    }
                })

        if issues:
            logger.info(f"Analyzer found {len(issues)} issues.")
            
        return issues

import asyncio
from loguru import logger
from typing import Optional

from browser.playwright_manager import PlaywrightManager
from llm.groq_client import GroqLLM
from agent.observer import Observer
from agent.reasoner import PageReasoner
from agent.planner import ActionPlanner
from agent.executor import ActionExecutor
from agent.analyzer import IssueAnalyzer
from agent.memory import Memory

class AurickLiteAgent:
    """
    Aurick-Lite: A Semi-Autonomous Web Insight Agent.
    """
    def __init__(self, 
                 browser: PlaywrightManager,
                 groq: GroqLLM):
        
        self.browser = browser
        self.memory = Memory()
        
        # Initialize Modules
        self.observer = Observer(browser)
        self.reasoner = PageReasoner(groq)
        self.planner = ActionPlanner()
        self.executor = ActionExecutor()
        self.analyzer = IssueAnalyzer()
        
    async def run(self, start_url: str, max_steps: int = 15):
        """
        Main Agent Loop.
        """
        logger.info(f"Agent starting session on {start_url}")
        
        try:
            await self.browser.open(start_url)
            
            for step in range(1, max_steps + 1):
                logger.info(f"\n--- STEP {step} ---")
                
                # 1. OBSERVE
                observation = await self.observer.observe()
                if "error" in observation:
                    logger.error("Failed to observe. Stopping.")
                    break

                # 2. REASON ("THINK")
                # Pass history into reasoner
                decision = self.reasoner.reason(observation, self.memory.get_history())
                
                # 3. PLAN
                plan = self.planner.plan(decision)
                
                if plan["type"] == "stop":
                    logger.info(f"Agent decided to STOP: {plan.get('reason', 'No reason')}")
                    break

                # 4. ACT
                result = await self.executor.execute(plan, self.browser)

                # 5. REFLECT & ANALYZE
                # Pass 'decision' (which has potential_issues) as 'action' arg to analyzer as per design pattern
                issues = self.analyzer.analyze(
                    observation=observation, 
                    action=decision, 
                    result=result, 
                    browser=self.browser
                )
                
                # SAVE STATE
                step_data = {
                    "step": step,
                    "timestamp": str(self.memory.start_time),
                    "url": observation.get("url"),
                    "observation_summary": observation.get("visible_text_summary", "")[:100],
                    "decision": decision,
                    "plan": plan,
                    "result": result,
                    "issues": issues
                }
                self.memory.add_step(step_data)
                
                # Small pause for stability
                await asyncio.sleep(2)

        except Exception as e:
            logger.critical(f"Agent Loop Crashed: {e}")
            # Log crash state?
        finally:
            # Save session
            log_path = self.memory.save_session()
            logger.info(f"Session finished. Log saved to {log_path}")

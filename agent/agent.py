import asyncio
from loguru import logger
from typing import Optional

from browser.playwright_manager import PlaywrightManager
from llm.groq_client import GroqClient
from agent.observer import Observer
from agent.reasoner import Reasoner
from agent.planner import Planner
from agent.executor import Executor
from agent.analyzer import Analyzer
from agent.memory import Memory

class AurickLiteAgent:
    """
    Aurick-Lite: A Semi-Autonomous Web Insight Agent.
    """
    def __init__(self, 
                 browser: PlaywrightManager,
                 groq: GroqClient,
                 model: str = "llama-3.1-70b-versatile"):
        
        self.browser = browser
        self.memory = Memory()
        
        # Initialize Modules
        self.observer = Observer(browser)
        self.reasoner = Reasoner(groq)
        self.planner = Planner()
        self.executor = Executor()
        self.analyzer = Analyzer()
        
    async def run(self, start_url: str, max_steps: int = 15):
        """
        Main Agent Loop.
        """
        logger.info(f"Agent starting session on {start_url}")
        
        try:
            await self.browser.open_url(start_url)
            
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
                
                # 3. PLAN & ACT
                action = self.planner.plan(decision)
                
                if action["type"] == "stop":
                    logger.info(f"Agent decided to STOP: {action.get('reason', 'No reason')}")
                    break

                result = await self.executor.execute(action, self.browser)

                # 4. REFLECT & ANALYZE
                issues = self.analyzer.analyze(observation, decision, result)
                
                # SAVE STATE
                step_data = {
                    "step": step,
                    "timestamp": str(self.memory.start_time),  # or current time
                    "url": observation.get("url"),
                    "observation_summary": observation.get("page_text_summary", "")[:100],
                    "decision": decision,
                    "action": action,
                    "result": result,
                    "issues": issues
                }
                self.memory.add_step(step_data)
                
                # Small pause for stability
                await asyncio.sleep(2)

        except Exception as e:
            logger.critical(f"Agent Loop Crashed: {e}")
        finally:
            # Save session
            log_path = self.memory.save_session()
            logger.info(f"Session finished. Log saved to {log_path}")

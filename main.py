import asyncio
import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from browser.playwright_manager import PlaywrightManager
from llm.groq_client import GroqClient
from agent.agent import AurickLiteAgent

async def main():
    # 1. Setup
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY is missing via .env or environment variable.")
        return

    start_url = "https://www.saucedemo.com/" 
    # Optional: Take URL from args
    if len(sys.argv) > 1:
        start_url = sys.argv[1]

    logger.info(f"Initializing Aurick-Lite Agent for {start_url}...")

    # 2. Initialize Core Systems
    browser_manager = PlaywrightManager()
    groq_client = GroqClient(api_key=settings.GROQ_API_KEY)
    
    agent = AurickLiteAgent(browser=browser_manager, groq=groq_client)

    try:
        # Start Browser
        await browser_manager.start()
        
        # 3. Run Agent
        await agent.run(start_url, max_steps=settings.MAX_STEPS)
        
    except KeyboardInterrupt:
        logger.info("User interrupted session.")
    except Exception as e:
        logger.critical(f"Unexpected crash: {e}")
    finally:
        await browser_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())

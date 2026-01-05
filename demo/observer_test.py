import asyncio
import os
import sys

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser.playwright_manager import PlaywrightManager
from agent.observer import Observer

async def test():
    print("Initializing Browser...")
    browser = PlaywrightManager(headless=True)
    await browser.start()
    
    try:
        url = "https://www.saucedemo.com/"
        print(f"Navigating to {url}...")
        await browser.open(url)
        
        print("Initializing Observer...")
        observer = Observer(browser)
        
        print("Observing...")
        data = await observer.observe()
        
        print("\n--- OBSERVATION RESULT ---")
        print(f"Title: {data.get('title')}")
        print(f"Visible Text (first 100 chars): {data.get('visible_text_summary')[:100]}...")
        
        elements = data.get('interactive_elements', {})
        print(f"Buttons found: {len(elements.get('buttons', []))}")
        print(f"Links found: {len(elements.get('links', []))}")
        print(f"Inputs found: {len(elements.get('inputs', []))}")
        
        if elements.get('inputs'):
            print(f"First Input: {elements['inputs'][0]}")

    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        await browser.close()
        print("Browser Closed.")

if __name__ == "__main__":
    asyncio.run(test())

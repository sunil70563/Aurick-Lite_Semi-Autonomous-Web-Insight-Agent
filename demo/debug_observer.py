import asyncio
import os
import sys
import traceback

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser.playwright_manager import PlaywrightManager
from agent.observer import Observer

async def test():
    log_file = "debug_output.txt"
    # Write to root
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Initializing Browser...\n")
    
    def log(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")

    browser = PlaywrightManager(headless=True)
    await browser.start()
    
    try:
        url = "https://www.google.com/"
        log(f"Navigating to {url}...")
        await browser.open(url)
        
        log("Initializing Observer...")
        observer = Observer(browser)
        
        log("Observing...")
        data = await observer.observe()
        
        if not data:
            log("ERROR: Observer returned None")
            return

        if "error" in data:
            log(f"ERROR from Observer: {data['error']}")
            return
        
        log("\n--- OBSERVATION RESULT ---")
        log(f"Title: {data.get('title')}")
        log(f"Visible Text Summary Length: {len(data.get('visible_text_summary', ''))}")
        
        elements = data.get('interactive_elements', {})
        log(f"Buttons: {len(elements.get('buttons', []))}")
        log(f"Links: {len(elements.get('links', []))}")
        log(f"Inputs: {len(elements.get('inputs', []))}")

    except Exception:
        log("EXCEPTION CAUGHT:")
        log(traceback.format_exc())
    finally:
        await browser.close()
        log("Browser Closed.")

if __name__ == "__main__":
    asyncio.run(test())

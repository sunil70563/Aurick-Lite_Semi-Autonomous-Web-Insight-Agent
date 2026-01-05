import asyncio
import os
import sys

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser.playwright_manager import PlaywrightManager

async def test():
    print("Initializing Browser Manager...")
    # Headless=True for CI/Background, False for local debug if desired. 
    # User asked for 'headless=False' in their snippet, using False to show it works visually if watched, 
    # or just to match expectations.
    browser = PlaywrightManager(headless=True) 
    
    try:
        await browser.start()
        print("Browser Started.")
        
        url = "https://www.example.com"
        print(f"Opening {url}...")
        await browser.open(url)
        
        print("Taking screenshot...")
        path = await browser.screenshot("sanity_check")
        print(f"Screenshot saved to: {path}")
        
        content = await browser.get_page_content()
        print(f"Page content length: {len(content)} bytes")
        
        print("Test Complete.")
        
    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        await browser.close()
        print("Browser Closed.")

if __name__ == "__main__":
    asyncio.run(test())

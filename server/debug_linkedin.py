#!/usr/bin/env python
"""
Debug script to test LinkedIn scraping and see actual page structure.
Run with: python server/debug_linkedin.py
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SESSION_FILE = Path(__file__).parent / '.linkedin_session' / 'session.json'

async def debug_scrape():
    """Debug scraper - saves HTML for inspection."""
    
    if not SESSION_FILE.exists():
        print("❌ Session file not found. Run linkedin_login.py first.")
        return
    
    profile_url = input("Enter LinkedIn profile URL to debug: ").strip()
    
    async with async_playwright() as p:
        # Load session
        with open(SESSION_FILE, 'r') as f:
            storage_state = json.load(f)
        
        # Launch in HEADFUL mode to see what's happening
        browser = await p.chromium.launch(
            headless=False,  # See the browser!
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            storage_state=storage_state,
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        print(f"\n📖 Navigating to: {profile_url}")
        await page.goto(profile_url, wait_until='domcontentloaded')
        
        # Wait for page to load
        await asyncio.sleep(5)
        
        # Save HTML for inspection
        html = await page.content()
        debug_html_file = Path(__file__).parent / 'debug_linkedin.html'
        with open(debug_html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML saved to: {debug_html_file}")
        print("\n🔍 Test selectors interactively:")
        print("The browser will stay open. Check the console for element inspection.")
        
        # Keep browser open
        input("\nPress ENTER to close browser...")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_scrape())

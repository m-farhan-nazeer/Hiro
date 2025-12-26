#!/usr/bin/env python
"""
LinkedIn Login Helper Script

Run this script ONCE to save your LinkedIn session:
    python server/linkedin_login.py

This will:
1. Open a browser window
2. Let you log in manually
3. Save your session to server/.linkedin_session/
4. Close the browser

After this, the scraper can reuse your session for ~30 days.
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright


SESSION_DIR = Path(__file__).parent / '.linkedin_session'
SESSION_FILE = SESSION_DIR / 'session.json'


async def login_to_linkedin():
    """Interactive LinkedIn login that saves session."""
    
    # Create session directory
    SESSION_DIR.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("LinkedIn Login Helper")
    print("=" * 60)
    print("\n📋 Instructions:")
    print("1. A browser will open")
    print("2. Log in to LinkedIn manually")
    print("3. Complete any 2FA/verification")
    print("4. Browse to any profile (to verify you're logged in)")
    print("5. Press ENTER in this terminal when done")
    print("\n⏳ Starting browser...\n")
    
    async with async_playwright() as p:
        # Launch browser in headful mode (visible)
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        # Create persistent context (this is what saves cookies)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Navigate to LinkedIn login
        await page.goto('https://www.linkedin.com/login')
        
        print("✅ Browser opened!")
        print("👉 Please log in to LinkedIn now...")
        
        # Wait for user to complete login
        input("\n⌨️  Press ENTER when you're logged in and viewing a profile: ")
        
        # Save session (cookies + storage state)
        print("\n💾 Saving session...")
        storage_state = await context.storage_state()
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(storage_state, f, indent=2)
        
        print(f"✅ Session saved to: {SESSION_FILE}")
        print("\n🎉 Setup complete!")
        print("\nYour scraper can now use this session for ~30 days.")
        print("If the session expires, just run this script again.")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(login_to_linkedin())

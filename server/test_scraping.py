import os
import django
import asyncio
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applicants.scrapers import LinkedInScraper

async def run_test():
    scraper = LinkedInScraper()
    # Use a public company page or a known public profile. 
    # Company pages are often less restricted than personal profiles for testing.
    # But our scraper is built for profiles. Let's try a public figure or just see if it runs without crashing.
    target_url = "https://www.linkedin.com/in/williamhgates" 
    
    print(f"Testing scraper against: {target_url}")
    print("This might take 10-20 seconds...")
    
    insights = await scraper.scrape_profile(target_url)
    
    print("\n--- Scraping Results ---")
    print(insights)
    
    if insights.get('error') and "AuthWall" in insights['error']:
        print("\n⚠️  Hit AuthWall. This is expected for server-side scraping without cookies.")
        print("The mechanics work, but LinkedIn blocked the request.")
    elif insights.get('headline'):
        print("\n✅ Success! Extracted headline.")

if __name__ == "__main__":
    asyncio.run(run_test())

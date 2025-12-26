import logging
import random
import json
import time
from pathlib import Path
from typing import Dict
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Session file location
SESSION_DIR = Path(__file__).parent.parent / '.linkedin_session'
SESSION_FILE = SESSION_DIR / 'session.json'


class LinkedInScraper:
    """
    Authenticated LinkedIn scraper using persistent browser sessions.
    Requires one-time manual login via linkedin_login.py script.
    """

    def __init__(self):
        self.timeout = 15000  # milliseconds
        self.daily_limit = 50

    def scrape_profile(self, profile_url: str) -> Dict:
        """
        Scrape LinkedIn profile (fully synchronous).
        """
        insights = {
            "headline": None,
            "about": None,
            "profile_picture": None,
            "location": None,
            "current_position": {
                "title": None,
                "company": None,
                "duration": None
            },
            "experiences": [],  # All work experiences
            "connections": None,
            "followers": None,
            "recent_activity": [],
            "error": None
        }

        if not profile_url or "linkedin.com" not in profile_url:
            insights["error"] = "Invalid LinkedIn URL"
            return insights

        # Check if session file exists
        if not SESSION_FILE.exists():
            insights["error"] = (
                "LinkedIn session not found. "
                "Please run: python server/linkedin_login.py"
            )
            return insights

        with sync_playwright() as p:
            browser = None
            try:
                logger.info(f"Loading LinkedIn session from: {SESSION_FILE}")
                
                # Load saved session
                with open(SESSION_FILE, 'r') as f:
                    storage_state = json.load(f)
                
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                # Create context with saved session
                context = browser.new_context(
                    storage_state=storage_state,
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = context.new_page()
                
                logger.info(f"Navigating to: {profile_url}")
                page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
                
                # Human-like delay
                time.sleep(random.uniform(3, 5))
                
                # Save screenshot and HTML for debugging
                try:
                    debug_dir = SESSION_DIR.parent / 'debug'
                    debug_dir.mkdir(exist_ok=True)
                    screenshot_path = debug_dir / 'linkedin_page.png'
                    html_path = debug_dir / 'linkedin_page.html'
                    
                    page.screenshot(path=str(screenshot_path))
                    html_content = page.content()
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                    logger.info(f"HTML saved to: {html_path}")
                except Exception as e:
                    logger.debug(f"Debug save failed: {e}")
                
                # Check if we're still logged in
                current_url = page.url
                logger.info(f"Current URL after navigation: {current_url}")
                
                if any(x in current_url.lower() for x in ['authwall', 'login', 'signup']):
                    insights["error"] = (
                        "LinkedIn session expired. "
                        "Please run: python server/linkedin_login.py"
                    )
                    return insights
                
                # Simulate human behavior
                self._simulate_human(page)
                
                # Extract data
                insights = self._extract_profile_data(page, insights)
                
                # Success logging
                if insights["headline"] or insights["about"]:
                    logger.info(f"Successfully scraped: {profile_url}")
                else:
                    insights["error"] = "Could not extract profile data"
                
            except Exception as e:
                logger.error(f"Scraping failed: {e}", exc_info=True)
                insights["error"] = str(e)
            
            finally:
                if browser:
                    browser.close()
        
        return insights

    def _extract_profile_data(self, page: Page, insights: Dict) -> Dict:
        """Extract profile data from the page."""
        try:
            # Wait for content to load
            time.sleep(2)
            
            # === Profile Photo ===
            try:
                # Try specific selectors first
                photo_selectors = [
                    'img.pv-top-card-profile-picture__image--show',  # Main profile pic
                    'img[alt*="Musa"]',  # Look for alt text with name
                    'img[alt*="profile"]',
                ]
                
                found = False
                for selector in photo_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            photo_url = element.get_attribute('src')
                            if photo_url and 'http' in photo_url and 'ghost' not in photo_url and 'profile-displayphoto' in photo_url:
                                insights["profile_picture"] = photo_url
                                logger.info(f"Found profile photo via {selector}: {photo_url[:70]}...")
                                found = True
                                break
                    except:
                        continue
                
                # Fallback: Find profile photo by looking for larger img near top
                if not found:
                    all_imgs = page.query_selector_all('img')
                    for img in all_imgs[:15]:  # Check first 15 images
                        try:
                            src = img.get_attribute('src')
                            alt = img.get_attribute('alt') or ''
                            width = img.get_attribute('width') or ''
                            
                            # Profile photos are usually 100x100 or 200x200
                            if src and 'profile-displayphoto' in src and int(width or 0) >= 100:
                                insights["profile_picture"] = src
                                logger.info(f"Found profile photo via fallback (alt: {alt}, width: {width})")
                                break
                        except:
                            continue
            except Exception as e:
                logger.warning(f"Profile photo extraction failed: {e}")
            
            # === Location ===
            try:
                location_selectors = [
                    'span.text-body-small.inline.t-black--light.break-words',
                    'div.pv-text-details__left-panel span.text-body-small',
                    'span.text-body-small',
                ]
                
                for selector in location_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        for element in elements:
                            text = element.inner_text().strip()
                            # Location usually has a comma (City, Country)
                            if text and 3 < len(text) < 100 and ',' in text:
                                # Avoid things that look like job titles/companies
                                if not any(x in text.lower() for x in ['engineer', 'developer', 'manager', 'analyst']):
                                    insights["location"] = text
                                    logger.info(f"Found location: {text}")
                                    break
                        if insights["location"]:
                            break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Location extraction failed: {e}")
            
            # === Connection Count ===
            try:
                # Look specifically for "XXX+ connections" or "XXX connections" text
                all_text_elements = page.query_selector_all('span, li, div, a')
                for element in all_text_elements[:100]:  # Check first 100 elements
                    try:
                        text = element.inner_text().strip()
                        # Must contain "connection" word AND have digits
                        if 'connection' in text.lower() and any(char.isdigit() for char in text):
                            # Extract number (must be 3+ digits to avoid notification badges)
                            import re
                            match = re.search(r'(\d{3,}[\+,\d]*)\s*connection', text, re.IGNORECASE)
                            if match:
                                number = match.group(1).replace(',', '')
                                insights["connections"] = number if '+' in text else f"{number}+"
                                logger.info(f"Found connections: {insights['connections']} (from text: '{text}')")
                                break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Connections extraction failed: {e}")
            
            # === Work Experience (All Jobs) ===
            try:
                # Scroll to Experience section
                try:
                    page.evaluate('document.querySelector("#experience")?.scrollIntoView()')
                    time.sleep(1)
                except:
                    pass
                
                # Look for all experience items
                exp_selectors = [
                    'li.artdeco-list__item',  # Main experience list items
                    'div[data-view-name="profile-component-entity"]',
                ]
                
                for selector in exp_selectors:
                    try:
                        all_exp_elements = page.query_selector_all(selector)
                        
                        for idx, exp_element in enumerate(all_exp_elements[:10]):  # Limit to 10 jobs
                            try:
                                exp_text = exp_element.inner_text()
                                lines = [l.strip() for l in exp_text.split('\n') if l.strip()]
                                
                                if len(lines) >= 1:
                                    # Parse experience entry
                                    experience = {
                                        "title": None,
                                        "company": None,
                                        "duration": None,
                                        "location": None
                                    }
                                    
                                    first_line = lines[0]
                                    
                                    # Check if it's combined "Title at Company" format
                                    if ' at ' in first_line:
                                        parts = first_line.split(' at ', 1)
                                        experience["title"] = parts[0].strip()
                                        experience["company"] = parts[1].strip()
                                    else:
                                        experience["title"] = first_line
                                        # Second line is usually company
                                        if len(lines) >= 2:
                                            experience["company"] = lines[1]
                                    
                                    # Look for duration (contains "yr", "mo", or date patterns)
                                    for line in lines[1:]:
                                        if any(x in line.lower() for x in ['yr', 'mo', 'year', 'month', '·']):
                                            experience["duration"] = line
                                            break
                                    
                                    # Add to experiences list
                                    insights["experiences"].append(experience)
                                    
                                    # First one is current position
                                    if idx == 0:
                                        insights["current_position"]["title"] = experience["title"]
                                        insights["current_position"]["company"] = experience["company"]
                                        insights["current_position"]["duration"] = experience["duration"]
                                        logger.info(f"Found current position: {experience['title']} at {experience['company']}")
                                    
                            except Exception as e:
                                logger.debug(f"Failed to parse experience {idx}: {e}")
                                continue
                        
                        logger.info(f"Extracted {len(insights['experiences'])} work experiences")
                        break
                        
                    except Exception as e:
                        logger.debug(f"Failed with selector {selector}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Experience extraction failed: {e}")
            
            # === Headline (existing) ===
            headline_selectors = [
                'h1.text-heading-xlarge',
                'div.text-body-medium.break-words',
                'h2.top-card-layout__headline',
            ]
            
            for selector in headline_selectors:
                try:
                    element = page.wait_for_selector(selector, timeout=5000, state='visible')
                    if element:
                        text = element.inner_text()
                        if text and len(text) > 3:
                            insights["headline"] = text.strip()
                            logger.info(f"Found headline: {insights['headline'][:50]}...")
                            break
                except:
                    continue
            
            # === About Section (existing) ===
            about_selectors = [
                '#about ~ .display-flex .inline-show-more-text',
                'section.pv-about-section .pv-about__summary-text',
                'div.pv-shared-text-with-see-more',
            ]
            
            for selector in about_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.inner_text()
                        if text and len(text) > 10:
                            insights["about"] = text.strip()
                            logger.info(f"Found about section ({len(text)} chars)")
                            break
                except:
                    continue
            
            # === Fallback to Metadata ===
            if not insights["headline"]:
                soup = BeautifulSoup(page.content(), 'html.parser')
                
                # OpenGraph
                og_title = soup.find('meta', property='og:title')
                if og_title and og_title.get('content'):
                    content = og_title['content']
                    if '|' in content:
                        parts = content.split('|')[0].strip()
                        if ' - ' in parts:
                            insights["headline"] = parts.split(' - ', 1)[1].strip()
                
                # Meta description
                if not insights["about"]:
                    og_desc = soup.find('meta', property='og:description')
                    if og_desc and og_desc.get('content'):
                        insights["about"] = og_desc['content'].strip()
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
        
        return insights

    def _simulate_human(self, page: Page):
        """Simulate human-like behavior to avoid detection."""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(200, 1600)
                y = random.randint(200, 900)
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.2, 0.5))
            
            # Scroll naturally
            scroll_amount = random.randint(300, 700)
            page.evaluate(f'window.scrollBy({{top: {scroll_amount}, behavior: "smooth"}})')
            time.sleep(random.uniform(1, 2))
            
            # Scroll back up a bit
            page.evaluate(f'window.scrollBy({{top: -{scroll_amount // 2}, behavior: "smooth"}})')
            time.sleep(random.uniform(0.5, 1))
            
        except Exception as e:
            logger.debug(f"Human simulation warning: {e}")

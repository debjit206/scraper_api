import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)

class PlaywrightInstagramScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def get_user_reels(self, username: str, max_posts: int = 10) -> List[Dict[str, Any]]:
        """Scrape Instagram reels using Playwright"""
        try:
            self.page = await self.browser.new_page()
            
            # Set user agent to look more like a real browser
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Navigate to Instagram profile
            profile_url = f"https://www.instagram.com/{username}/"
            logger.info(f"Navigating to: {profile_url}")
            
            await self.page.goto(profile_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Check if profile exists
            if "Sorry, this page isn't available." in await self.page.content():
                logger.error(f"Profile not found: {username}")
                return []
            
            # Click on reels tab
            try:
                reels_tab = await self.page.wait_for_selector('a[href*="/reels/"]', timeout=10000)
                await reels_tab.click()
                await asyncio.sleep(3)
                logger.info("Clicked on reels tab")
            except Exception as e:
                logger.warning(f"Could not find reels tab: {e}")
                # Try to find posts instead
                pass
            
            # Wait for content to load
            await asyncio.sleep(5)
            
            # Extract reel links
            reel_links = await self.page.query_selector_all('a[href*="/reel/"]')
            logger.info(f"Found {len(reel_links)} reel links")
            
            reels_data = []
            for i, link in enumerate(reel_links[:max_posts]):
                try:
                    href = await link.get_attribute('href')
                    if href:
                        shortcode = self.extract_shortcode_from_url(href)
                        if shortcode:
                            reel_data = {
                                'url': f"https://www.instagram.com{href}",
                                'shortcode': shortcode,
                                'username': username,
                                'likes': 0,  # Will be updated if we can scrape individual posts
                                'comments': 0,
                                'views': 0,
                                'posted_time': 0,
                                'video_duration': 0.0,
                                'dimensions': {'width': 1080, 'height': 1920},
                                'numbers_of_qualities': 1
                            }
                            reels_data.append(reel_data)
                            logger.info(f"Added reel: {shortcode}")
                except Exception as e:
                    logger.error(f"Error processing reel {i}: {e}")
                    continue
            
            return reels_data
            
        except Exception as e:
            logger.error(f"Error scraping profile {username}: {e}")
            return []
    
    def extract_shortcode_from_url(self, url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL"""
        if not url:
            return None
        
        patterns = [
            r'/reel/([^/?]+)',
            r'/p/([^/?]+)',
            r'reel/([^/?]+)',
            r'p/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

# Helper function to use the scraper
async def scrape_user_reels_playwright(username: str, max_posts: int = 10) -> List[Dict[str, Any]]:
    """Scrape user reels using Playwright"""
    async with PlaywrightInstagramScraper() as scraper:
        return await scraper.get_user_reels(username, max_posts)

# Synchronous wrapper for Flask
def scrape_user_reels_sync(username: str, max_posts: int = 10) -> List[Dict[str, Any]]:
    """Synchronous wrapper for Playwright scraper"""
    return asyncio.run(scrape_user_reels_playwright(username, max_posts)) 
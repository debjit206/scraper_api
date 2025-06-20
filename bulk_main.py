import pandas as pd
import json
import re
from typing import List, Dict, Any, Optional
from reelscraper import ReelScraper, ReelMultiScraper
from reelscraper.utils import LoggerManager
from reelscraper.utils.database import DBManager

# Configure logger and optional DB manager
logger = LoggerManager()
db_manager = DBManager(db_url="sqlite:///myreels.db")

# Create a single scraper instance
single_scraper = ReelScraper(timeout=30, proxy=None, logger_manager=logger)

# MultiScraper for concurrency, database integration, and auto-logging
multi_scraper = ReelMultiScraper(
    single_scraper,
    max_workers=5,
    db_manager=None,
)

def extract_shortcode_from_url(url: str) -> Optional[str]:
    """Extract shortcode from Instagram post/reel URL"""
    if not url:
        return None
    
    # Patterns to match Instagram post/reel URLs
    patterns = [
        r'/reel/([^/?]+)',
        r'/p/([^/?]+)',
        r'reel/([^/?]+)',
        r'p/([^/?]+)',
        r'instagram\.com/reel/([^/?]+)',
        r'instagram\.com/p/([^/?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def match_posts_with_targets(scraped_reels: List[Dict[str, Any]], target_links: List[str]) -> List[Dict[str, Any]]:
    """Match scraped reels with target post links based on shortcode"""
    matched_posts = []
    
    # Extract shortcodes from target links
    target_shortcodes = {}
    for link in target_links:
        shortcode = extract_shortcode_from_url(link)
        if shortcode:
            target_shortcodes[shortcode] = link
    
    print(f"🔍 Looking for {len(target_shortcodes)} target shortcodes: {list(target_shortcodes.keys())}")
    
    # Match scraped reels with target shortcodes
    for reel in scraped_reels:
        reel_shortcode = reel.get('shortcode')
        if reel_shortcode and reel_shortcode in target_shortcodes:
            matched_post = {
                'username': reel.get('username'),
                'target_link': target_shortcodes[reel_shortcode],
                'matched_post_data': {
                    'url': reel.get('url'),
                    'shortcode': reel.get('shortcode'),
                    'likes': reel.get('likes', 0),
                    'comments': reel.get('comments', 0),
                    'views': reel.get('views', 0),
                    'posted_time': reel.get('posted_time', 0),
                    'video_duration': reel.get('video_duration', 0.0),
                    'dimensions': reel.get('dimensions', {}),
                    'numbers_of_qualities': reel.get('numbers_of_qualities', 1)
                }
            }
            matched_posts.append(matched_post)
            print(f"✅ Matched: {reel_shortcode} for user {reel.get('username')}")
    
    return matched_posts

def process_excel_input(excel_file_path: str, max_posts_per_profile: int = 10) -> List[Dict[str, Any]]:
    """Process Excel file and return matched posts data"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_file_path)
        print(f"📊 Loaded {len(df)} rows from {excel_file_path}")
        
        # Validate required columns
        required_columns = ['username', 'post_link']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean and validate data
        df = df.dropna(subset=['username', 'post_link'])
        df['username'] = df['username'].astype(str).str.strip()
        df['post_link'] = df['post_link'].astype(str).str.strip()
        
        print(f"📋 Processing {len(df)} valid rows")
        
        # Group by username to get unique usernames and their target links
        username_groups = df.groupby('username')['post_link'].apply(list).to_dict()
        
        print(f"👥 Found {len(username_groups)} unique usernames")
        
        # Create temporary accounts file for scraping
        temp_accounts_file = "temp_accounts.txt"
        with open(temp_accounts_file, 'w', encoding='utf-8') as f:
            for username in username_groups.keys():
                f.write(f"{username}\n")
        
        # Scrape accounts concurrently
        print("🚀 Starting to scrape accounts...")
        all_reels = multi_scraper.scrape_accounts(
            accounts_file=temp_accounts_file,
            max_posts_per_profile=max_posts_per_profile,
            max_retires_per_profile=10
        )
        
        if all_reels is None:
            print("❌ No reels returned from scraper")
            return []
        
        print(f"📹 Scraped {len(all_reels)} total reels")
        
        # Match posts with target links
        all_matched_posts = []
        for username, target_links in username_groups.items():
            # Filter reels for this username
            user_reels = [reel for reel in all_reels if reel.get('username') == username]
            print(f"🔍 Processing {len(user_reels)} reels for {username}")
            
            # Match with target links
            matched_posts = match_posts_with_targets(user_reels, target_links)
            all_matched_posts.extend(matched_posts)
        
        print(f"✅ Total matched posts: {len(all_matched_posts)}")
        return all_matched_posts
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        return []

def save_results_to_json(matched_posts: List[Dict[str, Any]], output_file: str = "matched_posts.json"):
    """Save matched posts data to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(matched_posts, f, ensure_ascii=False, indent=2)
        print(f"💾 Results saved to {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    # Excel file path - update this to your input file
    excel_file_path = "input.xlsx"
    
    # Process the Excel file
    matched_posts = process_excel_input(excel_file_path, max_posts_per_profile=10)
    
    if matched_posts:
        # Save results to JSON
        save_results_to_json(matched_posts)
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"Total matched posts: {len(matched_posts)}")
        
        # Group by username for summary
        username_counts = {}
        for post in matched_posts:
            username = post['username']
            username_counts[username] = username_counts.get(username, 0) + 1
        
        print(f"Users with matched posts: {len(username_counts)}")
        for username, count in username_counts.items():
            print(f"  - {username}: {count} posts")
    else:
        print("❌ No matched posts found")
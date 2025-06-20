from flask import Flask, request, jsonify
from reelscraper import ReelScraper
from reelscraper.utils import LoggerManager
from bulk_main import extract_shortcode_from_url, match_posts_with_targets
import traceback
import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize scraper with configurable settings
scraper = ReelScraper(
    timeout=int(os.getenv('SCRAPER_TIMEOUT', 30)),
    proxy=os.getenv('SCRAPER_PROXY', None),
    logger_manager=LoggerManager()
)

def validate_request_data(data: Dict[str, Any]) -> tuple[bool, str, Dict[str, Any]]:
    """Validate incoming request data"""
    if not data:
        return False, "Request body is required", {}
    
    username = data.get("username")
    post_links = data.get("post_links")
    
    if not username:
        return False, "username is required", {}
    
    if not post_links:
        return False, "post_links is required", {}
    
    if not isinstance(post_links, list):
        return False, "post_links must be a list", {}
    
    if len(post_links) == 0:
        return False, "post_links cannot be empty", {}
    
    # Validate each post link
    for i, link in enumerate(post_links):
        if not isinstance(link, str):
            return False, f"post_links[{i}] must be a string", {}
        if not link.strip():
            return False, f"post_links[{i}] cannot be empty", {}
    
    return True, "", {"username": username.strip(), "post_links": [link.strip() for link in post_links]}

def create_response(success: bool, data: Any = None, error: str = None, status_code: int = 200) -> tuple[Dict[str, Any], int]:
    """Create standardized API response"""
    response = {
        "success": success,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if success and data is not None:
        response["data"] = data
    elif not success and error:
        response["error"] = error
    
    return response, status_code

@app.route("/v1/fetch-instagram-post", methods=["POST"])
def fetch_instagram_post():
    """API endpoint to fetch and match Instagram posts"""
    try:
        # Get request data
        data = request.get_json()
        
        # Validate request data
        is_valid, error_msg, validated_data = validate_request_data(data)
        if not is_valid:
            return jsonify(*create_response(False, error=error_msg, status_code=400))
        
        username = validated_data["username"]
        post_links = validated_data["post_links"]
        
        logger.info(f"📥 Processing request for username: {username}, post_links: {len(post_links)}")
        
        # Extract shortcodes for logging
        shortcodes = []
        for link in post_links:
            shortcode = extract_shortcode_from_url(link)
            if shortcode:
                shortcodes.append(shortcode)
        
        logger.info(f"🔍 Looking for shortcodes: {shortcodes}")
        
        # Scrape latest posts from user
        max_posts = int(request.args.get('max_posts', 10))
        logger.info(f"🚀 Scraping up to {max_posts} posts for user: {username}")
        
        reels = scraper.get_user_reels(username, max_posts=max_posts)
        
        if not reels:
            logger.warning(f"❌ No reels found for user: {username}")
            return jsonify(*create_response(
                False, 
                error=f"No reels found for user '{username}'", 
                status_code=404
            ))
        
        logger.info(f"📹 Scraped {len(reels)} reels for user: {username}")
        
        # Match with provided post links
        matched = match_posts_with_targets(reels, post_links)
        
        logger.info(f"✅ Found {len(matched)} matched posts for user: {username}")
        
        # Create response with metadata
        response_data = {
            "username": username,
            "total_reels_scraped": len(reels),
            "total_target_links": len(post_links),
            "matched_posts_count": len(matched),
            "matched_posts": matched
        }
        
        return jsonify(*create_response(True, data=response_data))
        
    except Exception as e:
        logger.error(f"❌ Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify(*create_response(
            False, 
            error=f"Internal server error: {str(e)}", 
            status_code=500
        ))

@app.route("/v1/health", methods=["GET"])
def health_check():
    """Health check endpoint for GCP"""
    return jsonify(*create_response(True, data={"status": "healthy", "service": "instagram-post-matcher"}))

@app.route("/v1/status", methods=["GET"])
def status():
    """Detailed status endpoint"""
    return jsonify(*create_response(True, data={
        "service": "Instagram Post Matcher API",
        "version": "1.0.0",
        "status": "running",
        "scraper_timeout": scraper.timeout,
        "endpoints": {
            "fetch_posts": "/v1/fetch-instagram-post",
            "health": "/v1/health",
            "status": "/v1/status"
        }
    }))

@app.route("/", methods=["GET"])
def home():
    """Root endpoint"""
    return jsonify(*create_response(True, data={
        "message": "Instagram Post Match API is running!",
        "documentation": {
            "fetch_posts": "POST /v1/fetch-instagram-post",
            "health": "GET /v1/health",
            "status": "GET /v1/status"
        }
    }))

@app.errorhandler(404)
def not_found(error):
    return jsonify(*create_response(False, error="Endpoint not found", status_code=404))

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(*create_response(False, error="Method not allowed", status_code=405))

@app.errorhandler(500)
def internal_error(error):
    return jsonify(*create_response(False, error="Internal server error", status_code=500))

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting Instagram Post Matcher API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

# Instagram Post Matcher API Documentation

## Overview

This API allows you to fetch Instagram posts for a specific username and match them with provided post links. It's designed for deployment on Google Cloud Platform (GCP).

## Base URL

```
https://your-app-id.appspot.com
```

## Authentication

Currently, the API doesn't require authentication. For production use, consider implementing API keys or OAuth.

## Endpoints

### 1. Health Check

**GET** `/v1/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "status": "healthy",
    "service": "instagram-post-matcher"
  }
}
```

### 2. Service Status

**GET** `/v1/status`

Get detailed service information.

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "service": "Instagram Post Matcher API",
    "version": "1.0.0",
    "status": "running",
    "scraper_timeout": 30,
    "endpoints": {
      "fetch_posts": "/v1/fetch-instagram-post",
      "health": "/v1/health",
      "status": "/v1/status"
    }
  }
}
```

### 3. Fetch Instagram Posts

**POST** `/v1/fetch-instagram-post`

Fetch and match Instagram posts for a specific username.

**Request Body:**
```json
{
  "username": "nasa",
  "post_links": [
    "https://www.instagram.com/reel/C8X9Y2Z1ABC/",
    "https://www.instagram.com/p/C8X9Y2Z1DEF/"
  ]
}
```

**Query Parameters:**
- `max_posts` (optional): Maximum number of posts to scrape (default: 10)

**Example Request:**
```bash
curl -X POST "https://your-app-id.appspot.com/v1/fetch-instagram-post?max_posts=15" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nasa",
    "post_links": [
      "https://www.instagram.com/reel/C8X9Y2Z1ABC/",
      "https://www.instagram.com/p/C8X9Y2Z1DEF/"
    ]
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "username": "nasa",
    "total_reels_scraped": 8,
    "total_target_links": 2,
    "matched_posts_count": 2,
    "matched_posts": [
      {
        "username": "nasa",
        "target_link": "https://www.instagram.com/reel/C8X9Y2Z1ABC/",
        "matched_post_data": {
          "url": "https://www.instagram.com/reel/C8X9Y2Z1ABC/",
          "shortcode": "C8X9Y2Z1ABC",
          "likes": 1500,
          "comments": 250,
          "views": 50000,
          "posted_time": 1640995200,
          "video_duration": 30.5,
          "dimensions": {
            "width": 1080,
            "height": 1920
          },
          "numbers_of_qualities": 3
        }
      },
      {
        "username": "nasa",
        "target_link": "https://www.instagram.com/p/C8X9Y2Z1DEF/",
        "matched_post_data": {
          "url": "https://www.instagram.com/p/C8X9Y2Z1DEF/",
          "shortcode": "C8X9Y2Z1DEF",
          "likes": 2200,
          "comments": 180,
          "views": 75000,
          "posted_time": 1640995800,
          "video_duration": 45.2,
          "dimensions": {
            "width": 1080,
            "height": 1920
          },
          "numbers_of_qualities": 3
        }
      }
    ]
  }
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "success": false,
  "timestamp": "2024-01-15T10:30:00Z",
  "error": "username is required"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "timestamp": "2024-01-15T10:30:00Z",
  "error": "No reels found for user 'invalid_user'"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "timestamp": "2024-01-15T10:30:00Z",
  "error": "Internal server error: Network timeout"
}
```

## Data Models

### Request Model

```json
{
  "username": "string (required)",
  "post_links": ["string (required, non-empty)"]
}
```

### Response Model

```json
{
  "success": "boolean",
  "timestamp": "string (ISO 8601)",
  "data": {
    "username": "string",
    "total_reels_scraped": "number",
    "total_target_links": "number",
    "matched_posts_count": "number",
    "matched_posts": [
      {
        "username": "string",
        "target_link": "string",
        "matched_post_data": {
          "url": "string",
          "shortcode": "string",
          "likes": "number",
          "comments": "number",
          "views": "number",
          "posted_time": "number (Unix timestamp)",
          "video_duration": "number",
          "dimensions": {
            "width": "number",
            "height": "number"
          },
          "numbers_of_qualities": "number"
        }
      }
    ]
  }
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - User or posts not found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port to run the server on | 5000 |
| `FLASK_DEBUG` | Enable debug mode | False |
| `SCRAPER_TIMEOUT` | Scraper timeout in seconds | 30 |
| `SCRAPER_PROXY` | Proxy configuration | None |

## Deployment

### Google App Engine

1. Install Google Cloud SDK
2. Deploy using:
```bash
gcloud app deploy app.yaml
```

### Docker

1. Build the image:
```bash
docker build -t instagram-post-matcher .
```

2. Run the container:
```bash
docker run -p 5000:5000 instagram-post-matcher
```

## Testing

### Using curl

```bash
# Health check
curl https://your-app-id.appspot.com/v1/health

# Fetch posts
curl -X POST "https://your-app-id.appspot.com/v1/fetch-instagram-post" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nasa",
    "post_links": ["https://www.instagram.com/reel/C8X9Y2Z1ABC/"]
  }'
```

### Using Python

```python
import requests
import json

url = "https://your-app-id.appspot.com/v1/fetch-instagram-post"
data = {
    "username": "nasa",
    "post_links": [
        "https://www.instagram.com/reel/C8X9Y2Z1ABC/"
    ]
}

response = requests.post(url, json=data)
result = response.json()

if result["success"]:
    print(f"Found {result['data']['matched_posts_count']} matched posts")
    for post in result["data"]["matched_posts"]:
        print(f"Post: {post['matched_post_data']['shortcode']}")
else:
    print(f"Error: {result['error']}")
```

## Notes

- The API only returns posts that match the provided target links
- If a target link doesn't match any scraped posts, it won't appear in the results
- The API supports both `/reel/` and `/p/` URL formats
- Scraping is limited to the most recent posts (controlled by `max_posts` parameter)
- All timestamps are in UTC 
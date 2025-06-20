import requests
import json

def test_api():
    # Try with a different username that might work better
    test_cases = [
        {
            "username": "nasa",
            "post_links": ["https://www.instagram.com/reel/DKaidwvJm-Y/"]
        },
        {
            "username": "virat.kohli", 
            "post_links": ["https://www.instagram.com/reel/DKG7fpwRZiT/"]
        }
    ]
    
    url = "http://localhost:5000/v1/fetch-instagram-post"
    
    for i, data in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {data['username']}")
        print(f"📡 Sending request to: {url}")
        print(f"📋 Data: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        try:
            response = requests.post(url, json=data, timeout=60)
            
            # Handle the response properly
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
            else:
                print(f"❌ Unexpected response type: {response.headers.get('content-type')}")
                print(f"Response text: {response.text}")
                continue
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            
            # Check if it's a list (error response) or dict (success response)
            if isinstance(result, list) and len(result) > 0:
                # Error response format
                error_data = result[0]
                if not error_data.get("success", True):
                    print(f"❌ API Error: {error_data.get('error', 'Unknown error')}")
                else:
                    print("✅ Success!")
            elif isinstance(result, dict):
                # Success response format
                if result.get("success"):
                    matched_count = result["data"]["matched_posts_count"]
                    print(f"✅ Success! Found {matched_count} matched posts")
                    
                    for post in result["data"]["matched_posts"]:
                        post_data = post["matched_post_data"]
                        print(f"📱 Post: {post_data['shortcode']}")
                        print(f"   Likes: {post_data['likes']:,}")
                        print(f"   Comments: {post_data['comments']:,}")
                        print(f"   Views: {post_data['views']:,}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ Unexpected response format: {type(result)}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the API server is running!")
            print("   Run: python app.py")
            break
        except requests.exceptions.Timeout:
            print("❌ Timeout: Request took too long")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api() 
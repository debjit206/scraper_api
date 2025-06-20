import requests
import json

def simple_test():
    print("🧪 Simple API Test")
    print("=" * 50)
    
    # Test with a simple username
    url = "http://localhost:5000/v1/fetch-instagram-post"
    data = {
        "username": "nasa",
        "post_links": ["https://www.instagram.com/reel/DKaidwvJm-Y/"]
    }
    
    print(f"📡 Testing with username: {data['username']}")
    print(f"🔗 Target post: {data['post_links'][0]}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API responded successfully!")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    simple_test() 
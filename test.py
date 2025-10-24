import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_generate():
    """Test the generate endpoint"""
    print("=" * 60, flush=True)
    print("Testing: POST /api/pages/generate", flush=True)
    print("=" * 60, flush=True)
    
    payload = {
        "industry": "Similar to the provided URL products and services but avoid similar name",
        "offer": "Similar to the provided URL products and services",
        "target_audience": "People",
        "brand_tone": "Similar to the provided URL tone",
        
    }
    
    print(f"\nPayload being sent:", flush=True)
    print(json.dumps(payload, indent=2), flush=True)
    
    try:
        print("\nSending request... (this may take 10-30 seconds)", flush=True)
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/pages/generate",
            json=payload,
            timeout=60  # Increased timeout
        )
        
        elapsed = time.time() - start_time
        print(f"✓ Response received in {elapsed:.1f} seconds", flush=True)
        print(f"Status: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            page_id = data.get("pageId")
            print(f"✓ Generated page: {page_id}", flush=True)
            print(f"  Version: {data.get('version')}", flush=True)
            print(f"  Sections: {len(data.get('sections', []))}", flush=True)
            
            # Print first section to see if it has KFC-specific content
            if data.get('sections'):
                print(f"\nFirst section (hero):", flush=True)
                hero = data['sections'][0]
                print(f"  Type: {hero.get('type')}", flush=True)
                print(f"  Headline: {hero.get('data', {}).get('headline')}", flush=True)
                print(f"  Subheadline: {hero.get('data', {}).get('subheadline')}", flush=True)
            
            print(f"\nFull response:", flush=True)
            print(json.dumps(data, indent=2), flush=True)
            return page_id
        else:
            print(f"✗ Error: {response.text}", flush=True)
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (LLM is slow, try increasing timeout)", flush=True)
    except Exception as e:
        print(f"✗ Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return None

def test_health():
    """Test health check"""
    print("=" * 60, flush=True)
    print("Testing: GET /health", flush=True)
    print("=" * 60, flush=True)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}", flush=True)
        print(f"Response: {response.json()}", flush=True)
        print("✓ Server is running\n", flush=True)
        return True
    except Exception as e:
        print(f"✗ Server is not running: {str(e)}", flush=True)
        return False

if __name__ == "__main__":
    # Test health first
    if not test_health():
        print("Start the server first: python main.py", flush=True)
        exit(1)
    
    # Test generate
    page_id = test_generate()
    
    if page_id:
        print("\n✓ Test passed!", flush=True)
    else:
        print("\n✗ Test failed!", flush=True)
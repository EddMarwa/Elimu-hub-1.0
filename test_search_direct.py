#!/usr/bin/env python3
"""
Direct test of search endpoint
"""

import requests

def test_search_direct():
    """Test search endpoint directly"""
    print("🔍 Direct Search Test")
    print("=" * 20)
    
    # Test the search endpoint directly
    url = "http://localhost:8000/api/v1/search"
    params = {"query": "derivative", "limit": 3}
    
    print(f"Testing: {url} with params: {params}")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Response: {data}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test original search endpoint (without api/v1)
    print(f"\n🔍 Testing original search endpoint...")
    try:
        response = requests.get("http://localhost:8000/search", params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Response: {data}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search_direct()

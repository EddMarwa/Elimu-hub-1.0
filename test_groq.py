#!/usr/bin/env python3
"""
Test GROQ API key functionality
"""

import os
import requests

def test_groq_api():
    """Test if GROQ API key is working"""
    groq_key = os.getenv("GROQ_API_KEY")
    
    print("🔑 Testing GROQ API Key")
    print("=" * 25)
    
    if not groq_key:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {groq_key[:10]}...{groq_key[-4:]}")
    
    # Test API call
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2? Answer briefly."
            }
        ],
        "model": "llama3-8b-8192",
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    try:
        print("\n🚀 Making test API call...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"✅ API call successful!")
            print(f"📝 Response: {answer}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API call error: {e}")
        return False

if __name__ == "__main__":
    test_groq_api()

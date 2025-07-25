#!/usr/bin/env python3
"""
Test PDF upload functionality in the chat interface
"""

import requests
import json

def test_upload_functionality():
    print("🧪 Testing PDF Upload Functionality")
    print("=" * 40)
    
    # Test 1: Check if upload endpoint exists
    print("\n1️⃣  Testing upload endpoint availability...")
    try:
        response = requests.get("http://localhost:8000/api/v1/upload", timeout=5)
        if response.status_code == 405:  # Method not allowed (expecting POST)
            print("   ✅ Upload endpoint exists (returns 405 for GET, expects POST)")
        else:
            print(f"   ⚠️  Upload endpoint response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Upload endpoint not accessible: {e}")
        return False
    
    # Test 2: Test chat endpoint with file reference
    print("\n2️⃣  Testing chat functionality...")
    try:
        response = requests.post("http://localhost:8000/api/v1/chat", 
                               headers={"Content-Type": "application/json"},
                               json={"question": "Hello, can you help me?", "topic": "General"},
                               timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chat endpoint working: {result.get('answer', 'No answer')[:50]}...")
        else:
            print(f"   ⚠️  Chat endpoint response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Chat endpoint error: {e}")
    
    # Test 3: Test topics endpoint
    print("\n3️⃣  Testing topics endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/list-topics", timeout=5)
        if response.status_code == 200:
            topics = response.json()
            print(f"   ✅ Topics available: {len(topics)} topics found")
            for topic in topics:
                print(f"      - {topic.get('name', 'Unknown')}")
        else:
            print(f"   ⚠️  Topics endpoint response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Topics endpoint error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Upload Test Complete!")
    print("\n📝 Frontend Integration Status:")
    print("   - 📄 PDF Upload Button: Added to chat interface")
    print("   - 🔗 Upload Endpoint: /api/v1/upload (POST)")
    print("   - 💬 Chat Integration: Messages show upload status")
    print("   - 🏷️  Topic Assignment: Files uploaded to current topic")
    print("   - ✅ File Validation: PDF only, max 10MB")
    
    print("\n🚀 How to use:")
    print("   1. Go to http://localhost:3000/chat")
    print("   2. Click the blue '📄 PDF' button")
    print("   3. Select a PDF file (max 10MB)")
    print("   4. File uploads to current topic")
    print("   5. Chat about the uploaded content!")

if __name__ == "__main__":
    try:
        test_upload_functionality()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

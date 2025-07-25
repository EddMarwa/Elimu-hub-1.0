#!/usr/bin/env python3
"""
Simple test for Elimu Hub - Test PDF upload and basic functionality
"""

import requests
import json
import time
import os

# API base URL (updated for minimal server)
BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the API is running."""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running!")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_pdf_upload():
    """Test PDF upload without authentication (if possible)."""
    print("📄 Testing document upload...")
    
    # Create a simple test content file
    test_content = """Biology Study Guide

Photosynthesis:
Photosynthesis is the process by which plants convert light energy into chemical energy. 
The basic equation is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2

This process occurs in chloroplasts and involves:
- Light-dependent reactions in the thylakoids  
- Light-independent reactions (Calvin cycle) in the stroma

Cell Division:
Cell division includes mitosis (for growth) and meiosis (for reproduction).
Mitosis produces identical diploid cells, while meiosis produces genetically diverse gametes.

DNA Structure:
DNA has a double helix structure with complementary base pairs:
- Adenine (A) pairs with Thymine (T)
- Guanine (G) pairs with Cytosine (C)

Cellular Respiration:
Cellular respiration is the process by which cells break down glucose to produce ATP energy.
This process occurs in mitochondria and is essentially the reverse of photosynthesis.
The equation is: C6H12O6 + 6O2 → 6CO2 + 6H2O + ATP
"""
    
    # Write test content to a file
    test_file_path = "test_biology.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_biology.txt", f, "text/plain")}
            data = {"topic": "Biology"}  # Updated for minimal server
            
            response = requests.post(f"{BASE_URL}/upload", 
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded successfully!")
            print(f"   ID: {result.get('id', 'N/A')}")
            print(f"   Filename: {result.get('filename', 'N/A')}")
            print(f"   Topic: {result.get('topic', 'N/A')}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_llm_completion():
    """Test the chat functionality."""
    print("🤖 Testing chat functionality...")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", 
            json={
                "question": "What is photosynthesis and how does it work?",
                "topic": "Biology",
                "max_tokens": 200
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat successful!")
            
            answer = result.get("answer", "No answer returned")
            sources = result.get("sources", [])
            
            print(f"🎯 Answer: {answer[:200]}...")
            if sources:
                print(f"📚 Sources: {', '.join(sources)}")
            
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_search():
    """Test basic search functionality."""
    print("🔍 Testing search functionality...")
    
    try:
        response = requests.get(f"{BASE_URL}/search", 
            params={"query": "photosynthesis", "limit": 3}
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful! Found {len(results)} results")
            
            for i, result in enumerate(results[:2], 1):
                content = result.get("content", "")[:100] + "..."
                score = result.get("score", 0)
                print(f"   {i}. Score: {score:.3f} - {content}")
            
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def main():
    """Run basic tests."""
    print("🚀 Starting Elimu Hub Basic Test")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("Cannot proceed - API is not running")
        return
    
    # Test 2: PDF upload
    print()
    upload_success = test_pdf_upload()
    
    # Test 3: Chat functionality
    print()
    chat_success = test_llm_completion()
    
    # Test 4: Search (might work even without upload)
    print()
    search_success = test_search()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   ✅ API Health: {'PASS' if True else 'FAIL'}")
    print(f"   📄 Document Upload: {'PASS' if upload_success else 'FAIL'}")
    print(f"   🤖 Chat/RAG: {'PASS' if chat_success else 'FAIL'}")
    print(f"   🔍 Search: {'PASS' if search_success else 'FAIL'}")
    
    if upload_success or chat_success:
        print("\n🎉 Your Elimu Hub is working!")
        print("\nNext steps:")
        print("1. Upload more PDF documents") 
        print("2. Set GROQ_API_KEY environment variable for AI responses")
        print("3. Try asking questions about your uploaded content")
        print("\nAPI Documentation: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some features need configuration:")
        print("1. Set GROQ_API_KEY in environment for AI responses")
        print("2. Upload documents to test search")
        print("3. Check logs for errors")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the backend server is running on http://localhost:8000")

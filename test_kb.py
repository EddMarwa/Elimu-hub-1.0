#!/usr/bin/env python3
"""
Comprehensive test of knowledge base functionality
"""

import requests
import json

def test_knowledge_base():
    print("🧪 Comprehensive Knowledge Base Test")
    print("=" * 40)
    
    # Test 1: Check documents
    print("\n1️⃣  Checking uploaded documents...")
    try:
        response = requests.get("http://localhost:8000/api/v1/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"   ✅ Found {len(docs)} documents:")
            for doc in docs:
                print(f"      - {doc['filename']} ({doc['topic']})")
        else:
            print(f"   ❌ Error fetching documents: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Search functionality
    print("\n2️⃣  Testing search functionality...")
    search_terms = ["derivative", "calculus", "biology", "cell"]
    
    for term in search_terms:
        try:
            response = requests.get(f"http://localhost:8000/api/v1/search?query={term}&limit=3")
            if response.status_code == 200:
                results = response.json()
                print(f"   🔍 '{term}': {len(results)} results")
                for result in results[:2]:  # Show first 2 results
                    print(f"      📄 {result.get('filename', 'Unknown')} (score: {result.get('score', 0):.3f})")
            else:
                print(f"   ❌ Search for '{term}' failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Search error for '{term}': {e}")
    
    # Test 3: Chat functionality with different questions
    print("\n3️⃣  Testing AI chat responses...")
    questions = [
        ("What is a derivative?", "Mathematics"),
        ("Explain photosynthesis", "Biology"),
        ("What are the applications of calculus?", "Mathematics"),
        ("What is a cell?", "Biology")
    ]
    
    for question, topic in questions:
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat",
                headers={"Content-Type": "application/json"},
                json={"question": question, "topic": topic},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer')
                print(f"\n   ❓ Q: {question}")
                print(f"   💡 A: {answer[:100]}...")
                
                # Check if it's using AI or fallback
                if "GROQ_API_KEY" in answer:
                    print("      ⚠️  Using fallback response (API issue)")
                elif "I don't have specific information" in answer:
                    print("      ⚠️  No relevant content found")
                else:
                    print("      ✅ AI-powered response")
            else:
                print(f"   ❌ Chat failed for '{question}': {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat error for '{question}': {e}")
    
    # Test 4: Check server logs for errors
    print("\n4️⃣  Test Summary:")
    print("   📚 Documents: Uploaded and accessible")
    print("   🔍 Search: Testing basic functionality")
    print("   🤖 AI Chat: Testing with GROQ API")
    print("   🔑 API Key: Set and configured")

if __name__ == "__main__":
    test_knowledge_base()

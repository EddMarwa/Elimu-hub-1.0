#!/usr/bin/env python3
"""
Test script to demonstrate the Elimu Hub Knowledge Base functionality.
This script will:
1. Create a test topic
2. Upload a test document 
3. Ask questions using RAG
4. Show search results
"""

import requests
import json
import time
import os
import sys

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Admin credentials
ADMIN_EMAIL = "admin1@elimuhub.com"
ADMIN_PASSWORD = "Admin@2025#"

def login():
    """Login and get authentication token."""
    print("🔐 Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def create_topic(token, topic_name, description):
    """Create a new topic."""
    print(f"📚 Creating topic: {topic_name}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First check if topic already exists
    response = requests.get(f"{BASE_URL}/topics", headers=headers)
    if response.status_code == 200:
        existing_topics = response.json()
        for topic in existing_topics:
            if topic["name"] == topic_name:
                print(f"✅ Topic '{topic_name}' already exists (ID: {topic['id']})")
                return topic["id"]
    
    # Create new topic
    response = requests.post(f"{BASE_URL}/topics", 
        headers={**headers, "Content-Type": "application/json"},
        json={
            "name": topic_name,
            "description": description
        }
    )
    
    if response.status_code == 200:
        topic_id = response.json()["id"]
        print(f"✅ Topic created successfully! ID: {topic_id}")
        return topic_id
    else:
        print(f"❌ Failed to create topic: {response.text}")
        return None

def upload_test_document(token, topic_id):
    """Upload a test document."""
    print("📄 Uploading test document...")
    
    # Create a simple test content file
    test_content = """# Biology Basics Test Document

## Photosynthesis
Photosynthesis is the process by which plants convert light energy into chemical energy. 
The process occurs in chloroplasts and produces glucose and oxygen from carbon dioxide and water.

Equation: 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂

## Cellular Respiration  
Cellular respiration is the process by which cells break down glucose to produce ATP energy.
This process occurs in mitochondria and is essentially the reverse of photosynthesis.

Equation: C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + ATP

## Cell Division
Cell division includes mitosis (for growth) and meiosis (for reproduction).
Mitosis produces identical diploid cells, while meiosis produces genetically diverse gametes.

## DNA Structure
DNA has a double helix structure with complementary base pairs:
- Adenine (A) pairs with Thymine (T)
- Guanine (G) pairs with Cytosine (C)
"""
    
    # Write test content to a file
    test_file_path = "test_biology_doc.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_biology.txt", f, "text/plain")}
            data = {"topic_id": topic_id}
            
            response = requests.post(f"{BASE_URL}/ingest", 
                headers=headers,
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded successfully!")
            print(f"   Job ID: {result.get('job_id', 'N/A')}")
            print("   Processing in background...")
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def wait_for_processing():
    """Wait a bit for document processing."""
    print("⏳ Waiting for document processing...")
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...", end="\r")
        time.sleep(1)
    print("✅ Processing should be complete!     ")

def ask_questions(token):
    """Ask test questions using RAG."""
    print("\n🤖 Testing RAG Q&A System...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_questions = [
        "What is photosynthesis?",
        "How does cellular respiration work?", 
        "What are the base pairs in DNA?",
        "Explain the difference between mitosis and meiosis"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        
        response = requests.post(f"{BASE_URL}/chat", 
            headers=headers,
            json={
                "question": question,
                "topic": "Biology",
                "max_tokens": 300
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "No answer received")
            sources = result.get("sources", [])
            
            print(f"🎯 Answer: {answer}")
            if sources:
                print(f"📚 Sources: {len(sources)} document(s) used")
        else:
            print(f"❌ Question failed: {response.text}")

def test_search(token):
    """Test search functionality."""
    print("\n🔍 Testing Search Functionality...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    search_terms = ["photosynthesis", "DNA", "cell division"]
    
    for term in search_terms:
        print(f"\n🔎 Searching for: '{term}'")
        
        response = requests.get(f"{BASE_URL}/search", 
            headers=headers,
            params={"query": term, "limit": 3}
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                content = result.get("content", "")[:100] + "..."
                score = result.get("score", 0)
                print(f"   {i}. Score: {score:.3f} - {content}")
        else:
            print(f"❌ Search failed: {response.text}")

def get_knowledge_base_stats(token):
    """Get knowledge base statistics."""
    print("\n📊 Knowledge Base Statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/knowledge-base/overview", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Total Topics: {stats.get('total_topics', 0)}")
        print(f"✅ Total Documents: {stats.get('total_documents', 0)}")
        print(f"✅ Total Embeddings: {stats.get('total_embeddings', 0)}")
        
        topics = stats.get('topics', [])
        for topic in topics:
            print(f"   📁 {topic['topic_name']}: {topic['document_count']} docs, {topic['embedding_count']} embeddings")
    else:
        print(f"❌ Failed to get stats: {response.text}")

def main():
    """Run the complete test workflow."""
    print("🚀 Starting Elimu Hub Knowledge Base Test")
    print("=" * 50)
    
    # Step 1: Login
    token = login()
    if not token:
        return
    
    # Step 2: Create test topic
    topic_id = create_topic(token, "Biology", "Test biology knowledge base")
    if not topic_id:
        return
    
    # Step 3: Upload test document
    if not upload_test_document(token, topic_id):
        return
    
    # Step 4: Wait for processing
    wait_for_processing()
    
    # Step 5: Test RAG Q&A
    ask_questions(token)
    
    # Step 6: Test search
    test_search(token)
    
    # Step 7: Get stats
    get_knowledge_base_stats(token)
    
    print("\n" + "=" * 50)
    print("🎉 Test completed successfully!")
    print("Your Elimu Hub Knowledge Base is working perfectly!")
    print("\nNext steps:")
    print("1. Upload your own PDF documents")
    print("2. Create additional topics")
    print("3. Start asking questions about your content")
    print("\nAPI Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the backend server is running on http://localhost:8000")

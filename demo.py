#!/usr/bin/env python3
"""
Quick test script to demonstrate all Elimu Hub functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def demo_elimu_hub():
    print("🎯 Elimu Hub Complete Demo")
    print("=" * 40)
    
    # 1. Check health
    print("\n1️⃣  Testing API Health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.json()['status']}")
    
    # 2. Upload a document
    print("\n2️⃣  Uploading sample document...")
    sample_content = """Machine Learning Basics

Machine Learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task.

Types of Machine Learning:

1. Supervised Learning
   - Uses labeled training data
   - Examples: Classification, Regression
   - Algorithms: Linear Regression, Decision Trees, Neural Networks

2. Unsupervised Learning  
   - Finds patterns in unlabeled data
   - Examples: Clustering, Dimensionality Reduction
   - Algorithms: K-Means, PCA, Autoencoders

3. Reinforcement Learning
   - Learns through interaction with environment
   - Uses rewards and penalties
   - Examples: Game playing, Robotics

Key Concepts:
- Training Data: Examples used to teach the algorithm
- Model: The learned representation of the data
- Features: Individual measurable properties of observations
- Overfitting: When model memorizes training data but fails on new data
- Cross-validation: Technique to test model performance

Applications:
- Image Recognition
- Natural Language Processing
- Recommendation Systems
- Autonomous Vehicles
- Medical Diagnosis
"""
    
    with open("ml_sample.txt", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    with open("ml_sample.txt", "rb") as f:
        files = {"file": ("ml_sample.txt", f, "text/plain")}
        data = {"topic": "Machine Learning"}
        response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
    
    print(f"   Upload result: {response.json()['filename']} → {response.json()['topic']}")
    
    # 3. List documents
    print("\n3️⃣  Listing all documents...")
    response = requests.get(f"{BASE_URL}/documents")
    docs = response.json()
    for doc in docs:
        print(f"   📄 {doc['filename']} (Topic: {doc['topic']})")
    
    # 4. Search for information
    print("\n4️⃣  Searching for 'neural networks'...")
    response = requests.get(f"{BASE_URL}/search", params={"query": "neural networks", "limit": 2})
    results = response.json()
    for i, result in enumerate(results, 1):
        print(f"   🔍 Result {i}: {result['content'][:100]}...")
        print(f"      Source: {result['filename']}, Score: {result['score']:.3f}")
    
    # 5. Ask questions
    print("\n5️⃣  Asking questions about uploaded content...")
    questions = [
        "What is supervised learning?",
        "What are the main types of machine learning?",
        "What is overfitting?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   ❓ Question {i}: {question}")
        response = requests.post(f"{BASE_URL}/chat", json={
            "question": question,
            "topic": "Machine Learning"
        })
        result = response.json()
        answer = result['answer'][:200] + "..." if len(result['answer']) > 200 else result['answer']
        print(f"   💡 Answer: {answer}")
        if result['sources']:
            print(f"   📚 Sources: {', '.join(result['sources'])}")
    
    # 6. Get system stats
    print("\n6️⃣  System Statistics...")
    response = requests.get(f"{BASE_URL}/stats")
    stats = response.json()
    print(f"   📊 Total Documents: {stats['total_documents']}")
    print(f"   📂 Total Topics: {stats['total_topics']}")
    print(f"   ⚡ Status: {stats['status']}")
    
    print("\n" + "=" * 40)
    print("🎉 Demo Complete!")
    print("Your Elimu Hub is fully functional and ready to use!")
    print("\n🔗 Try the interactive API at: http://localhost:8000/docs")
    
    # Cleanup
    import os
    if os.path.exists("ml_sample.txt"):
        os.remove("ml_sample.txt")

if __name__ == "__main__":
    try:
        demo_elimu_hub()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Elimu Hub server")
        print("Please start the server first: python minimal_server.py")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

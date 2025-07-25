#!/usr/bin/env python3

import requests
import json

def test_search():
    """Test the search functionality"""
    print("🔍 Testing search functionality...")
    
    response = requests.get('http://localhost:8000/api/v1/search', params={'query': 'calculus', 'limit': 2})
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'Results found: {len(result)}')
        for r in result:
            print(f'  File: {r["filename"]}')
            print(f'  Page: {r.get("page", "N/A")}')
            print(f'  Content preview: {r["content"][:100]}...')
            print()
    else:
        print('Error:', response.text)

def test_chat():
    """Test the chat functionality"""
    print("💬 Testing AI chat functionality...")
    
    data = {
        'question': 'What is calculus and what are its main concepts?',
        'chatSessionId': 'test-session-123'
    }
    
    response = requests.post('http://localhost:8000/api/v1/chat', json=data)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('AI Answer:')
        print(result['answer'])
        print()
        print(f'Sources used: {len(result.get("sources", []))}')
        for source in result.get('sources', []):
            print(f'  - {source}')
    else:
        print('Error:', response.text)

def test_upload():
    """Test document upload"""
    print("📤 Testing document upload...")
    
    # Create a simple test document
    test_content = """Introduction to Mathematics

Mathematics is the study of numbers, shapes, and patterns. It includes:

1. Arithmetic - Basic operations like addition, subtraction, multiplication, and division
2. Algebra - Working with variables and equations
3. Geometry - Study of shapes and their properties
4. Calculus - Study of change and motion

Page 2 Content:

Advanced topics in mathematics include:
- Linear algebra
- Differential equations
- Statistics and probability
- Number theory

Mathematics is essential for science, engineering, and technology."""
    
    files = {'file': ('test_math.txt', test_content.encode(), 'text/plain')}
    data = {'topic': 'Mathematics', 'chatSessionId': 'test-session-123'}
    
    response = requests.post('http://localhost:8000/api/v1/upload', files=files, data=data)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('Upload successful:')
        print(f'  ID: {result["id"]}')
        print(f'  Filename: {result["filename"]}')
        print(f'  Topic: {result["topic"]}')
    else:
        print('Error:', response.text)

if __name__ == '__main__':
    print("🧪 Testing Elimu Hub API")
    print("=" * 40)
    
    test_search()
    print()
    test_upload()
    print()
    test_chat()

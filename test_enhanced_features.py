#!/usr/bin/env python3

import requests
import json

def test_with_content():
    """Test chat with uploaded content"""
    print("💬 Testing AI chat with uploaded content...")
    
    # Test with a question about the uploaded content
    data = {
        'question': 'What are the main areas of mathematics mentioned in the document?',
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
        for i, source in enumerate(result.get('sources', []), 1):
            if isinstance(source, dict):
                page_info = f" (Page {source.get('page', 'N/A')})" if source.get('page') else ""
                print(f'  {i}. {source.get("filename", "Unknown")}{page_info}')
            else:
                print(f'  {i}. {source}')
    else:
        print('Error:', response.text)

def test_search_with_session():
    """Test search with session ID"""
    print("🔍 Testing search with session ID...")
    
    response = requests.get('http://localhost:8000/api/v1/search', params={
        'query': 'mathematics arithmetic algebra',
        'limit': 3,
        'chatSessionId': 'test-session-123'
    })
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'Results found: {len(result)}')
        for r in result:
            page_info = f" (Page {r.get('page', 'N/A')})" if r.get('page') else ""
            print(f'  File: {r["filename"]}{page_info}')
            print(f'  Content: {r["content"][:100]}...')
            print()
    else:
        print('Error:', response.text)

if __name__ == '__main__':
    print("🧪 Testing Enhanced Elimu Hub Features")
    print("=" * 45)
    
    test_search_with_session()
    print()
    test_with_content()

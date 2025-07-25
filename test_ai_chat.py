#!/usr/bin/env python3

import requests
import json

def test_ai_chat():
    # Test AI chat with uploaded documents
    data = {
        'question': 'What is calculus and what are its main concepts?',
        'topic': 'Mathematics'
    }

    response = requests.post('http://localhost:8000/api/v1/chat', json=data)
    print(f'Chat Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('\nAI Answer:')
        print(result['answer'])
        print(f'\nSources used: {len(result.get("sources", []))} documents')
        
        if result.get('sources'):
            for i, source in enumerate(result['sources'], 1):
                print(f'  {i}. {source["filename"]} (Topic: {source["topic"]})')
    else:
        print('Error:', response.text)

def test_biology_chat():
    # Test with biology question
    data = {
        'question': 'What is photosynthesis?',
        'topic': 'Science'
    }

    response = requests.post('http://localhost:8000/api/v1/chat', json=data)
    print(f'\nBiology Chat Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('\nAI Answer:')
        print(result['answer'])
        print(f'\nSources used: {len(result.get("sources", []))} documents')

if __name__ == '__main__':
    test_ai_chat()
    test_biology_chat()

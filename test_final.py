#!/usr/bin/env python3

import requests

# Test search for 'mathematics'
response = requests.get('http://localhost:8000/api/v1/search', params={
    'query': 'Mathematics',
    'chatSessionId': 'test-session-123'
})

print('Search Response:')
print('Status:', response.status_code)
if response.status_code == 200:
    result = response.json()
    print('Found:', len(result), 'results')
    for r in result:
        print(f'  File: {r["filename"]}')
        print(f'  Page: {r.get("page", "N/A")}')
        print(f'  Content: {r["content"][:150]}...')
        print()
else:
    print('Error:', response.text)

# Now test chat
print("\n" + "="*50)
print("Testing AI Chat:")

data = {
    'question': 'What is mathematics and what are its main areas?',
    'chatSessionId': 'test-session-123'
}

response = requests.post('http://localhost:8000/api/v1/chat', json=data)
print('Status:', response.status_code)

if response.status_code == 200:
    result = response.json()
    print('\nAI Answer:')
    print(result['answer'])
    print(f'\nSources used: {len(result.get("sources", []))}')
    for i, source in enumerate(result.get('sources', []), 1):
        if isinstance(source, dict):
            page_info = f" (Page {source.get('page', 'N/A')})" if source.get('page') else ""
            print(f'  {i}. {source.get("filename", "Unknown")}{page_info}')
        else:
            print(f'  {i}. {source}')
else:
    print('Error:', response.text)

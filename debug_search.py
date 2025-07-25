#!/usr/bin/env python3

import sqlite3

# Test the search logic directly
conn = sqlite3.connect('data/documents.db')
cursor = conn.cursor()

query = 'arithmetic'
chat_session_id = 'test-session-123'

# Test different search approaches
print('Testing different search patterns:')

# 1. Simple LIKE with one word
cursor.execute('''
    SELECT filename, page_number, substr(content, 1, 100) FROM documents 
    WHERE chat_session_id = ? AND LOWER(content) LIKE ?
''', (chat_session_id, f'%{query}%'))

results = cursor.fetchall()
print(f'1. Single word search for "{query}": {len(results)} results')
for result in results:
    print(f'   {result[0]} (Page {result[1]}): {result[2]}...')

# 2. Search for 'mathematics'
query2 = 'mathematics'
cursor.execute('''
    SELECT filename, page_number, substr(content, 1, 100) FROM documents 
    WHERE chat_session_id = ? AND LOWER(content) LIKE ?
''', (chat_session_id, f'%{query2}%'))

results = cursor.fetchall()
print(f'2. Search for "{query2}": {len(results)} results')
for result in results:
    print(f'   {result[0]} (Page {result[1]}): {result[2]}...')

# 3. Show all documents for this session
cursor.execute('''
    SELECT filename, page_number, substr(content, 1, 200) FROM documents 
    WHERE chat_session_id = ?
''', (chat_session_id,))

results = cursor.fetchall()
print(f'3. All documents in session "{chat_session_id}": {len(results)} results')
for result in results:
    print(f'   {result[0]} (Page {result[1]}): {result[2]}...')

conn.close()

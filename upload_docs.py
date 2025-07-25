#!/usr/bin/env python3
"""
Upload sample documents to the knowledge base
"""

import requests
import os

def upload_document(file_path, topic):
    """Upload a document to the knowledge base"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            data = {'topic': topic}
            
            response = requests.post(
                'http://localhost:8000/api/v1/upload',
                files=files,
                data=data
            )
            
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully uploaded {file_path} to {topic}: {result}")
            return True
        else:
            print(f"❌ Failed to upload {file_path}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {e}")
        return False

def main():
    print("📚 Uploading Sample Documents")
    print("=" * 30)
    
    # Upload documents
    documents = [
        ("calculus_basics.txt", "Mathematics"),
        ("biology_basics.txt", "Biology")
    ]
    
    for file_path, topic in documents:
        if os.path.exists(file_path):
            print(f"\n📄 Uploading {file_path} to {topic}...")
            upload_document(file_path, topic)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎉 Upload complete!")
    print("\n🚀 Now you can ask questions like:")
    print("   - 'What is a derivative in calculus?'")
    print("   - 'Explain photosynthesis'")
    print("   - 'What are the applications of integrals?'")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script to verify Hugging Face API key
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('HUGGINGFACE_API_KEY')
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

# Test API key with a simple request
headers = {
    "Authorization": f"Bearer {api_key}",
}

try:
    # Test the API key by making a request to the API info endpoint
    response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)
    print(f"API Key test response: {response.status_code}")
    if response.status_code == 200:
        print("✓ API Key is valid")
        data = response.json()
        print(f"  User: {data.get('name', 'Unknown')}")
    else:
        print("✗ API Key might be invalid")
        print(f"  Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error testing API key: {str(e)}")

# Also test direct model access without inference API
print("\nTesting direct model access:")
try:
    url = "https://api-inference.huggingface.co/models/gpt2"
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Direct model access: {response.status_code}")
    if response.status_code != 200:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"Error accessing model: {str(e)}")

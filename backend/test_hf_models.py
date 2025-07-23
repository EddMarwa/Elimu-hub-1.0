#!/usr/bin/env python3
"""
Test script to check available Hugging Face models
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('HUGGINGFACE_API_KEY')

# Test different models
models_to_test = [
    "microsoft/DialoGPT-small",
    "facebook/blenderbot-400M-distill",
    "google/flan-t5-small",
    "distilgpt2",
    "EleutherAI/gpt-neo-125M"
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("Testing Hugging Face models...")
print(f"API Key configured: {'Yes' if api_key else 'No'}")
print("-" * 50)

for model in models_to_test:
    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            print(f"✓ {model}: WORKING")
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                print(f"  Response: {result[0].get('generated_text', '')[:100]}...")
            break
        else:
            print(f"✗ {model}: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ {model}: {str(e)}")

print("-" * 50)

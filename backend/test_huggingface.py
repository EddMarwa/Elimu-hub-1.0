#!/usr/bin/env python3
"""
Test script to verify Hugging Face integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from services.llm_service import LLMService
    
    print("✓ Successfully imported LLMService")
    
    # Test LLM service initialization
    provider = os.getenv('LLM_PROVIDER', 'huggingface')
    model = os.getenv('LLM_MODEL', 'HuggingFaceH4/zephyr-7b-alpha')
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    print(f"Provider: {provider}")
    print(f"Model: {model}")  
    print(f"API Key configured: {'Yes' if api_key else 'No'}")
    
    # Initialize LLM service
    llm_service = LLMService(model=model, provider=provider)
    print("✓ LLMService initialized successfully")
    
    # Test a simple LLM call
    print("\nTesting LLM call...")
    prompt = "Hello! Can you tell me what you are?"
    
    try:
        response = llm_service.call_llm(prompt)
        print(f"✓ LLM Response: {response}")
    except Exception as e:
        print(f"✗ LLM Error: {str(e)}")
        
except ImportError as e:
    print(f"✗ Import Error: {str(e)}")
except Exception as e:
    print(f"✗ General Error: {str(e)}")

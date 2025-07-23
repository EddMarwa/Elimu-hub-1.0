#!/usr/bin/env python3
"""
Test script to verify Groq integration
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
    provider = os.getenv('LLM_PROVIDER', 'groq')
    model = os.getenv('LLM_MODEL', 'llama3-8b-8192')
    api_key = os.getenv('GROQ_API_KEY')
    
    print(f"Provider: {provider}")
    print(f"Model: {model}")  
    print(f"API Key configured: {'Yes' if api_key else 'No'}")
    print(f"API Key: {api_key[:20]}..." if api_key else "No API key found")
    
    # Initialize LLM service
    llm_service = LLMService(model=model, provider=provider)
    print("✓ LLMService initialized successfully")
    
    # Test a simple LLM call
    print("\nTesting LLM call...")
    prompt = "What is 2+2? Answer briefly."
    
    try:
        response = llm_service.call_llm(prompt)
        print(f"✓ LLM Response: {response}")
    except Exception as e:
        print(f"✗ LLM Error: {str(e)}")
        
except ImportError as e:
    print(f"✗ Import Error: {str(e)}")
except Exception as e:
    print(f"✗ General Error: {str(e)}")

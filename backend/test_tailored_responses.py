"""
Test Script for Tailored LLM Responses
Demonstrates the enhanced response customization features
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_basic_response_options():
    """Test getting available response options"""
    print("=== Testing Response Options ===")
    
    response = requests.get(f"{BASE_URL}/chat/response-options")
    if response.status_code == 200:
        options = response.json()
        print("Available Options:")
        print(f"- Tones: {', '.join(options['tones'])}")
        print(f"- Formats: {', '.join(options['formats'])}")
        print(f"- Audience Levels: {', '.join(options['audience_levels'])}")
        print(f"- Quick Response Types: {', '.join(options['quick_response_types'])}")
        print()
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_tailored_responses():
    """Test different tailored response styles for the same question"""
    print("=== Testing Tailored Responses ===")
    
    question = "Explain the water cycle"
    topic = "Science"
    
    # Test different configurations
    configs = [
        {
            "name": "Elementary Student",
            "tone": "encouraging",
            "format_type": "explanation",
            "audience_level": "elementary",
            "custom_instructions": "Use simple words and fun examples that children can relate to"
        },
        {
            "name": "High School Academic", 
            "tone": "academic",
            "format_type": "numbered_list",
            "audience_level": "high_school",
            "custom_instructions": "Include scientific terminology and processes"
        },
        {
            "name": "Professional Summary",
            "tone": "professional",
            "format_type": "summary",
            "audience_level": "adult",
            "custom_instructions": "Provide a concise overview suitable for teachers"
        },
        {
            "name": "Step-by-Step Guide",
            "tone": "friendly",
            "format_type": "step_by_step",
            "audience_level": "middle_school",
            "custom_instructions": "Break down each stage of the water cycle clearly"
        }
    ]
    
    for config in configs:
        print(f"\n--- {config['name']} ---")
        
        payload = {
            "question": question,
            "topic": topic,
            **{k: v for k, v in config.items() if k != "name"}
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/chat/tailored", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response ({end_time - start_time:.2f}s):")
            print(data["answer"][:300] + ("..." if len(data["answer"]) > 300 else ""))
            print(f"Config: {data['response_config']['tone']} tone, {data['response_config']['format']} format, {data['response_config']['audience_level']} level")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        print()

def test_quick_responses():
    """Test quick response presets"""
    print("=== Testing Quick Responses ===")
    
    question = "How do I solve quadratic equations?"
    subject = "Mathematics"
    
    quick_types = [
        {"type": "student_tutor", "grade_level": "high_school"},
        {"type": "professional_summary", "grade_level": None},
        {"type": "step_by_step", "grade_level": None}
    ]
    
    for config in quick_types:
        print(f"\n--- {config['type'].replace('_', ' ').title()} ---")
        
        payload = {
            "question": question,
            "subject": subject,
            "response_type": config["type"]
        }
        if config["grade_level"]:
            payload["grade_level"] = config["grade_level"]
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/chat/quick", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response ({end_time - start_time:.2f}s):")
            print(data["answer"][:300] + ("..." if len(data["answer"]) > 300 else ""))
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        print()

def test_response_examples():
    """Test the examples endpoint"""
    print("=== Testing Response Examples ===")
    
    response = requests.post(f"{BASE_URL}/chat/examples")
    if response.status_code == 200:
        data = response.json()
        print(f"Question: {data['question']}")
        print(f"Subject: {data['subject']}")
        print()
        
        print("Different Tones:")
        for tone, example in data['examples']['tones'].items():
            print(f"  {tone.title()}: {example}")
        print()
        
        print("Different Formats:")
        for fmt, example in data['examples']['formats'].items():
            print(f"  {fmt.replace('_', ' ').title()}: {example}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced LLM Response Tailoring")
    print("=" * 50)
    
    try:
        test_basic_response_options()
        test_tailored_responses()
        test_quick_responses()
        test_response_examples()
        
        print("\n✅ All tests completed!")
        print("\nThe LLM can now provide:")
        print("- Multiple tone options (professional, friendly, academic, etc.)")
        print("- Various formats (paragraphs, bullet points, step-by-step, etc.)")
        print("- Different audience levels (elementary to expert)")
        print("- Custom instructions and personas")
        print("- Quick preset response types")
        print("- Context-aware responses with document integration")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error running tests: {e}")

if __name__ == "__main__":
    main()

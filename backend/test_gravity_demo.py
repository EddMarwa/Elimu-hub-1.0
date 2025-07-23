import requests
import json

# Test different response configurations
def test_gravity_explanations():
    base_url = "http://localhost:8000/api/v1/chat/tailored"
    question = "How does gravity work?"
    topic = "Science"
    
    # Test configurations
    configs = [
        {
            "name": "Elementary Kid",
            "request": {
                "question": question,
                "topic": topic,
                "tone": "friendly",
                "format_type": "step_by_step",
                "audience_level": "elementary",
                "custom_instructions": "Use simple analogies that children can understand, like comparing gravity to magnets"
            }
        },
        {
            "name": "High School Student",
            "request": {
                "question": question,
                "topic": topic,
                "tone": "academic",
                "format_type": "explanation",
                "audience_level": "high_school",
                "custom_instructions": "Include basic physics concepts and Newton's law of universal gravitation"
            }
        },
        {
            "name": "Adult Learner",
            "request": {
                "question": question,
                "topic": topic,
                "tone": "professional",
                "format_type": "summary",
                "audience_level": "adult",
                "custom_instructions": "Provide a concise but comprehensive overview suitable for general knowledge"
            }
        }
    ]
    
    print("🌍 Testing Gravity Explanations with Different Audiences")
    print("=" * 60)
    
    for config in configs:
        print(f"\n📚 {config['name']} Response:")
        print("-" * 40)
        
        try:
            response = requests.post(base_url, json=config['request'], timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"⚡ Model: {data['llm_model']}")
                print(f"⏱️ Processing Time: {data['processing_time']:.2f}s")
                print(f"🎯 Config: {data['response_config']['tone']} tone, {data['response_config']['audience_level']} level")
                print(f"📝 Response:\n{data['answer']}")
                
                if data['sources']:
                    print(f"📖 Sources: {', '.join(data['sources'])}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_gravity_explanations()

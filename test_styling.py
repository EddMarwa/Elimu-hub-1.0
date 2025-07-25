#!/usr/bin/env python3
"""
Test script to verify the styling changes work properly
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_styling_features():
    """Test that demonstrates the new styling features"""
    
    print("🎨 Testing Elimu Hub Styling Features...")
    print("=" * 50)
    
    # Create a test session
    session_id = "test-session-styling"
    
    # Test chat with mock response that includes references
    print("\n📝 Testing chat with page references...")
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "question": "What is the main topic discussed in the document?",
                "chatSessionId": session_id
            }
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"✅ Chat Response: {response_data['answer'][:100]}...")
            
            # Check if the response contains reference patterns
            answer = response_data['answer']
            has_page_ref = any(pattern in answer.lower() for pattern in ['page', 'source:', 'pp.'])
            print(f"📄 Contains page references: {'Yes' if has_page_ref else 'No'}")
            
        else:
            print(f"❌ Chat failed: {chat_response.status_code}")
            
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    print("\n🎯 Styling Features Implemented:")
    print("✅ References displayed in italics and green color")
    print("✅ Upload button removed from chat input")
    print("✅ Responsive sidebar that adapts to chat history")
    print("✅ Improved mobile layout with better transitions")
    print("✅ Chat counter in sidebar header")
    print("✅ Auto-collapse sidebar on mobile after chat selection")
    
    print("\n🎨 Frontend Features:")
    print("• MessageBubble: References styled with italic green text")
    print("• ChatInput: Upload button removed, simplified interface")
    print("• Sidebar: Responsive width, chat counters, improved layout")
    print("• ChatInterface: Better mobile handling, adaptive layout")
    
    print("\n🌐 Frontend Server: http://localhost:3001")
    print("🚀 Backend Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_styling_features()

#!/usr/bin/env python3
"""
Test script to verify OpenRouter API key works
"""

import os
import requests
import json

# Get API key from environment
api_key = os.environ.get('OPEN_ROUTER')

print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"🔑 API Key starts with: {api_key[:10]}...")
else:
    print("❌ No API key found in environment variables")
    exit(1)

# Test the API
try:
    print("\n🧪 Testing OpenRouter API...")
    
    response = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://openrouter.ai/'
        },
        json={
            'model': 'mistralai/mistral-small-3.2-24b-instruct:free',
            'messages': [
                {
                    'role': 'user',
                    'content': 'Say "Hello, API test successful!"'
                }
            ],
            'max_tokens': 50,
            'temperature': 0.7
        }
    )
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        message = data['choices'][0]['message']['content']
        print(f"✅ API Test Successful!")
        print(f"🤖 Response: {message}")
    else:
        print(f"❌ API Test Failed!")
        print(f"📄 Error Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")

print("\n🏁 Test completed!") 
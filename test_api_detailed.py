#!/usr/bin/env python3
"""
Detailed test script to debug OpenRouter API key issues
"""

import os
import requests
import json

# Get API key from environment
api_key = os.environ.get('OPEN_ROUTER')

print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"🔑 API Key length: {len(api_key)} characters")
    print(f"🔑 API Key starts with: {api_key[:10]}...")
    print(f"🔑 API Key ends with: ...{api_key[-10:]}")
else:
    print("❌ No API key found in environment variables")
    exit(1)

# Test different models
models_to_test = [
    'mistralai/mistral-small-3.2-24b-instruct:free',
    'openai/gpt-3.5-turbo',
    'anthropic/claude-3-haiku',
    'meta-llama/llama-3.1-8b-instruct:free'
]

for model in models_to_test:
    print(f"\n🧪 Testing model: {model}")
    
    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://openrouter.ai/'
            },
            json={
                'model': model,
                'messages': [
                    {
                        'role': 'user',
                        'content': 'Say "Hello, API test successful!"'
                    }
                ],
                'max_tokens': 50,
                'temperature': 0.7
            },
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content']
            print(f"✅ Success with {model}!")
            print(f"🤖 Response: {message}")
            break
        else:
            print(f"❌ Failed with {model}")
            print(f"📄 Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing {model}: {e}")

print("\n🏁 All tests completed!")

# Test API key format
print(f"\n🔍 API Key Analysis:")
print(f"   - Contains 'sk-or-v1': {'sk-or-v1' in api_key}")
print(f"   - Length is reasonable: {50 <= len(api_key) <= 100}")
print(f"   - No spaces: {' ' not in api_key}")
print(f"   - No newlines: {'\\n' not in api_key}") 
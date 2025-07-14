#!/usr/bin/env python3
"""
Test script for Google Gemini API integration
"""

import requests
import json

# Your Gemini API key
GEMINI_API_KEY = "AIzaSyCR2qkH4DXw4jBXbT94YnAOgwaSD6r-rBI"

def list_available_models():
    """List available Gemini models"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        
        print("Listing available models...")
        response = requests.get(url)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Available models:")
            for model in data.get('models', []):
                print(f"  - {model['name']}")
            return data.get('models', [])
        else:
            print(f"❌ Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def test_gemini_api():
    """Test the Gemini API with a simple prompt"""
    try:
        # Try different model names
        models_to_try = [
            "gemini-1.5-pro",
            "gemini-1.5-flash", 
            "gemini-pro",
            "gemini-1.0-pro"
        ]
        
        for model_name in models_to_try:
            print(f"\nTrying model: {model_name}")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Create a short LinkedIn post about technology trends. Keep it under 100 words."}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 200
                }
            }
            
            response = requests.post(url, json=payload)
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'candidates' in data and len(data['candidates']) > 0:
                    generated_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    print(f"✅ SUCCESS with model {model_name}!")
                    print(f"Generated text:\n{generated_text}")
                    return model_name, True
                else:
                    print(f"❌ No candidates in response for {model_name}")
            else:
                print(f"❌ Error with {model_name}: {response.text}")
        
        return None, False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, False

if __name__ == "__main__":
    print("🔍 Checking available models...")
    models = list_available_models()
    
    print("\n🧪 Testing API calls...")
    working_model, success = test_gemini_api()
    
    if success:
        print(f"\n🎉 Gemini API test successful with model: {working_model}")
        print(f"Use this model in your server.py: {working_model}")
    else:
        print("\n💥 Gemini API test failed!") 
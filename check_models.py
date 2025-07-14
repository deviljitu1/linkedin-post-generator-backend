import requests
import json

def check_available_models():
    """Check available models on OpenRouter and find free ones"""
    api_key = "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"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            
            print("🤖 Available Models on OpenRouter:")
            print("=" * 50)
            
            free_models = []
            
            for model in models.get('data', []):
                model_id = model.get('id', '')
                pricing = model.get('pricing', {})
                prompt_price = pricing.get('prompt', '0')
                completion_price = pricing.get('completion', '0')
                
                # Check if it's free (both prompt and completion are 0 or very low)
                is_free = (prompt_price == '0' or float(prompt_price) == 0) and (completion_price == '0' or float(completion_price) == 0)
                
                if is_free:
                    free_models.append(model_id)
                    print(f"✅ FREE: {model_id}")
                else:
                    print(f"💰 PAID: {model_id} (prompt: ${prompt_price}/1K, completion: ${completion_price}/1K)")
            
            print(f"\n🎉 Found {len(free_models)} free models!")
            
            if free_models:
                print("\nRecommended free models for LinkedIn posts:")
                for model in free_models[:5]:  # Show first 5
                    print(f"  - {model}")
                
                return free_models[0] if free_models else None
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return None

if __name__ == "__main__":
    best_free_model = check_available_models()
    if best_free_model:
        print(f"\n🚀 Recommended model to use: {best_free_model}")
    else:
        print("\n❌ No free models found or error occurred") 
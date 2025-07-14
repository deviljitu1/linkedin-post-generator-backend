import requests
import json
import random

class SimpleAIGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai/"
        }

    def generate_linkedin_post(self, topic=None, industry=None, tone="professional"):
        """Generate a LinkedIn post using AI"""
        if not topic:
            topics = [
                "latest project completion",
                "industry insights and tips", 
                "professional achievement",
                "client success story",
                "technology trends",
                "business growth strategies",
                "team collaboration",
                "innovation in the field"
            ]
            topic = random.choice(topics)
        
        if not industry:
            industry = "technology and digital marketing"

        prompt = f"""Create a compelling LinkedIn post about {topic} in the {industry} industry.

Requirements:
- Tone: {tone}
- Length: 2-4 sentences
- Include emojis for engagement
- Make it professional yet engaging
- End with a question to encourage interaction
- Include 3-5 relevant hashtags

Generate the post:"""

        try:
            print(f"[DEBUG] Authorization header: Bearer {OPENROUTER_API_KEY}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                    "messages": [
                        {"role": "system", "content": "You are a professional LinkedIn content creator. Create engaging, authentic posts that drive engagement and provide value to the audience."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return self._get_fallback_post(topic, industry, tone)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._get_fallback_post(topic, industry, tone)

    def _get_fallback_post(self, topic, industry, tone):
        """Fallback post if AI fails"""
        fallback_posts = [
            f"🚀 Excited to share insights about {topic} in the {industry} space! The journey of continuous learning and growth never stops. What's your experience with this?\n\n#{industry.replace(' ', '')} #{topic.replace(' ', '')} #ProfessionalGrowth #Innovation",
            f"💡 Just completed an amazing {topic} project! The {industry} industry is evolving rapidly, and staying ahead requires constant innovation. How do you stay updated?\n\n#{industry.replace(' ', '')} #{topic.replace(' ', '')} #ProfessionalGrowth #Innovation",
            f"🎯 Another milestone achieved in {topic}! The {industry} landscape is full of opportunities for those willing to adapt and grow. What challenges are you facing?\n\n#{industry.replace(' ', '')} #{topic.replace(' ', '')} #ProfessionalGrowth #Innovation"
        ]
        return random.choice(fallback_posts)

def main():
    print("🤖 LinkedIn AI Post Generator")
    print("=" * 40)
    print("This tool generates LinkedIn posts for you to copy and paste manually.")
    print()
    
    # Your OpenRouter API key
    api_key = "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"
    
    generator = SimpleAIGenerator(api_key)
    
    print(f"OPEN_ROUTER from environment: {OPENROUTER_API_KEY}")
    
    while True:
        print("\n📝 Generate a LinkedIn Post")
        print("-" * 30)
        
        # Get user input
        topic = input("Enter topic (or press Enter for random): ").strip()
        if not topic:
            topic = None
            
        industry = input("Enter industry (or press Enter for 'technology'): ").strip()
        if not industry:
            industry = "technology"
            
        tone = input("Enter tone (professional/casual/enthusiastic/educational) [default: professional]: ").strip()
        if not tone:
            tone = "professional"
        
        print("\n🤖 Generating post...")
        post = generator.generate_linkedin_post(topic, industry, tone)
        
        print("\n✅ Generated LinkedIn Post:")
        print("=" * 50)
        print(post)
        print("=" * 50)
        
        # Copy to clipboard option
        try:
            import pyperclip
            pyperclip.copy(post)
            print("\n📋 Post copied to clipboard! You can now paste it on LinkedIn.")
        except ImportError:
            print("\n📋 Copy the post above and paste it on LinkedIn.")
        
        # Ask if user wants to generate another
        another = input("\nGenerate another post? (y/n): ").strip().lower()
        if another != 'y':
            break
    
    print("\n🎉 Thanks for using LinkedIn AI Post Generator!")

if __name__ == "__main__":
    main() 
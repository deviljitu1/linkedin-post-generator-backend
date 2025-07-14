import requests
import os
import random

class AIContentGenerator:
    def __init__(self, openrouter_api_key):
        """
        Initialize AI Content Generator with OpenRouter.ai API key
        """
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai/"
        }

    def generate_post_text(self, topic=None, industry=None, tone="professional", include_hashtags=True):
        """
        Generate LinkedIn post text using OpenRouter.ai
        """
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
{('- Include 3-5 relevant hashtags' if include_hashtags else '')}

Example format:
🚀 [Engaging opening about the topic]

[2-3 sentences with insights, achievements, or tips]

[Question to engage audience]

{('#Hashtag1 #Hashtag2 #Hashtag3' if include_hashtags else '')}

Generate the post:"""
        try:
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
                generated_text = result['choices'][0]['message']['content'].strip()
                return generated_text
            else:
                print(f"❌ Error generating text: {response.status_code} - {response.text}")
                return self._get_fallback_text(topic, industry, tone, include_hashtags)
        except Exception as e:
            print(f"❌ Error in text generation: {e}")
            return self._get_fallback_text(topic, industry, tone, include_hashtags)

    def generate_complete_post(self, topic=None, industry=None, tone="professional", **kwargs):
        """
        Generate a complete LinkedIn post with text only (no image)
        Returns: dict: {"text": "generated text", "image_path": None}
        """
        print("🤖 Generating AI content (OpenRouter.ai)...")
        text = self.generate_post_text(topic, industry, tone)
        return {"text": text, "image_path": None}

    def _get_fallback_text(self, topic, industry, tone, include_hashtags):
        fallback_texts = [
            f"🚀 Excited to share insights about {topic} in the {industry} space! The journey of continuous learning and growth never stops. What's your experience with this?",
            f"💡 Just completed an amazing {topic} project! The {industry} industry is evolving rapidly, and staying ahead requires constant innovation. How do you stay updated?",
            f"🎯 Another milestone achieved in {topic}! The {industry} landscape is full of opportunities for those willing to adapt and grow. What challenges are you facing?",
            f"✨ Reflecting on the latest developments in {topic}. The {industry} sector continues to surprise and inspire. What trends are you most excited about?"
        ]
        text = random.choice(fallback_texts)
        if include_hashtags:
            hashtags = f"#{industry.replace(' ', '')} #{topic.replace(' ', '')} #ProfessionalGrowth #Innovation"
            text += f"\n\n{hashtags}"
        return text

def main():
    print("🤖 AI Content Generator Test (OpenRouter.ai)")
    print("=" * 40)
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("Please set your OpenRouter.ai API key:")
        print("export OPENROUTER_API_KEY='your-api-key-here'")
        return
    generator = AIContentGenerator(api_key)
    print("\n📝 Testing text generation...")
    text = generator.generate_post_text(
        topic="web development project",
        industry="technology",
        tone="professional"
    )
    print(f"Generated text:\n{text}")
    print("\n📦 Testing complete post generation...")
    post = generator.generate_complete_post(
        topic="digital marketing success",
        industry="marketing",
        tone="enthusiastic"
    )
    print(f"Complete post:\n{post}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import json
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import urllib.request
from bs4 import BeautifulSoup

# Configuration
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get('PORT', 8000))
HOST = os.environ.get('HOST', '0.0.0.0')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY environment variable not set!")
    exit(1)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/generate-post':
            self.handle_generate_post()
        else:
            self.send_error(404)

    def ensure_hashtags_and_emojis(self, post, topic=None, industry=None):
        import re
        emoji_map = {
            'technology': ['💻', '🤖', '🚀', '📱'],
            'marketing': ['📈', '💡', '📣', '🚀'],
            'business': ['💼', '📊', '🏢', '🚀'],
            'education': ['🎓', '📚', '🧑‍🏫', '💡'],
            'healthcare': ['🩺', '💊', '🏥', '💡'],
            'finance': ['💰', '📈', '💹', '🏦'],
            'startup': ['🚀', '💡', '🌱', '🔥'],
            'consulting': ['💼', '🧑‍💼', '📊', '💡'],
            'others': ['🌟', '✨', '🔥', '💡']
        }
        hashtag_map = {
            'technology': ['#Tech', '#Innovation', '#AI', '#DigitalTransformation'],
            'marketing': ['#Marketing', '#Branding', '#Growth', '#DigitalMarketing'],
            'business': ['#Business', '#Leadership', '#Strategy', '#Entrepreneurship'],
            'education': ['#Education', '#Learning', '#EdTech', '#GrowthMindset'],
            'healthcare': ['#Healthcare', '#Wellness', '#MedTech', '#HealthInnovation'],
            'finance': ['#Finance', '#Investing', '#FinTech', '#MoneyMatters'],
            'startup': ['#Startup', '#Entrepreneur', '#Innovation', '#Growth'],
            'consulting': ['#Consulting', '#Strategy', '#BusinessGrowth', '#Leadership'],
            'others': ['#Success', '#Motivation', '#Inspiration', '#Career']
        }
        emoji_pattern = re.compile('[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+', flags=re.UNICODE)
        emojis_found = emoji_pattern.findall(post)
        hashtags_found = re.findall(r'#\w+', post)
        context = (industry or topic or 'others').lower()
        context = context if context in emoji_map else 'others'
        # Add emojis if less than 2
        if len(emojis_found) < 2:
            needed = 2 - len(emojis_found)
            extra_emojis = emoji_map[context][:needed]
            post = post.strip() + ' ' + ' '.join(extra_emojis)
        # Add hashtags if less than 3, always on a new line
        if len(hashtags_found) < 3:
            needed = 3 - len(hashtags_found)
            extra_hashtags = hashtag_map[context][:needed]
            post = post.rstrip() + '\n' + ' '.join(extra_hashtags)
        return post.strip()

    def handle_generate_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if not GEMINI_API_KEY:
                self.send_error(500, "Gemini API key not configured")
                return

            model = data.get('model', 'gemini').lower()

            if data.get('type') == 'article':
                post = self.generate_post_from_article(data['url'], data['industry'], data['tone'], model)
            else:
                post = self.generate_post_from_topic(data['topic'], data['industry'], data['tone'], model)

            post = self.ensure_hashtags_and_emojis(post, data.get('topic'), data.get('industry'))

            response = {
                'post': post,
                'title': f"🚀 {data.get('topic', 'LinkedIn Growth Strategy')[:60]} – Key Takeaway for {data.get('industry', 'Professionals')}"
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"Error generating post: {e}")
            self.send_error(500, str(e))

    def call_gemini_api(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 400
                }
            }
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                raise Exception("No response from Gemini API")
        except Exception as e:
            raise e

    def call_openrouter_api(self, prompt):
        if not OPENROUTER_API_KEY:
            raise Exception("OpenRouter API key not configured")
        url = "https://openrouter.ai/api/v1/generate"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()
        else:
            raise Exception("No response from OpenRouter API")

    def generate_post_from_topic(self, topic, industry, tone, model='gemini'):
        prompt = self.create_topic_prompt(topic, industry, tone)
        try:
            if model == 'openrouter':
                return self.call_openrouter_api(prompt)
            return self.call_gemini_api(prompt)
        except Exception as e:
            print(f"Primary model failed, trying fallback: {e}")
            if model == 'openrouter':
                return self.call_gemini_api(prompt)
            return self.call_openrouter_api(prompt)

    def generate_post_from_article(self, url, industry, tone, model='gemini'):
        try:
            try:
                article_data = self.extract_article_content(url)
                prompt = self.create_article_prompt(article_data, industry, tone)
            except Exception as extraction_error:
                prompt = f"Summarize the article at this URL for a LinkedIn post: {url}\nIndustry: {industry}\nTone: {tone}\nInclude emojis, a call-to-action, and at least 3 relevant hashtags."
            try:
                if model == 'openrouter':
                    return self.call_openrouter_api(prompt)
                return self.call_gemini_api(prompt)
            except Exception as e:
                print(f"Primary model failed, trying fallback: {e}")
                if model == 'openrouter':
                    return self.call_gemini_api(prompt)
                return self.call_openrouter_api(prompt)
        except Exception as e:
            raise e

    def extract_article_content(self, url):
        try:
            import newspaper
            article = newspaper.Article(url)
            article.download()
            article.parse()
            content = article.text.strip()
            title = article.title.strip() if article.title else 'Article'
            return {
                'title': title,
                'content': content[:2000],
                'url': url
            }
        except Exception as e:
            raise Exception('Failed to extract article content.')

    def get_tone_instruction(self, tone):
        tone_map = {
            'professional': 'Maintain a formal, knowledgeable, and trustworthy voice.',
            'casual': 'Keep it light, friendly, and conversational.',
            'enthusiastic': 'Use high energy, exclamation, and positive words.',
            'educational': 'Break concepts down clearly, like teaching someone new.',
            'inspirational': 'Uplift the audience with stories or visionary insights.'
        }
        return tone_map.get(tone.lower(), f"Use a {tone} tone.")

    def create_topic_prompt(self, topic, industry, tone):
        topic = topic or 'latest industry trend'
        industry = industry or 'technology'
        tone_instruction = self.get_tone_instruction(tone)

        return f"""You are a LinkedIn content strategist. Write a compelling post about "{topic}" in the "{industry}" industry.

Instructions:
- {tone_instruction}
- Start with a hook (statistic, bold opinion, question)
- Include personal or industry perspective
- Add emojis to boost engagement
- End with a strong CTA or open question
- **MANDATORY**: Add 3-5 relevant and trending hashtags at the end

Now write the post:"""

    def create_article_prompt(self, article_data, industry, tone):
        tone_instruction = self.get_tone_instruction(tone)
        return f'''Summarize the following article into a scroll-stopping, SEO-friendly LinkedIn post.

Title: {article_data['title']}
Industry: {industry}
Tone: {tone_instruction}

Article content:
{article_data['content'][:1500]}

Post requirements:
- Open with a striking insight, quote, or statistic
- Summarize key points clearly
- Add a unique personal or industry insight
- Include emojis for tone
- End with a question or CTA
- **MANDATORY**: Add 3-5 relevant and trending hashtags at the end

Now write the LinkedIn post:'''

def main():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 LinkedIn AI Post Generator Server Running at http://{HOST}:{PORT}")
        if not os.environ.get('RAILWAY_ENVIRONMENT'):
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("✅ Browser opened automatically")
            except:
                print("⚠️  Open the browser manually.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

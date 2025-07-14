#!/usr/bin/env python3
"""
Optimized HTTP server for LinkedIn AI Post Generator using Google Gemini API
Enhanced for SEO, hooks, emotional engagement, and fallback support.
"""

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
    
    def handle_generate_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if not GEMINI_API_KEY:
                self.send_error(500, "Gemini API key not configured")
                return
            
            if data.get('type') == 'article':
                post = self.generate_post_from_article(data['url'], data['industry'], data['tone'])
            else:
                post = self.generate_post_from_topic(data['topic'], data['industry'], data['tone'])

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
            print(f"Error calling Gemini API: {e}")
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

    def generate_post_from_topic(self, topic, industry, tone):
        prompt = self.create_topic_prompt(topic, industry, tone)
        try:
            return self.call_gemini_api(prompt)
        except Exception as e:
            print(f"Gemini failed, trying OpenRouter: {e}")
            return self.call_openrouter_api(prompt)

    def generate_post_from_article(self, url, industry, tone):
        try:
            try:
                article_data = self.extract_article_content(url)
                prompt = self.create_article_prompt(article_data, industry, tone)
            except Exception as extraction_error:
                print(f"Article extraction failed: {extraction_error}")
                prompt = f"Summarize the main points of this article for LinkedIn: {url}\nIndustry: {industry}\nTone: {tone}"
            try:
                return self.call_gemini_api(prompt)
            except Exception as e:
                print(f"Gemini failed, trying OpenRouter: {e}")
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
            print(f"Error extracting article: {e}")
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

        return f"""You are a LinkedIn content strategist. Create a compelling, SEO-friendly LinkedIn post about "{topic}" in the "{industry}" industry.

Requirements:
- {tone_instruction}
- Start with a bold hook (stat, quote, opinion)
- Add personal insight or storytelling
- Use emojis smartly for engagement
- End with a question or CTA
- Include 3-5 trending, industry-relevant hashtags

Example:
🚀 “Most businesses still ignore this one growth channel…”

[Share the insight or story]

What’s your take on this?

#Growth #Marketing #Leadership #Career #LinkedInTips

Now write the post:"""

    def create_article_prompt(self, article_data, industry, tone):
        tone_instruction = self.get_tone_instruction(tone)
        return f"""You are a LinkedIn strategist. Summarize this article into a compelling, SEO-optimized LinkedIn post.

Title: {article_data['title']}
URL: {article_data['url']}
Industry: {industry}
Tone: {tone_instruction}

Content:
{article_data['content'][:1500]}

Post requirements:
- Catchy opening
- 2-3 sentence summary
- Add a unique insight or comment
- End with a CTA or thought-provoking question
- Mention article title or URL
- Add 3-5 trending hashtags
- Include emojis where appropriate

Now write the post:"""

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

#!/usr/bin/env python3
"""
Simple HTTP server for LinkedIn AI Post Generator using Google Gemini API
Run this script to serve the web interface locally
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
PORT = int(os.environ.get('PORT', 8000))  # Railway sets PORT environment variable
HOST = os.environ.get('HOST', '0.0.0.0')  # Railway uses 0.0.0.0
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# Check if API key is set
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY environment variable not set!")
    print("Please set your Gemini API key as an environment variable in Render.")
    exit(1)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for web API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/generate-post':
            self.handle_generate_post()
        else:
            self.send_error(404)
    
    def handle_generate_post(self):
        """Handle POST requests to generate LinkedIn posts"""
        try:
            # Get request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Check if we have an API key
            if not GEMINI_API_KEY:
                self.send_error(500, "Gemini API key not configured")
                return
            
            # Generate post based on type
            if data.get('type') == 'article':
                post = self.generate_post_from_article(data['url'], data['industry'], data['tone'])
            else:
                post = self.generate_post_from_topic(data['topic'], data['industry'], data['tone'])
            
            # Send response
            response = {'post': post}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error generating post: {e}")
            self.send_error(500, str(e))
    
    def call_gemini_api(self, prompt):
        """Call Google Gemini API with the given prompt"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 400
                }
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                print(f"Gemini API error: {response.text}")
                raise Exception(f"Gemini API error: {response.status_code}")
            
            data = response.json()
            
            # Extract the generated text from Gemini response
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                raise Exception("No response generated from Gemini API")
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise e
    
    def call_openrouter_api(self, prompt):
        """Call OpenRouter API with the given prompt as a fallback"""
        if not OPENROUTER_API_KEY:
            raise Exception("OpenRouter API key not configured")
        url = "https://openrouter.ai/api/v1/generate"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        data = response.json()
        # Extract the generated text from OpenRouter response
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()
        else:
            raise Exception("No response generated from OpenRouter API")

    def generate_post_from_topic(self, topic, industry, tone):
        """Generate LinkedIn post from topic using Gemini, fallback to OpenRouter"""
        prompt = self.create_topic_prompt(topic, industry, tone)
        try:
            return self.call_gemini_api(prompt)
        except Exception as e:
            print(f"Gemini API failed, trying OpenRouter: {e}")
            return self.call_openrouter_api(prompt)

    def generate_post_from_article(self, url, industry, tone):
        """Generate LinkedIn post from article URL using Gemini, fallback to OpenRouter. If extraction fails, try summarizing the URL directly."""
        try:
            try:
                article_data = self.extract_article_content(url)
                prompt = self.create_article_prompt(article_data, industry, tone)
            except Exception as extraction_error:
                print(f"Article extraction failed: {extraction_error}. Trying to summarize URL directly.")
                # Fallback prompt for summarizing the URL directly
                prompt = f"Summarize the main points of the article at this URL for a LinkedIn post.\nURL: {url}\nIndustry: {industry}\nTone: {tone}\nInclude emojis, hashtags, and end with a question."
            try:
                return self.call_gemini_api(prompt)
            except Exception as e:
                print(f"Gemini API failed, trying OpenRouter: {e}")
                return self.call_openrouter_api(prompt)
        except Exception as e:
            print(f"Error generating post from article: {e}")
            raise e
    
    def extract_article_content(self, url):
        """Extract content from article URL using newspaper3k"""
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
            print(f"Error extracting article content with newspaper3k: {e}")
            raise Exception('Failed to extract article content. Please check the URL and try again.')
    
    def get_tone_instruction(self, tone):
        tone_map = {
            'professional': 'Use formal language, focus on expertise, and maintain a business-like tone.',
            'casual': 'Use friendly, conversational language, and keep the tone relaxed.',
            'enthusiastic': 'Use energetic, positive language, and express excitement.',
            'educational': 'Focus on teaching, use clear explanations, and provide actionable insights.'
        }
        return tone_map.get(tone.lower(), f"Write in a {tone} tone.")

    def create_topic_prompt(self, topic, industry, tone):
        """Create prompt for topic-based post generation with explicit tone instructions"""
        default_topic = topic or 'latest project completion'
        default_industry = industry or 'technology and digital marketing'
        tone_instruction = self.get_tone_instruction(tone)
        return f"""Create a compelling LinkedIn post about {default_topic} in the {default_industry} industry.\n\nRequirements:\n- {tone_instruction}\n- Length: 2-4 sentences\n- Include emojis for engagement\n- Make it professional yet engaging\n- End with a question to encourage interaction\n- Include 3-5 relevant hashtags\n\nExample format:\n🚀 [Engaging opening about the topic]\n\n[2-3 sentences with insights, achievements, or tips]\n\n[Question to engage audience]\n\n#Hashtag1 #Hashtag2 #Hashtag3\n\nGenerate the post:"""

    def create_article_prompt(self, article_data, industry, tone):
        """Create prompt for article summarization with explicit tone instructions"""
        tone_instruction = self.get_tone_instruction(tone)
        return f"""Create a compelling LinkedIn post that summarizes this article:\n\nArticle Title: {article_data['title']}\nArticle URL: {article_data['url']}\nArticle Content: {article_data['content'][:1500]}...\n\nRequirements:\n- {tone_instruction}\n- Industry Context: {industry}\n- Length: 3-5 sentences\n- Include emojis for engagement\n- Summarize key points from the article\n- Add your professional insights\n- End with a question to encourage interaction\n- Include 3-5 relevant hashtags\n- Mention the source article\n\nFormat:\n🚀 [Engaging opening about the article topic]\n\n[2-3 sentences summarizing key insights from the article]\n\n[Your professional take or industry perspective]\n\n[Question to engage audience]\n\n[Source: Article Title]\n\n#Hashtag1 #Hashtag2 #Hashtag3\n\nGenerate the LinkedIn post:"""

def main():
    """Start the HTTP server"""
    
    # Change to the directory containing this script
    os.chdir(DIRECTORY)
    
    # Create server
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 LinkedIn AI Post Generator Server (Gemini)")
        print(f"📁 Serving files from: {DIRECTORY}")
        print(f"🌐 Server running at: http://{HOST}:{PORT}")
        
        # Check if running on Railway
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            print(f"🚂 Deployed on Railway")
            print(f"🔗 Public URL: https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'your-app.railway.app')}")
        else:
            print(f"📱 Open your browser and go to: http://localhost:{PORT}")
            print(f"⏹️  Press Ctrl+C to stop the server")
        
        print("-" * 50)
        
        if GEMINI_API_KEY:
            print("✅ Gemini API key configured")
        else:
            print("⚠️  Gemini API key not found in environment variables")
            print("Set GEMINI_API_KEY variable in Railway dashboard")
        
        # Open browser automatically (only for local development)
        if not os.environ.get('RAILWAY_ENVIRONMENT'):
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("✅ Browser opened automatically!")
            except:
                print("⚠️  Could not open browser automatically. Please open it manually.")
        
        print("\n🎯 Features:")
        print("• Generate LinkedIn posts with Google Gemini AI")
        print("• Article URL summarization")
        print("• Choose topic, industry, and tone")
        print("• Copy posts to clipboard")
        print("• Direct link to LinkedIn")
        print("• Mobile-friendly design")
        print("• Secure API key handling")
        print("-" * 50)
        
        try:
            # Start serving
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 
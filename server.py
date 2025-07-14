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
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCR2qkH4DXw4jBXbT94YnAOgwaSD6r-rBI')

# Check if API key is set
if not GEMINI_API_KEY:
    print("⚠️  Warning: GEMINI_API_KEY environment variable not set!")
    print("Please set your Gemini API key as an environment variable:")
    print("set GEMINI_API_KEY=your-api-key-here")
    print("Or set it in Railway dashboard under Variables section")
    # Don't exit - let Railway handle it

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
    
    def generate_post_from_topic(self, topic, industry, tone):
        """Generate LinkedIn post from topic using Gemini"""
        try:
            prompt = self.create_topic_prompt(topic, industry, tone)
            return self.call_gemini_api(prompt)
        except Exception as e:
            print(f"Error generating post from topic: {e}")
            raise e
    
    def generate_post_from_article(self, url, industry, tone):
        """Generate LinkedIn post from article URL using Gemini"""
        try:
            # Extract article content
            article_data = self.extract_article_content(url)
            
            # Create prompt for article summarization
            prompt = self.create_article_prompt(article_data, industry, tone)
            return self.call_gemini_api(prompt)
            
        except Exception as e:
            print(f"Error generating post from article: {e}")
            raise e
    
    def extract_article_content(self, url):
        """Extract content from article URL"""
        try:
            # Use a CORS proxy to fetch the article content
            proxy_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(url)}"
            response = requests.get(proxy_url)
            data = response.json()
            
            if data.get('contents'):
                # Parse the HTML content
                soup = BeautifulSoup(data['contents'], 'html.parser')
                
                # Extract text content from common article selectors
                selectors = [
                    'article',
                    '[class*="content"]',
                    '[class*="article"]',
                    '[class*="post"]',
                    '.post-content',
                    '.article-content',
                    '.entry-content',
                    'main',
                    '.main-content'
                ]
                
                content = ''
                for selector in selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text().strip()
                        if len(content) > 100:
                            break
                
                # If no specific content found, get body text
                if not content or len(content) < 100:
                    content = soup.body.get_text().strip() if soup.body else ''
                
                # Clean up the content
                content = ' '.join(content.split())[:2000]
                
                return {
                    'title': soup.title.string if soup.title else 'Article',
                    'content': content,
                    'url': url
                }
            
            raise Exception('Could not extract content from URL')
            
        except Exception as e:
            print(f"Error extracting article content: {e}")
            raise Exception('Failed to extract article content. Please check the URL and try again.')
    
    def create_topic_prompt(self, topic, industry, tone):
        """Create prompt for topic-based post generation"""
        default_topic = topic or 'latest project completion'
        default_industry = industry or 'technology and digital marketing'
        
        return f"""Create a compelling LinkedIn post about {default_topic} in the {default_industry} industry.

Requirements:
- Tone: {tone}
- Length: 2-4 sentences
- Include emojis for engagement
- Make it professional yet engaging
- End with a question to encourage interaction
- Include 3-5 relevant hashtags

Example format:
🚀 [Engaging opening about the topic]

[2-3 sentences with insights, achievements, or tips]

[Question to engage audience]

#Hashtag1 #Hashtag2 #Hashtag3

Generate the post:"""
    
    def create_article_prompt(self, article_data, industry, tone):
        """Create prompt for article summarization"""
        return f"""Create a compelling LinkedIn post that summarizes this article:

Article Title: {article_data['title']}
Article URL: {article_data['url']}
Article Content: {article_data['content'][:1500]}...

Requirements:
- Tone: {tone}
- Industry Context: {industry}
- Length: 3-5 sentences
- Include emojis for engagement
- Summarize key points from the article
- Add your professional insights
- End with a question to encourage interaction
- Include 3-5 relevant hashtags
- Mention the source article

Format:
🚀 [Engaging opening about the article topic]

[2-3 sentences summarizing key insights from the article]

[Your professional take or industry perspective]

[Question to engage audience]

[Source: Article Title]

#Hashtag1 #Hashtag2 #Hashtag3

Generate the LinkedIn post:"""

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
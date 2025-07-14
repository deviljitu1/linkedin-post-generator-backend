 import os
import requests
import json
from datetime import datetime
from linkedin_api import Linkedin
import time
from PIL import Image
import io
from ai_content_generator import AIContentGenerator

class LinkedInAutomation:
    def __init__(self, email, password, together_api_key=None):
        """
        Initialize LinkedIn automation with your credentials and optional AI content generation
        """
        self.api = Linkedin(email, password)
        self.user_id = None
        self.ai_generator = None
        
        # Initialize AI generator if API key provided
        if together_api_key:
            self.ai_generator = AIContentGenerator(together_api_key)
        
        self._get_user_id()
    
    def _get_user_id(self):
        """
        Get the current user's LinkedIn ID
        """
        try:
            profile = self.api.get('me')
            self.user_id = profile['id']
            print(f"Successfully authenticated as: {profile.get('firstName', '')} {profile.get('lastName', '')}")
        except Exception as e:
            print(f"Error getting user ID: {e}")
            raise
    
    def generate_and_post(self, topic=None, industry=None, tone="professional", 
                         generate_image=True, image_prompt=None):
        """
        Generate AI content and post to LinkedIn
        """
        if not self.ai_generator:
            print("❌ AI generator not initialized. Please provide Together AI API key.")
            return None
        
        print("🤖 Generating AI content...")
        
        # Generate content using AI
        post_data = self.ai_generator.generate_complete_post(
            topic=topic,
            industry=industry,
            tone=tone,
            generate_image=generate_image,
            image_prompt=image_prompt
        )
        
        if not post_data:
            print("❌ Failed to generate content")
            return None
        
        print(f"✅ Generated text: {post_data['text'][:100]}...")
        if post_data['image_path']:
            print(f"✅ Generated image: {post_data['image_path']}")
        
        # Post the generated content
        if post_data['image_path']:
            return self.post_image_with_text(post_data['text'], post_data['image_path'])
        else:
            return self.post_text(post_data['text'])
    
    def post_text(self, text_content):
        """
        Post text content to LinkedIn
        """
        try:
            # Create the post data
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Make the API call
            response = self.api.post('/ugcPosts', json=post_data)
            
            if response.status_code == 201:
                print("✅ Text post published successfully!")
                return response.json()
            else:
                print(f"❌ Error posting text: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting text content: {e}")
            return None
    
    def post_image_with_text(self, text_content, image_path):
        """
        Post image with text content to LinkedIn
        """
        try:
            # First, upload the image
            print("📤 Uploading image...")
            image_urn = self._upload_image(image_path)
            
            if not image_urn:
                print("❌ Failed to upload image")
                return None
            
            # Create the post data with image
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text_content
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": "AI Generated Image"
                                },
                                "media": image_urn,
                                "title": {
                                    "text": "LinkedIn Post"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Make the API call
            response = self.api.post('/ugcPosts', json=post_data)
            
            if response.status_code == 201:
                print("✅ Image post published successfully!")
                return response.json()
            else:
                print(f"❌ Error posting image: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting image with text: {e}")
            return None
    
    def _upload_image(self, image_path):
        """
        Upload image to LinkedIn and return the URN
        """
        try:
            # Read and prepare the image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Upload the image
            upload_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            upload_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{self.user_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            # Register the upload
            response = self.api.post(upload_url, json=upload_data)
            
            if response.status_code != 200:
                print(f"❌ Error registering upload: {response.status_code}")
                return None
            
            upload_info = response.json()
            asset = upload_info['value']['asset']
            upload_url = upload_info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            
            # Upload the actual image
            headers = {
                'Authorization': f'Bearer {self.api.session.access_token}',
                'Content-Type': 'application/octet-stream'
            }
            
            upload_response = requests.post(upload_url, data=image_data, headers=headers)
            
            if upload_response.status_code == 201:
                print("✅ Image uploaded successfully!")
                return asset
            else:
                print(f"❌ Error uploading image: {upload_response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error in image upload: {e}")
            return None
    
    def schedule_post(self, text_content, image_path=None, schedule_time=None):
        """
        Schedule a post for later (basic implementation)
        """
        if schedule_time:
            print(f"⏰ Post scheduled for: {schedule_time}")
            # In a real implementation, you'd use a task scheduler like Celery
            # For now, we'll just post immediately
            print("📝 Posting immediately (scheduling not implemented)")
        
        if image_path:
            return self.post_image_with_text(text_content, image_path)
        else:
            return self.post_text(text_content)

def main():
    """
    Main function to demonstrate the LinkedIn automation with AI content generation
    """
    print("🚀 LinkedIn Automation Tool with AI Content Generation")
    print("=" * 60)
    
    # Load configuration
    config_file = "linkedin_config.json"
    
    if not os.path.exists(config_file):
        print("❌ Configuration file not found. Please create linkedin_config.json")
        print("Example configuration:")
        print('''
{
    "email": "your-email@example.com",
    "password": "your-password",
    "together_api_key": "your-together-ai-api-key",
    "ai_posts": [
        {
            "topic": "web development project",
            "industry": "technology",
            "tone": "professional",
            "generate_image": true,
            "image_prompt": "modern coding workspace"
        }
    ],
    "manual_posts": [
        {
            "text": "Check out this amazing content! #LinkedIn #Automation",
            "image": "path/to/image.jpg",
            "schedule": null
        }
    ]
}
        ''')
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Get API keys
        together_api_key = config.get('together_api_key') or os.getenv('TOGETHER_API_KEY')
        
        # Initialize LinkedIn automation with AI
        linkedin = LinkedInAutomation(
            config['email'], 
            config['password'],
            together_api_key
        )
        
        # Process AI-generated posts
        ai_posts = config.get('ai_posts', [])
        if ai_posts:
            print(f"\n🤖 Processing {len(ai_posts)} AI-generated posts...")
            
            for i, post_config in enumerate(ai_posts, 1):
                print(f"\n📝 Processing AI post {i}/{len(ai_posts)}")
                print(f"Topic: {post_config.get('topic', 'General')}")
                print(f"Industry: {post_config.get('industry', 'Technology')}")
                
                result = linkedin.generate_and_post(
                    topic=post_config.get('topic'),
                    industry=post_config.get('industry'),
                    tone=post_config.get('tone', 'professional'),
                    generate_image=post_config.get('generate_image', True),
                    image_prompt=post_config.get('image_prompt')
                )
                
                if result:
                    print("✅ AI post published successfully!")
                else:
                    print("❌ AI post failed!")
                
                # Add delay between posts to avoid rate limiting
                if i < len(ai_posts):
                    print("⏳ Waiting 30 seconds before next post...")
                    time.sleep(30)
        
        # Process manual posts
        manual_posts = config.get('manual_posts', [])
        if manual_posts:
            print(f"\n📝 Processing {len(manual_posts)} manual posts...")
            
            for i, post in enumerate(manual_posts, 1):
                print(f"\n📝 Processing manual post {i}/{len(manual_posts)}")
                print(f"Text: {post['text'][:50]}...")
                
                if 'image' in post and post['image']:
                    print(f"Image: {post['image']}")
                    if os.path.exists(post['image']):
                        linkedin.post_image_with_text(post['text'], post['image'])
                    else:
                        print(f"❌ Image file not found: {post['image']}")
                else:
                    linkedin.post_text(post['text'])
                
                # Add delay between posts to avoid rate limiting
                if i < len(manual_posts):
                    print("⏳ Waiting 30 seconds before next post...")
                    time.sleep(30)
        
        print("\n✅ All posts processed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 
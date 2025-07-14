#!/usr/bin/env python3
"""
Example usage of LinkedIn Automation Tool
This script demonstrates how to use the LinkedInAutomation class programmatically
"""

from linkedin_automation import LinkedInAutomation
import json
import os

def example_single_post():
    """Example of posting a single text post"""
    print("📝 Example: Single Text Post")
    print("=" * 40)
    
    # Initialize LinkedIn automation
    linkedin = LinkedInAutomation("your-email@example.com", "your-password")
    
    # Post text content
    text = "🚀 Excited to share my latest project! Building amazing web solutions and digital marketing strategies. #WebDevelopment #DigitalMarketing #Innovation"
    
    result = linkedin.post_text(text)
    if result:
        print("✅ Post successful!")
    else:
        print("❌ Post failed!")

def example_image_post():
    """Example of posting an image with text"""
    print("\n📸 Example: Image Post with Text")
    print("=" * 40)
    
    # Initialize LinkedIn automation
    linkedin = LinkedInAutomation("your-email@example.com", "your-password")
    
    # Post image with text
    text = "🎯 Just completed another successful client project! Here's a sneak peek at the results. Quality work always speaks for itself. #ClientSuccess #Results #Professional"
    image_path = "images/project_result.jpg"  # Make sure this file exists
    
    if os.path.exists(image_path):
        result = linkedin.post_image_with_text(text, image_path)
        if result:
            print("✅ Image post successful!")
        else:
            print("❌ Image post failed!")
    else:
        print(f"❌ Image file not found: {image_path}")

def example_batch_posts():
    """Example of batch posting from configuration"""
    print("\n📦 Example: Batch Posting")
    print("=" * 40)
    
    # Sample posts data
    posts_data = [
        {
            "text": "💡 Pro tip: Consistency is key in digital marketing. Small daily actions compound into massive results over time. What's your daily marketing routine? #DigitalMarketing #Growth #Consistency",
            "image": None
        },
        {
            "text": "🎯 Just completed another successful client project! Here's a sneak peek at the results. Quality work always speaks for itself. #ClientSuccess #Results #Professional",
            "image": "images/results.jpg"
        },
        {
            "text": "🚀 Excited to share my latest project! Building amazing web solutions and digital marketing strategies. #WebDevelopment #DigitalMarketing #Innovation",
            "image": "images/project1.jpg"
        }
    ]
    
    # Initialize LinkedIn automation
    linkedin = LinkedInAutomation("your-email@example.com", "your-password")
    
    # Process each post
    for i, post in enumerate(posts_data, 1):
        print(f"\n📝 Processing post {i}/{len(posts_data)}")
        print(f"Text: {post['text'][:50]}...")
        
        if post['image'] and os.path.exists(post['image']):
            print(f"Image: {post['image']}")
            result = linkedin.post_image_with_text(post['text'], post['image'])
        else:
            result = linkedin.post_text(post['text'])
        
        if result:
            print("✅ Post successful!")
        else:
            print("❌ Post failed!")

def create_sample_images_folder():
    """Create a sample images folder with placeholder files"""
    print("\n📁 Creating sample images folder...")
    
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
        print("✅ Created images/ directory")
    
    # Create placeholder files
    placeholder_files = [
        "images/project1.jpg",
        "images/results.jpg",
        "images/project_result.jpg"
    ]
    
    for file_path in placeholder_files:
        if not os.path.exists(file_path):
            # Create a simple text file as placeholder
            with open(file_path, 'w') as f:
                f.write("This is a placeholder image file.\nReplace with actual image files.")
            print(f"✅ Created placeholder: {file_path}")

def main():
    """Main function to run examples"""
    print("🚀 LinkedIn Automation - Example Usage")
    print("=" * 50)
    
    # Create sample images folder
    create_sample_images_folder()
    
    print("\n⚠️  IMPORTANT: Before running examples:")
    print("1. Edit this file and replace 'your-email@example.com' with your LinkedIn email")
    print("2. Replace 'your-password' with your LinkedIn password")
    print("3. Replace placeholder image files with actual images")
    print("4. Uncomment the example functions you want to run")
    
    print("\n📋 Available examples:")
    print("1. example_single_post() - Post a single text post")
    print("2. example_image_post() - Post an image with text")
    print("3. example_batch_posts() - Post multiple posts from data")
    
    print("\n🔧 To run examples, uncomment the function calls below:")
    
    # Uncomment the examples you want to run:
    
    # example_single_post()
    # example_image_post()
    # example_batch_posts()
    
    print("\n✅ Example setup complete!")

if __name__ == "__main__":
    main() 
 import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from linkedin_automation import LinkedInAutomation
import threading

class LinkedInAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Automation Tool with AI Content Generation")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # LinkedIn instance
        self.linkedin = None
        
        self.create_widgets()
        self.load_config()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 LinkedIn Automation Tool with AI Content Generation", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Login Section
        login_frame = ttk.LabelFrame(main_frame, text="LinkedIn Login & API Keys", padding="10")
        login_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        login_frame.columnconfigure(1, weight=1)
        
        ttk.Label(login_frame, text="LinkedIn Email:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(login_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(login_frame, text="LinkedIn Password:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, 
                                       show="*", width=40)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(login_frame, text="Together AI API Key:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.together_api_key_var = tk.StringVar()
        self.together_api_key_entry = ttk.Entry(login_frame, textvariable=self.together_api_key_var, 
                                               show="*", width=40)
        self.together_api_key_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        self.login_btn.grid(row=0, column=2, rowspan=3, padx=(10, 0))
        
        # Tab Control for different posting methods
        tab_control = ttk.Notebook(main_frame)
        tab_control.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # AI Content Generation Tab
        ai_tab = ttk.Frame(tab_control)
        tab_control.add(ai_tab, text="🤖 AI Content Generation")
        self.create_ai_tab(ai_tab)
        
        # Manual Post Tab
        manual_tab = ttk.Frame(tab_control)
        tab_control.add(manual_tab, text="📝 Manual Post")
        self.create_manual_tab(manual_tab)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=80)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_ai_tab(self, parent):
        """Create AI content generation tab"""
        parent.columnconfigure(0, weight=1)
        
        # AI Settings Frame
        ai_settings_frame = ttk.LabelFrame(parent, text="AI Content Settings", padding="10")
        ai_settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ai_settings_frame.columnconfigure(1, weight=1)
        
        # Topic
        ttk.Label(ai_settings_frame, text="Topic:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.topic_var = tk.StringVar()
        self.topic_entry = ttk.Entry(ai_settings_frame, textvariable=self.topic_var, width=50)
        self.topic_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Industry
        ttk.Label(ai_settings_frame, text="Industry:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.industry_var = tk.StringVar(value="technology")
        industry_combo = ttk.Combobox(ai_settings_frame, textvariable=self.industry_var, 
                                     values=["technology", "marketing", "business", "finance", "healthcare", "education"])
        industry_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Tone
        ttk.Label(ai_settings_frame, text="Tone:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.tone_var = tk.StringVar(value="professional")
        tone_combo = ttk.Combobox(ai_settings_frame, textvariable=self.tone_var,
                                 values=["professional", "casual", "enthusiastic", "educational"])
        tone_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Image generation options
        self.generate_image_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ai_settings_frame, text="Generate Image", 
                       variable=self.generate_image_var).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        
        # Image prompt
        ttk.Label(ai_settings_frame, text="Image Prompt:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.image_prompt_var = tk.StringVar()
        self.image_prompt_entry = ttk.Entry(ai_settings_frame, textvariable=self.image_prompt_var, width=50)
        self.image_prompt_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Generate and Post button
        self.ai_post_btn = ttk.Button(ai_settings_frame, text="🤖 Generate & Post AI Content", 
                                     command=self.generate_and_post_ai, state='disabled')
        self.ai_post_btn.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(parent, text="Generated Content Preview", padding="10")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, width=80)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_manual_tab(self, parent):
        """Create manual posting tab"""
        parent.columnconfigure(0, weight=1)
        
        # Post Content Section
        post_frame = ttk.LabelFrame(parent, text="Create Manual Post", padding="10")
        post_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        post_frame.columnconfigure(0, weight=1)
        post_frame.rowconfigure(1, weight=1)
        
        ttk.Label(post_frame, text="Post Text:").grid(row=0, column=0, sticky=tk.W)
        
        self.post_text = scrolledtext.ScrolledText(post_frame, height=6, width=70)
        self.post_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        
        # Image selection
        image_frame = ttk.Frame(post_frame)
        image_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        ttk.Label(image_frame, text="Image (optional):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.image_path_var = tk.StringVar()
        self.image_entry = ttk.Entry(image_frame, textvariable=self.image_path_var, width=50)
        self.image_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_btn = ttk.Button(image_frame, text="Browse", command=self.browse_image)
        self.browse_btn.grid(row=0, column=2)
        
        # Post button
        self.post_btn = ttk.Button(post_frame, text="📤 Post to LinkedIn", 
                                  command=self.post_content, state='disabled')
        self.post_btn.grid(row=3, column=0, pady=(10, 0))
    
    def load_config(self):
        """Load configuration from file if it exists"""
        try:
            if os.path.exists('linkedin_config.json'):
                with open('linkedin_config.json', 'r') as f:
                    config = json.load(f)
                    self.email_var.set(config.get('email', ''))
                    self.password_var.set(config.get('password', ''))
                    self.together_api_key_var.set(config.get('together_api_key', ''))
        except Exception as e:
            self.log_status(f"Error loading config: {e}")
    
    def save_config(self):
        """Save current configuration"""
        try:
            config = {
                'email': self.email_var.get(),
                'password': self.password_var.get(),
                'together_api_key': self.together_api_key_var.get(),
                'ai_posts': [],
                'manual_posts': []
            }
            with open('linkedin_config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.log_status(f"Error saving config: {e}")
    
    def login(self):
        """Login to LinkedIn"""
        email = self.email_var.get()
        password = self.password_var.get()
        together_api_key = self.together_api_key_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter both LinkedIn email and password")
            return
        
        self.login_btn.config(state='disabled')
        self.progress.start()
        self.log_status("🔐 Logging in to LinkedIn...")
        
        # Run login in separate thread
        thread = threading.Thread(target=self._login_thread, args=(email, password, together_api_key))
        thread.daemon = True
        thread.start()
    
    def _login_thread(self, email, password, together_api_key):
        """Login thread to avoid blocking GUI"""
        try:
            self.linkedin = LinkedInAutomation(email, password, together_api_key)
            self.save_config()
            
            # Update GUI in main thread
            self.root.after(0, self._login_success)
        except Exception as e:
            self.root.after(0, lambda: self._login_error(str(e)))
    
    def _login_success(self):
        self.progress.stop()
        self.login_btn.config(state='normal')
        self.post_btn.config(state='normal')
        self.ai_post_btn.config(state='normal')
        self.log_status("✅ Successfully logged in to LinkedIn!")
        if self.linkedin.ai_generator:
            self.log_status("✅ AI content generator initialized!")
        messagebox.showinfo("Success", "Successfully logged in to LinkedIn!")
    
    def _login_error(self, error):
        self.progress.stop()
        self.login_btn.config(state='normal')
        self.log_status(f"❌ Login failed: {error}")
        messagebox.showerror("Login Error", f"Failed to login: {error}")
    
    def generate_and_post_ai(self):
        """Generate AI content and post to LinkedIn"""
        if not self.linkedin:
            messagebox.showerror("Error", "Please login first")
            return
        
        if not self.linkedin.ai_generator:
            messagebox.showerror("Error", "AI generator not available. Please provide Together AI API key.")
            return
        
        topic = self.topic_var.get().strip()
        industry = self.industry_var.get()
        tone = self.tone_var.get()
        generate_image = self.generate_image_var.get()
        image_prompt = self.image_prompt_var.get().strip()
        
        if not topic:
            messagebox.showerror("Error", "Please enter a topic for AI content generation")
            return
        
        self.ai_post_btn.config(state='disabled')
        self.progress.start()
        self.log_status("🤖 Generating AI content...")
        
        # Run AI generation in separate thread
        thread = threading.Thread(target=self._ai_generation_thread, 
                                args=(topic, industry, tone, generate_image, image_prompt))
        thread.daemon = True
        thread.start()
    
    def _ai_generation_thread(self, topic, industry, tone, generate_image, image_prompt):
        """AI generation thread to avoid blocking GUI"""
        try:
            result = self.linkedin.generate_and_post(
                topic=topic,
                industry=industry,
                tone=tone,
                generate_image=generate_image,
                image_prompt=image_prompt
            )
            
            if result:
                self.root.after(0, self._ai_post_success)
            else:
                self.root.after(0, lambda: self._ai_post_error("Failed to generate and post AI content"))
        except Exception as e:
            self.root.after(0, lambda: self._ai_post_error(str(e)))
    
    def _ai_post_success(self):
        self.progress.stop()
        self.ai_post_btn.config(state='normal')
        self.log_status("✅ AI content generated and posted successfully!")
        messagebox.showinfo("Success", "AI content generated and posted successfully!")
        
        # Clear the form
        self.topic_var.set("")
        self.image_prompt_var.set("")
        self.preview_text.delete("1.0", tk.END)
    
    def _ai_post_error(self, error):
        self.progress.stop()
        self.ai_post_btn.config(state='normal')
        self.log_status(f"❌ AI post failed: {error}")
        messagebox.showerror("AI Post Error", f"Failed to generate and post: {error}")
    
    def browse_image(self):
        """Browse for image file"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.image_path_var.set(filename)
    
    def post_content(self):
        """Post manual content to LinkedIn"""
        if not self.linkedin:
            messagebox.showerror("Error", "Please login first")
            return
        
        text = self.post_text.get("1.0", tk.END).strip()
        image_path = self.image_path_var.get().strip()
        
        if not text:
            messagebox.showerror("Error", "Please enter some text for your post")
            return
        
        if image_path and not os.path.exists(image_path):
            messagebox.showerror("Error", "Image file not found")
            return
        
        self.post_btn.config(state='disabled')
        self.progress.start()
        self.log_status("📤 Posting to LinkedIn...")
        
        # Run post in separate thread
        thread = threading.Thread(target=self._post_thread, args=(text, image_path))
        thread.daemon = True
        thread.start()
    
    def _post_thread(self, text, image_path):
        """Post thread to avoid blocking GUI"""
        try:
            if image_path:
                result = self.linkedin.post_image_with_text(text, image_path)
            else:
                result = self.linkedin.post_text(text)
            
            if result:
                self.root.after(0, self._post_success)
            else:
                self.root.after(0, lambda: self._post_error("Failed to post content"))
        except Exception as e:
            self.root.after(0, lambda: self._post_error(str(e)))
    
    def _post_success(self):
        self.progress.stop()
        self.post_btn.config(state='normal')
        self.log_status("✅ Post published successfully!")
        messagebox.showinfo("Success", "Post published successfully!")
        
        # Clear the form
        self.post_text.delete("1.0", tk.END)
        self.image_path_var.set("")
    
    def _post_error(self, error):
        self.progress.stop()
        self.post_btn.config(state='normal')
        self.log_status(f"❌ Post failed: {error}")
        messagebox.showerror("Post Error", f"Failed to post: {error}")
    
    def log_status(self, message):
        """Add message to status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)

def main():
    root = tk.Tk()
    app = LinkedInAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
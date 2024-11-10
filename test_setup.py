import os
from dotenv import load_dotenv

def test_environment():
    print("Testing environment setup...")
    
    # Test .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print("✓ .env file found")
        load_dotenv(env_path)
        
        # Check required environment variables
        required_vars = ['GROQ_API_KEY', 'YOUTUBE_EMAIL', 'YOUTUBE_PASSWORD']
        for var in required_vars:
            if os.getenv(var):
                print(f"✓ {var} is set")
            else:
                print(f"✗ {var} is missing")
    else:
        print("✗ .env file not found")
    
    # Test cookies file
    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    if os.path.exists(cookies_path):
        print("✓ cookies.txt file found")
        # Check if file has content
        with open(cookies_path, 'r') as f:
            content = f.read().strip()
            if content:
                print("✓ cookies.txt has content")
            else:
                print("✗ cookies.txt is empty")
    else:
        print("✗ cookies.txt not found")
    
    # Test required packages
    try:
        import streamlit
        print("✓ streamlit is installed")
    except ImportError:
        print("✗ streamlit is missing")
    
    try:
        import youtube_transcript_api
        print("✓ youtube_transcript_api is installed")
    except ImportError:
        print("✗ youtube_transcript_api is missing")
    
    try:
        from selenium import webdriver
        print("✓ selenium is installed")
    except ImportError:
        print("✗ selenium is missing")

if __name__ == "__main__":
    test_environment()
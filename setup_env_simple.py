"""
Simple script to create .env file with Gemini API key.
Alternative to setup_api_key.py - simpler version.
"""

import os

def create_env_file():
    """Create .env file with API key."""
    print("="*60)
    print("Simple .env File Setup")
    print("="*60)
    print("\nThis script will create a .env file with your Gemini API key.")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    print()
    
    # Check if .env already exists
    if os.path.exists(".env"):
        print("[WARN] .env file already exists.")
        response = input("Do you want to overwrite it? (y/n): ").lower()
        if response != 'y':
            print("Keeping existing .env file.")
            return False
    
    # Get API key
    print("\nEnter your Gemini API key:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("[ERROR] API key cannot be empty!")
        return False
    
    # Create .env content
    env_content = f"""# Gemini API Configuration
GEMINI_API_KEY={api_key}

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Data Configuration (optional)
DATA_DIR=data
"""
    
    # Write to file
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("\n[OK] .env file created successfully!")
        print(f"[OK] API key saved: {api_key[:10]}...{api_key[-4:]}")
        print("\nYou can now:")
        print("  - Run: python setup_backend.py")
        print("  - Run: python api.py")
        print("  - Run: python run_test.py")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error creating .env file: {e}")
        return False


if __name__ == "__main__":
    create_env_file()



"""
Script to set up Gemini API key in .env file.
"""

import os
import sys


def setup_api_key():
    """Interactive script to set up Gemini API key."""
    print("="*60)
    print("Gemini API Key Setup")
    print("="*60)
    print("\nThis script will help you set up your Gemini API key.")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    print()
    
    # Check if .env exists
    env_file = ".env"
    env_exists = os.path.exists(env_file)
    
    if env_exists:
        print(f"Found existing .env file.")
        # Read current API key if exists
        current_key = None
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        current_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
        
        if current_key and current_key != "your_gemini_api_key_here":
            print(f"Current API key: {current_key[:10]}...{current_key[-4:]}")
            response = input("\nDo you want to update it? (y/n): ").lower()
            if response != 'y':
                print("Keeping existing API key.")
                return True
    else:
        print("Creating new .env file...")
    
    # Get API key from user
    print("\nEnter your Gemini API key:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("[ERROR] API key cannot be empty!")
        return False
    
    # Validate format (basic check)
    if len(api_key) < 20:
        print("[WARN] Warning: API key seems too short. Please verify it's correct.")
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            return False
    
    # Read existing .env or create new content
    env_content = []
    if env_exists:
        try:
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        except:
            pass
    
    # Update or add GEMINI_API_KEY
    updated = False
    new_content = []
    for line in env_content:
        if line.startswith('GEMINI_API_KEY='):
            new_content.append(f'GEMINI_API_KEY={api_key}\n')
            updated = True
        else:
            new_content.append(line)
    
    if not updated:
        # Add new line if file doesn't end with newline
        if new_content and not new_content[-1].endswith('\n'):
            new_content[-1] = new_content[-1] + '\n'
        new_content.append(f'GEMINI_API_KEY={api_key}\n')
    
    # Add other default values if not present
    defaults = {
        'API_HOST': '0.0.0.0',
        'API_PORT': '8000',
        'API_DEBUG': 'false'
    }
    
    for key, value in defaults.items():
        if not any(line.startswith(f'{key}=') for line in new_content):
            new_content.append(f'{key}={value}\n')
    
    # Write to file
    try:
        with open(env_file, 'w') as f:
            f.writelines(new_content)
        
        print(f"\n[OK] API key saved to {env_file}")
        print("\nNext steps:")
        print("1. Run: python main.py (to extract fund data)")
        print("2. Run: python setup_backend.py (to build vector store)")
        print("3. Run: python api.py (to start the server)")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error saving API key: {e}")
        return False


def verify_api_key():
    """Verify if API key is set and test connection."""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[ERROR] GEMINI_API_KEY not set in .env file")
        return False
    
    print(f"[OK] API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test connection
    try:
        from gemini_client import GeminiClient
        print("Testing connection to Gemini API...")
        client = GeminiClient()
        if client.test_connection():
            print("[OK] Gemini API connection successful!")
            return True
        else:
            print("[ERROR] Gemini API connection failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error testing connection: {e}")
        print("\nTroubleshooting:")
        print("1. Check if your API key is correct")
        print("2. Check your internet connection")
        print("3. Verify API key has proper permissions")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        # Verify mode
        verify_api_key()
    else:
        # Setup mode
        success = setup_api_key()
        if success:
            print("\n" + "="*60)
            print("Verifying API key...")
            print("="*60)
            verify_api_key()


#!/usr/bin/env python3
"""
Test script to verify which AI models are available with your API keys.
This helps identify the correct model names to use.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_models():
    """Test Google Gemini model availability."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("\n📋 Available Gemini Models:")
        print("-" * 40)
        
        available_models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace("models/", "")
                available_models.append(model_name)
                print(f"  ✅ {model_name}")
        
        # Test specific models
        print("\n🧪 Testing Specific Models:")
        print("-" * 40)
        
        test_models = [
            "gemini-2.5-pro",       # From requirements
            "gemini-2.5-flash",     # From requirements
            "gemini-1.5-pro-latest", # Currently available
            "gemini-1.5-flash-latest", # Currently available
            "gemini-1.5-pro",       # Alternative
            "gemini-1.5-flash",     # Alternative
        ]
        
        for model_name in test_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'OK' if you're working")
                if response.text:
                    print(f"  ✅ {model_name} - Working")
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    print(f"  ❌ {model_name} - Not available")
                else:
                    print(f"  ⚠️  {model_name} - Error: {error_msg[:50]}")
        
        return True
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        return False
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        return False


def test_claude_models():
    """Test Anthropic Claude model availability."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        print("\n🧪 Testing Claude Models:")
        print("-" * 40)
        
        test_models = [
            "claude-sonnet-4-5-20250929",  # From requirements
            "claude-3-5-sonnet-20241022",  # Currently available
            "claude-3-sonnet-20240229",    # Alternative
        ]
        
        for model_name in test_models:
            try:
                message = client.messages.create(
                    model=model_name,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Say OK"}]
                )
                if message.content:
                    print(f"  ✅ {model_name} - Working")
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower() or "model_not_found" in error_msg:
                    print(f"  ❌ {model_name} - Not available")
                else:
                    print(f"  ⚠️  {model_name} - Error: {error_msg[:50]}")
        
        return True
        
    except ImportError:
        print("❌ anthropic package not installed")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude: {e}")
        return False


def suggest_env_config():
    """Suggest .env configuration based on test results."""
    print("\n💡 Suggested .env Configuration:")
    print("-" * 40)
    print("""
# Based on the tests above, use the working model names in your .env:

# If gemini-2.5 models are not available, use:
GEMINI_PRO=gemini-1.5-pro-latest
GEMINI_FLASH=gemini-1.5-flash-latest

# For Claude, use the working version:
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Or copy the alternative configuration:
# cp env.alternative.example .env
""")


def main():
    """Run all tests."""
    print("=" * 50)
    print("🤖 AI Model Availability Tester")
    print("=" * 50)
    
    # Check for API keys
    has_google = bool(os.getenv("GOOGLE_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not has_google and not has_anthropic:
        print("\n❌ No API keys found!")
        print("\n1. Create a .env file:")
        print("   cp env.example .env")
        print("\n2. Add your API keys to the .env file")
        print("\n3. Run this script again")
        return
    
    # Test available models
    if has_google:
        test_gemini_models()
    
    if has_anthropic:
        test_claude_models()
    
    # Suggest configuration
    suggest_env_config()
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()

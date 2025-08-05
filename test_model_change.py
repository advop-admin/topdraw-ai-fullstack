#!/usr/bin/env python3
"""
Test script to verify the new model configuration
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_new_model():
    """Test the new model configuration"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    print("🔑 Testing new model configuration...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test the new model (gemini-1.5-pro)
        new_model = "gemini-1.5-pro"
        print(f"🧪 Testing {new_model}...")
        
        model = genai.GenerativeModel(new_model)
        
        # Simple test prompt
        test_prompt = "Hello! Please respond with 'New model is working' if you can see this message."
        
        response = model.generate_content(test_prompt)
        
        if response.text:
            print(f"✅ {new_model} is working!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ {new_model} returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {new_model}: {str(e)}")
        
        # Check if it's still a rate limit
        if "429" in str(e) or "quota" in str(e).lower():
            print("\n💡 Rate limit still active. Options:")
            print("1. Wait 1-2 minutes and try again")
            print("2. Upgrade to paid Gemini API plan")
            print("3. Use the fallback mode (already implemented)")
            print("4. Try a different model")
        
        return False

if __name__ == "__main__":
    print("🧭 Testing New Model Configuration")
    print("=" * 40)
    
    success = test_new_model()
    
    if success:
        print("\n✅ New model configuration is working!")
        print("🚀 You can proceed with deployment")
    else:
        print("\n⚠️  Model test failed, but fallback mode is available")
        print("🔧 The application will work with fallback blueprints") 
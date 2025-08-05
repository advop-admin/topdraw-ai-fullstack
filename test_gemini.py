#!/usr/bin/env python3
"""
Test script to check Gemini API token and available models
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API token and list available models"""
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in the .env file")
        return False
    
    print(f"🔑 Found Gemini API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Available Gemini Models:")
        models = genai.list_models()
        
        gemini_models = []
        for model in models:
            if 'gemini' in model.name.lower():
                gemini_models.append(model.name)
                print(f"  ✅ {model.name}")
        
        if not gemini_models:
            print("  ❌ No Gemini models found")
            return False
        
        # Test current model (gemini-1.5-flash)
        current_model = "gemini-1.5-flash"
        print(f"\n🧪 Testing current model: {current_model}")
        
        try:
            model = genai.GenerativeModel(current_model)
            
            # Simple test prompt
            test_prompt = "Hello! Please respond with 'API is working' if you can see this message."
            
            response = model.generate_content(test_prompt)
            
            if response.text:
                print(f"✅ {current_model} is working!")
                print(f"Response: {response.text}")
                return True
            else:
                print(f"❌ {current_model} returned empty response")
                return False
                
        except Exception as e:
            print(f"❌ Error testing {current_model}: {str(e)}")
            
            # Try alternative models
            print("\n🔄 Trying alternative models...")
            
            alternative_models = [
                "gemini-1.5-pro",
                "gemini-1.0-pro",
                "gemini-pro"
            ]
            
            for alt_model in alternative_models:
                if alt_model in gemini_models:
                    try:
                        print(f"  Testing {alt_model}...")
                        model = genai.GenerativeModel(alt_model)
                        response = model.generate_content(test_prompt)
                        
                        if response.text:
                            print(f"✅ {alt_model} is working!")
                            print(f"Response: {response.text}")
                            print(f"\n💡 Recommendation: Update your .env file to use {alt_model}")
                            return True
                    except Exception as e:
                        print(f"  ❌ {alt_model} failed: {str(e)}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {str(e)}")
        return False

def check_quota_usage():
    """Check API quota usage (if available)"""
    print("\n📊 Checking API quota...")
    
    try:
        # This is a basic check - actual quota info might require different API calls
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print("ℹ️  To check detailed quota usage, visit:")
            print("   https://makersuite.google.com/app/apikey")
            print("   or")
            print("   https://console.cloud.google.com/apis/credentials")
    except Exception as e:
        print(f"❌ Could not check quota: {str(e)}")

if __name__ == "__main__":
    print("🧭 Topsdraw Compass - Gemini API Test")
    print("=" * 50)
    
    success = test_gemini_api()
    check_quota_usage()
    
    if success:
        print("\n✅ Gemini API is working correctly!")
        print("🚀 You can proceed with deployment")
    else:
        print("\n❌ Gemini API test failed")
        print("🔧 Please check your API key and try again") 
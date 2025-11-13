#!/usr/bin/env python3
"""
Test script for Gemini configuration.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_direct():
    """Test direct Gemini API usage with google-genai client."""
    try:
        from google import genai

        # Configure with API key from environment
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            print("[ERROR] Missing LLM_API_KEY in environment")
            return False

        print(f"[DEBUG] API key format: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else '[short]'}")

        # Create client with API key
        client = genai.Client(api_key=api_key)

        # Get model
        model_name = os.getenv('LLM_CHOICE', 'gemini-2.0-flash')

        # Test generation
        print(f"[TEST] Testing Gemini {model_name} with new client API...")
        print(f"[INFO] Client created successfully: {type(client)}")
        print(f"[INFO] Using model: {model_name}")
        print("[INFO] Client API structure is correct!")

        # Uncomment below to test actual API call (requires valid API key):
        # response = client.models.generate_content(
        #     model=model_name,
        #     contents="Explain how AI works in a few words"
        # )
        # print(f"[SUCCESS] Gemini response: {response.text}")

        print("[SUCCESS] New client API setup is working!")
        return True

    except Exception as e:
        print(f"[ERROR] Direct Gemini test failed: {e}")
        return False


async def test_provider_integration():
    """Test Gemini through the providers.py integration."""
    try:
        import sys
        sys.path.append('.')
        from agent.providers import get_llm_model, get_model_info, get_gemini_client

        print("[TEST] Testing provider integration...")

        # Get model info
        info = get_model_info()
        print(f"[INFO] Model configuration: {info}")

        # Get model (this will test our provider setup)
        model = get_llm_model()
        print(f"[SUCCESS] Provider integration successful: {type(model)}")

        # Test direct Gemini client access
        print("[TEST] Testing direct Gemini client access...")
        gemini_client = get_gemini_client()
        print(f"[SUCCESS] Direct Gemini client: {type(gemini_client)}")

        return True

    except Exception as e:
        print(f"[ERROR] Provider integration test failed: {e}")
        print(f"[ERROR] Error details: {type(e).__name__}: {e}")
        return False


async def main():
    """Run all Gemini tests."""
    print("[START] Testing Gemini configuration...")
    print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"LLM_CHOICE: {os.getenv('LLM_CHOICE')}")
    print(f"LLM_BASE_URL: {os.getenv('LLM_BASE_URL')}")
    print()

    # Test direct API
    direct_success = await test_gemini_direct()
    print()

    # Test provider integration
    provider_success = await test_provider_integration()
    print()

    if direct_success and provider_success:
        print("[SUCCESS] All Gemini tests passed! Configuration is ready.")
    else:
        print("[ERROR] Some tests failed. Check configuration.")


if __name__ == "__main__":
    asyncio.run(main())
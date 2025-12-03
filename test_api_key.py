#!/usr/bin/env python3
"""
Quick script to test if your OpenAI API key works
Usage: python test_api_key.py
"""

from openai import OpenAI
import sys

def test_api_key():
    print("🔑 OpenAI API Key Tester\n")

    # Get API key from user
    api_key = input("Paste your OpenAI API key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return False

    print(f"\n📋 Key format: {api_key[:7]}...{api_key[-4:]}")
    print(f"📏 Key length: {len(api_key)} characters")

    # Check format
    if not (api_key.startswith("sk-") or api_key.startswith("sk-proj-")):
        print("⚠️  Warning: Key doesn't start with 'sk-' or 'sk-proj-'")

    # Test the key
    print("\n🧪 Testing API key...")
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'API key works!'"}],
            max_tokens=10
        )

        print("✅ SUCCESS! Your API key works!")
        print(f"📝 Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: {error_msg}\n")

        # Provide specific guidance
        if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
            print("💡 Solution: Your API key is invalid or has been revoked.")
            print("   → Create a new key at: https://platform.openai.com/api-keys")

        elif "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            print("💡 Solution: Your account has no credits.")
            print("   → Add payment method at: https://platform.openai.com/account/billing")
            print("   → Or check if free trial expired")

        elif "rate_limit" in error_msg.lower():
            print("💡 Solution: You've hit rate limits.")
            print("   → Wait a minute and try again")
            print("   → Or upgrade your plan")

        else:
            print("💡 Solution: Check the error message above")
            print("   → Visit: https://platform.openai.com/account")

        return False

if __name__ == "__main__":
    test_api_key()

"""Quick test script to verify OpenAI API configuration."""

import os
import sys
from dotenv import load_dotenv

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_openai_config():
    """Test OpenAI API configuration."""
    print("Testing OpenAI Configuration...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("   Make sure you have a .env file in the backend directory")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ ERROR: Invalid API key format (should start with 'sk-')")
        print(f"   Current value starts with: {api_key[:3]}")
        return False
    
    if "your-" in api_key or "placeholder" in api_key.lower():
        print("❌ ERROR: API key appears to be a placeholder")
        print("   Please update .env with your real OpenAI API key")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Check model settings
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    print(f"✅ Chat Model: {model}")
    print(f"✅ Embedding Model: {embedding_model}")
    
    # Test API connection
    print("\nTesting API connection...")
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Test embedding
        print("  Testing embedding generation...")
        response = client.embeddings.create(
            model=embedding_model,
            input="test"
        )
        print(f"  ✅ Embedding generated: {len(response.data[0].embedding)} dimensions")
        
        # Test chat (simple)
        print("  Testing chat completion...")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'Hello'"}],
            max_tokens=10
        )
        print(f"  ✅ Chat response: {response.choices[0].message.content}")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! OpenAI is configured correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nCommon issues:")
        print("  - Invalid API key")
        print("  - No access to the model")
        print("  - Billing not set up")
        print("  - Network connectivity issues")
        return False

if __name__ == "__main__":
    success = test_openai_config()
    exit(0 if success else 1)

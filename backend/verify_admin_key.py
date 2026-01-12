"""Quick script to verify admin key format."""

import os
from dotenv import load_dotenv

load_dotenv()

def verify_key():
    """Verify the admin key format."""
    key = os.getenv("AZURE_SEARCH_API_KEY", "")
    
    print("=" * 50)
    print("Admin Key Verification")
    print("=" * 50)
    
    if not key:
        print("[ERROR] AZURE_SEARCH_API_KEY not found in .env")
        return False
    
    # Check for common issues
    key_trimmed = key.strip()
    
    print(f"\nKey Length: {len(key_trimmed)} characters")
    print(f"Key Preview: {key_trimmed[:15]}...{key_trimmed[-10:]}")
    
    issues = []
    
    # Check for whitespace
    if key != key_trimmed:
        issues.append("Key has leading/trailing whitespace")
    
    if ' ' in key or '\t' in key:
        issues.append("Key contains spaces or tabs")
    
    # Check length (admin keys are usually 32+ characters)
    if len(key_trimmed) < 30:
        issues.append(f"Key seems too short (admin keys are usually 32+ characters)")
    
    if issues:
        print("\n[WARNINGS]:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nTo fix:")
        print("1. Go to Azure Portal → Your Search Service → Keys")
        print("2. Click 'Show' next to 'Admin Key (primary)'")
        print("3. Copy the ENTIRE key (no spaces)")
        print("4. In .env, make sure: AZURE_SEARCH_API_KEY=your-key-here")
        print("5. No spaces around the = sign")
        return False
    else:
        print("\n[OK] Key format looks good!")
        print("\nIf you're still getting errors:")
        print("1. Double-check you copied 'Admin Key (primary)', NOT 'Query Key'")
        print("2. Make sure there are no extra spaces in your .env file")
        print("3. Try copying the key again from Azure Portal")
        return True

if __name__ == "__main__":
    verify_key()

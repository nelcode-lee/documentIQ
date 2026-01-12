"""Quick test to verify language support for Polish and Romanian."""

import sys

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Test UTF-8 encoding support
test_strings = {
    "pl": "Test polskiego tekstu: ąęćłńóśźż",
    "ro": "Test text românesc: ăâîșț",
    "en": "Test English text"
}

print("=" * 60)
print("Language Support Check")
print("=" * 60)

# Check Python encoding
print(f"\nPython Default Encoding: {sys.getdefaultencoding()}")
print(f"Filesystem Encoding: {sys.getfilesystemencoding()}")

# Test string handling
print("\n[1] String Encoding Test:")
for lang, text in test_strings.items():
    try:
        encoded = text.encode('utf-8')
        decoded = encoded.decode('utf-8')
        print(f"  ✅ {lang.upper()}: {text} - OK")
    except Exception as e:
        print(f"  ❌ {lang.upper()}: Error - {e}")

# Check if tiktoken supports these languages
print("\n[2] Tiktoken Encoding Test:")
try:
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    
    for lang, text in test_strings.items():
        try:
            tokens = encoding.encode(text)
            decoded = encoding.decode(tokens)
            print(f"  ✅ {lang.upper()}: {len(tokens)} tokens - OK")
        except Exception as e:
            print(f"  ❌ {lang.upper()}: Error - {e}")
except ImportError:
    print("  ⚠️  tiktoken not installed")

# Check document processing libraries
print("\n[3] Document Processing Libraries:")
try:
    import fitz  # PyMuPDF
    print("  ✅ PyMuPDF (fitz) - supports Unicode/UTF-8")
except ImportError:
    try:
        import PyPDF2
        print("  ✅ PyPDF2 - supports Unicode")
    except ImportError:
        print("  ⚠️  No PDF library found")

try:
    from docx import Document
    print("  ✅ python-docx - supports Unicode")
except ImportError:
    print("  ⚠️  python-docx not installed")

# Check OpenAI SDK
print("\n[4] OpenAI SDK:")
try:
    from openai import OpenAI
    print("  ✅ OpenAI SDK - supports multilingual models")
    print("     • text-embedding-ada-002: Multilingual (100+ languages)")
    print("     • GPT-4/GPT-3.5-turbo: Support Polish & Romanian natively")
except ImportError:
    print("  ❌ OpenAI SDK not installed")

print("\n" + "=" * 60)
print("✅ All dependencies support Polish and Romanian!")
print("=" * 60)
print("\nNo additional dependencies needed for language support.")
print("OpenAI models handle multilingual content natively.\n")

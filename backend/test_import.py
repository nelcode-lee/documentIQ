"""Quick test to check if backend imports work correctly."""

import sys
import os

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, '.')

try:
    print("Testing imports...")
    from app.config import settings
    print("[OK] Config loaded")
    
    from app.models.chat import ChatRequest
    print("[OK] ChatRequest model loaded")
    
    from app.services.chat_service import ChatService
    print("[OK] ChatService loaded")
    
    from app.routers.chat import router
    print("[OK] Chat router loaded")
    
    from app.main import app
    print("[OK] FastAPI app loaded")
    
    print("\n[SUCCESS] All imports successful!")
    
except Exception as e:
    print(f"\n[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

"""Script to start the backend with better error handling."""

import sys
import os

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Only run if this is the main script (not when imported by uvicorn reloader)
if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Starting Backend Server")
        print("=" * 60)
        
        # Check .env file exists
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if not os.path.exists(env_file):
            print("[ERROR] .env file not found!")
            print(f"Expected location: {env_file}")
            print("\nPlease create a .env file with your configuration.")
            sys.exit(1)
        
        print("[OK] .env file found")
        
        # Try to load settings
        try:
            from app.config import settings
            print("[OK] Settings loaded")
            print(f"  - API Prefix: {settings.api_v1_prefix}")
            print(f"  - OpenAI Model: {settings.openai_model}")
            print(f"  - Search Index: {settings.azure_search_index_name}")
        except Exception as e:
            print(f"[ERROR] Failed to load settings: {e}")
            sys.exit(1)
        
        # Test imports
        try:
            from app.main import app
            print("[OK] FastAPI app imported successfully")
        except Exception as e:
            print(f"[ERROR] Failed to import app: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("Starting Uvicorn server...")
        print("=" * 60)
        print("\nServer will be available at: http://localhost:8000")
        print("API Docs at: http://localhost:8000/docs\n")
        
        # Start uvicorn
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

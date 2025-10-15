"""
Main entry point for running the application.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Run the application."""
    
    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("Warning: .env file not found")
        print("Creating .env from env.example...")
        example_file = Path(__file__).parent / "env.example"
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("Please edit .env with your API keys")
        else:
            print("env.example not found. Please create .env with your configuration")
            return
    
    # Load environment if .env exists
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    # Import here to ensure environment is loaded first
    from app import app
    from config import settings
    
    print("=" * 60)
    print("Microlearning Content Generator")
    print("=" * 60)
    print()
    print(f"Server: http://localhost:{settings.port}")
    print(f"Password: {settings.editor_password or 'Not set (open access)'}")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Run the server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()

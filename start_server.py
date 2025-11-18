"""
Start both frontend and backend server.
"""

import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread

def start_backend():
    """Start the FastAPI backend server."""
    print("[Backend] Starting API server on http://localhost:8000")
    try:
        import uvicorn
        from api import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"[Backend] Error: {e}")
        sys.exit(1)

def open_browser():
    """Open browser after a delay."""
    time.sleep(3)
    print("\n[Frontend] Opening browser...")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("="*60)
    print("ICICI Prudential AMC FAQ Assistant")
    print("Starting Backend Server...")
    print("="*60)
    print("\nBackend API: http://localhost:8000")
    print("Frontend UI: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Open browser in a separate thread
    browser_thread = Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start backend (which serves frontend)
    start_backend()



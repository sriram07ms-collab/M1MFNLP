"""
Setup script to prepare the backend.
Builds vector store index from scraped data.
"""

import os
from data_storage import DataStorage
from vector_store import VectorStore
from gemini_client import GeminiClient
from config import RAG_DATA_FILE, GEMINI_API_KEY


def setup_backend():
    """Setup backend: export RAG data and build vector store."""
    print("="*60)
    print("ICICI Prudential AMC FAQ Assistant - Backend Setup")
    print("="*60)
    
    # Step 1: Check if RAG data exists
    print("\n[1/4] Checking RAG data...")
    storage = DataStorage()
    
    # Export RAG data if not exists
    if not os.path.exists(RAG_DATA_FILE):
        print("  RAG data not found. Exporting from stored fund data...")
        storage.export_for_rag()
    else:
        print(f"  ✓ RAG data found at {RAG_DATA_FILE}")
    
    # Step 2: Verify Gemini API key
    print("\n[2/4] Verifying Gemini API configuration...")
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("  ✗ GEMINI_API_KEY not set in .env file")
        print("  Please set GEMINI_API_KEY in .env file")
        return False
    else:
        print("  ✓ Gemini API key found")
    
    # Step 3: Test Gemini connection
    print("\n[3/4] Testing Gemini API connection...")
    try:
        client = GeminiClient()
        if client.test_connection():
            print("  ✓ Gemini API connection successful")
        else:
            print("  ✗ Gemini API connection failed")
            return False
    except Exception as e:
        print(f"  ✗ Error testing Gemini API: {e}")
        return False
    
    # Step 4: Build vector store index
    print("\n[4/4] Building vector store index...")
    vector_store = VectorStore()
    
    if vector_store.build_index():
        print("  ✓ Vector store index built successfully")
        
        # Show stats
        stats = vector_store.get_stats()
        print(f"\n  Vector Store Statistics:")
        print(f"    - Total facts: {stats['total_facts']}")
        print(f"    - Embedding model: {stats['embedding_model']}")
        print(f"    - Dimension: {stats['dimension']}")
    else:
        print("  ✗ Failed to build vector store index")
        print("  Make sure you have scraped fund data first (run main.py)")
        return False
    
    print("\n" + "="*60)
    print("✓ Backend setup completed successfully!")
    print("="*60)
    print("\nYou can now start the API server with:")
    print("  python api.py")
    print("\nOr use uvicorn:")
    print("  uvicorn api:app --reload")
    
    return True


if __name__ == "__main__":
    success = setup_backend()
    exit(0 if success else 1)



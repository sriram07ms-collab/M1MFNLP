"""
Configuration file for the FAQ Assistant backend.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Gemini 2.0 Flash model
# Alternative: "gemini-2.0-flash" or "gemini-1.5-flash" if above doesn't work

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
# Render and other PaaS providers expose the listening port via PORT
API_PORT = int(os.getenv("PORT") or os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

# Data Configuration
DATA_DIR = os.getenv("DATA_DIR", "data")
FUNDS_DATA_FILE = os.path.join(DATA_DIR, "funds_data.json")
RAG_DATA_FILE = os.path.join(DATA_DIR, "rag_data.json")

# Vector Store Configuration
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight embedding model
VECTOR_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# RAG Configuration
TOP_K_RESULTS = 3  # Number of relevant facts to retrieve
MAX_CONTEXT_LENGTH = 2000  # Maximum context length for LLM

# Validation (only raise error when actually using Gemini, not on import)
# This allows vector store to be built without API key
def validate_gemini_key():
    """Validate Gemini API key. Call this before using Gemini."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in .env file")
    return True


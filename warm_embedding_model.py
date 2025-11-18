"""
Warm up the sentence-transformer embedding model.

Render free tier instances sometimes hit runtime limits while downloading
model artifacts. Running this script during the build phase pre-downloads
the embeddings so the server can start quickly.
"""

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL


def main():
    print(f"Downloading embedding model: {EMBEDDING_MODEL}")
    SentenceTransformer(EMBEDDING_MODEL)
    print("✓ Model cached successfully")


if __name__ == "__main__":
    main()


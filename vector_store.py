"""
Vector store for semantic search using FAISS.
Stores fund facts as embeddings for RAG retrieval.
"""

import os
import json
import faiss
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from config import VECTOR_STORE_DIR, EMBEDDING_MODEL, VECTOR_DIMENSION, RAG_DATA_FILE


class VectorStore:
    """Vector store for semantic search of fund facts."""
    
    def __init__(self):
        """Initialize vector store with embedding model."""
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.facts = []  # Store original facts with metadata
        self._ensure_vector_store_dir()
    
    def _ensure_vector_store_dir(self):
        """Create vector store directory if it doesn't exist."""
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    def load_rag_data(self) -> List[Dict]:
        """Load RAG data from JSON file."""
        if not os.path.exists(RAG_DATA_FILE):
            print(f"RAG data file not found: {RAG_DATA_FILE}")
            print("Please run the data extraction first to generate RAG data.")
            return []
        
        try:
            with open(RAG_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading RAG data: {e}")
            return []
    
    def build_index(self, rag_data: Optional[List[Dict]] = None) -> bool:
        """
        Build FAISS index from RAG data.
        
        Args:
            rag_data: Optional RAG data. If None, loads from file.
        
        Returns:
            True if successful, False otherwise
        """
        if rag_data is None:
            rag_data = self.load_rag_data()
        
        if not rag_data:
            print("No RAG data available to build index")
            return False
        
        # Extract all facts from all funds
        all_facts = []
        for fund in rag_data:
            fund_name = fund.get('fund_name', 'Unknown')
            fund_id = fund.get('fund_id', '')
            source_url = fund.get('source_url', '')
            
            for fact in fund.get('facts', []):
                fact_text = fact.get('fact', '')
                category = fact.get('category', '')
                fact_source_url = fact.get('source_url', source_url)
                
                # Store fact with metadata
                all_facts.append({
                    'fact': fact_text,
                    'category': category,
                    'source_url': fact_source_url,
                    'fund_name': fund_name,
                    'fund_id': fund_id
                })
        
        if not all_facts:
            print("No facts found in RAG data")
            return False
        
        # Generate embeddings
        print(f"Generating embeddings for {len(all_facts)} facts...")
        fact_texts = [f["fact"] for f in all_facts]
        embeddings = self.embedding_model.encode(
            fact_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        self.facts = all_facts
        
        print(f"[OK] Built FAISS index with {len(all_facts)} facts")
        
        # Save index and facts
        self.save_index()
        
        return True
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant facts using semantic similarity.
        
        Args:
            query: User's question
            top_k: Number of top results to return
        
        Returns:
            List of relevant facts with metadata
        """
        if self.index is None or len(self.facts) == 0:
            # Try to load existing index
            if not self.load_index():
                print("Index not built. Building now...")
                if not self.build_index():
                    return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).astype('float32')
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Retrieve facts
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.facts):
                fact = self.facts[idx].copy()
                fact['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                results.append(fact)
        
        return results
    
    def save_index(self):
        """Save FAISS index and facts to disk."""
        if self.index is None:
            return
        
        # Save FAISS index
        index_file = os.path.join(VECTOR_STORE_DIR, "index.faiss")
        faiss.write_index(self.index, index_file)
        
        # Save facts metadata
        facts_file = os.path.join(VECTOR_STORE_DIR, "facts.json")
        with open(facts_file, 'w', encoding='utf-8') as f:
            json.dump(self.facts, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Saved index to {index_file}")
        print(f"[OK] Saved facts to {facts_file}")
    
    def load_index(self) -> bool:
        """Load FAISS index and facts from disk."""
        index_file = os.path.join(VECTOR_STORE_DIR, "index.faiss")
        facts_file = os.path.join(VECTOR_STORE_DIR, "facts.json")
        
        if not os.path.exists(index_file) or not os.path.exists(facts_file):
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_file)
            
            # Load facts
            with open(facts_file, 'r', encoding='utf-8') as f:
                self.facts = json.load(f)
            
            print(f"[OK] Loaded index with {len(self.facts)} facts")
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            "total_facts": len(self.facts) if self.facts else 0,
            "index_built": self.index is not None,
            "dimension": VECTOR_DIMENSION if self.index else None,
            "embedding_model": EMBEDDING_MODEL
        }


if __name__ == "__main__":
    # Test vector store
    vs = VectorStore()
    
    # Build index
    if vs.build_index():
        print("\n✓ Index built successfully")
        
        # Test search
        test_queries = [
            "What is the expense ratio?",
            "What is the minimum SIP amount?",
            "What is the exit load?",
            "What is the lock-in period for ELSS?",
            "What is the benchmark?"
        ]
        
        print("\n" + "="*60)
        print("Testing Semantic Search")
        print("="*60)
        
        for query in test_queries:
            results = vs.search(query, top_k=2)
            print(f"\nQuery: {query}")
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['fact']}")
                print(f"     Source: {result['source_url']}")
                print(f"     Similarity: {result.get('similarity_score', 0):.3f}")
        
        # Stats
        print("\n" + "="*60)
        print("Vector Store Stats:")
        print("="*60)
        stats = vs.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")


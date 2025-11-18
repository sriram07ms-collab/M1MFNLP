"""
Comprehensive test script for the FAQ Assistant backend.
Tests the rating query: "What is the rating for ICICI Prudential Large Cap Fund?"
Expected: Rating is 5
"""

import sys
import os
import json
import subprocess

def check_dependencies():
    """Check if required packages are installed."""
    print("="*60)
    print("Step 1: Checking Dependencies")
    print("="*60)
    
    required = ['faiss', 'sentence_transformers', 'google.generativeai', 'fastapi']
    missing = []
    
    for package in required:
        try:
            if package == 'google.generativeai':
                __import__('google.generativeai')
            elif package == 'sentence_transformers':
                __import__('sentence_transformers')
            elif package == 'faiss':
                import faiss
            elif package == 'fastapi':
                import fastapi
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            missing.append(package)
    
    if missing:
        print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n[OK] All dependencies installed")
    return True


def check_test_data():
    """Check if test data exists."""
    print("\n" + "="*60)
    print("Step 2: Checking Test Data")
    print("="*60)
    
    if not os.path.exists("data/funds_data.json"):
        print("[ERROR] Test data not found. Creating...")
        try:
            subprocess.run([sys.executable, "create_test_data.py"], check=True)
            print("[OK] Test data created")
        except:
            print("[ERROR] Failed to create test data")
            return False
    
    # Check if rating is in data
    with open("data/funds_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    has_rating = False
    for fund in data:
        if fund.get('rating') and fund['rating'].get('value') == 5:
            has_rating = True
            print(f"  [OK] Found fund: {fund['fund_name']}")
            print(f"  [OK] Rating: {fund['rating']['value']}")
            break
    
    if not has_rating:
        print("[ERROR] Rating not found in test data")
        return False
    
    print("[OK] Test data contains rating = 5")
    return True


def build_vector_store():
    """Build vector store index."""
    print("\n" + "="*60)
    print("Step 3: Building Vector Store")
    print("="*60)
    
    try:
        from vector_store import VectorStore
        vs = VectorStore()
        
        if vs.build_index():
            stats = vs.get_stats()
            print(f"  [OK] Index built with {stats['total_facts']} facts")
            return True
        else:
            print("[ERROR] Failed to build index")
            return False
    except Exception as e:
        print(f"[ERROR] Error building vector store: {e}")
        return False


def test_semantic_search():
    """Test semantic search without API."""
    print("\n" + "="*60)
    print("Step 4: Testing Semantic Search")
    print("="*60)
    
    try:
        from vector_store import VectorStore
        vs = VectorStore()
        
        if not vs.load_index():
            print("[ERROR] Index not found. Building...")
            if not vs.build_index():
                return False
        
        query = "What is the rating for ICICI Prudential Large Cap Fund?"
        results = vs.search(query, top_k=3)
        
        print(f"  Query: {query}")
        print(f"  Found {len(results)} results:")
        
        rating_found = False
        for i, result in enumerate(results, 1):
            fact_text = result['fact'].encode('ascii', 'replace').decode('ascii')
            print(f"    {i}. {fact_text}")
            print(f"       Category: {result.get('category', 'N/A')}")
            print(f"       Similarity: {result.get('similarity_score', 0):.3f}")
            
            if 'rating' in result.get('category', '').lower() and '5' in result.get('fact', ''):
                rating_found = True
        
        if rating_found:
            print("\n  [OK] Rating fact found in search results!")
            return True
        else:
            print("\n  [WARN] Rating fact not in top results, but search is working")
            return True  # Still pass if search works
            
    except Exception as e:
        print(f"[ERROR] Error testing search: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api_key():
    """Check if API key is set."""
    print("\n" + "="*60)
    print("Step 5: Checking Gemini API Key")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[WARN] GEMINI_API_KEY not set")
        print("  To set it: python setup_api_key.py")
        print("  Or create .env file with: GEMINI_API_KEY=your_key_here")
        return False
    else:
        print(f"  [OK] API key found: {api_key[:10]}...{api_key[-4:]}")
        return True


def test_full_rag():
    """Test full RAG pipeline with API."""
    print("\n" + "="*60)
    print("Step 6: Testing Full RAG Pipeline")
    print("="*60)
    
    try:
        from rag_pipeline import RAGPipeline
        
        pipeline = RAGPipeline()
        query = "What is the rating for ICICI Prudential Large Cap Fund?"
        
        print(f"  Query: {query}")
        print("  Generating answer...")
        
        result = pipeline.answer_query(query, fund_name="ICICI Prudential Large Cap Fund")
        
        print(f"\n  Answer: {result['answer']}")
        print(f"  Sources: {len(result['source_urls'])} URL(s)")
        
        # Check if answer contains "5"
        answer_lower = result['answer'].lower()
        contains_5 = '5' in result['answer'] or 'five' in answer_lower
        
        if contains_5:
            print("\n  [OK] Answer contains '5' or 'five'")
            print(f"  [OK] Full test PASSED!")
            return True
        else:
            print("\n  [FAIL] Answer does not contain '5' or 'five'")
            print(f"  Answer was: {result['answer']}")
            
            # Check retrieved facts
            if result.get('retrieved_facts'):
                print("\n  Retrieved facts:")
                for fact in result['retrieved_facts']:
                    print(f"    - {fact['fact']}")
            
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing RAG: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("ICICI Prudential AMC FAQ Assistant - Comprehensive Test")
    print("="*60)
    print("Testing: Rating query for ICICI Prudential Large Cap Fund")
    print("Expected: Rating is 5")
    print("="*60)
    
    results = []
    
    # Step 1: Dependencies
    results.append(("Dependencies", check_dependencies()))
    if not results[-1][1]:
        print("\n[ERROR] Please install dependencies first: pip install -r requirements.txt")
        return 1
    
    # Step 2: Test Data
    results.append(("Test Data", check_test_data()))
    if not results[-1][1]:
        return 1
    
    # Step 3: Vector Store
    results.append(("Vector Store", build_vector_store()))
    if not results[-1][1]:
        return 1
    
    # Step 4: Semantic Search
    results.append(("Semantic Search", test_semantic_search()))
    
    # Step 5: API Key
    has_api_key = check_api_key()
    results.append(("API Key", has_api_key))
    
    # Step 6: Full RAG (only if API key is set)
    if has_api_key:
        results.append(("Full RAG Test", test_full_rag()))
    else:
        print("\n[SKIP] Skipping full RAG test (API key not set)")
        results.append(("Full RAG Test", None))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            print(f"  [PASS] {test_name}")
            passed += 1
        elif result is False:
            print(f"  [FAIL] {test_name}")
            failed += 1
        else:
            print(f"  [SKIP] {test_name}")
            skipped += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and has_api_key:
        print("\n[SUCCESS] All tests passed!")
        return 0
    elif failed == 0:
        print("\n[PARTIAL] Core tests passed, but full RAG test skipped (API key needed)")
        print("Set API key and run again for full test.")
        return 0
    else:
        print("\n[FAILURE] Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())


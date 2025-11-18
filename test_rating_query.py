"""
Test script specifically for rating query.
Tests: "What is the rating for ICICI Prudential Large Cap Fund?"
Expected: Rating is 5
"""

import requests
import json
import sys
from config import API_PORT

BASE_URL = f"http://localhost:{API_PORT}"


def test_rating_query():
    """Test the rating query."""
    print("="*60)
    print("Rating Query Test")
    print("="*60)
    
    # Test query
    query = "What is the rating for ICICI Prudential Large Cap Fund?"
    fund_name = "ICICI Prudential Large Cap Fund"
    
    print(f"\nQuery: {query}")
    print(f"Fund: {fund_name}")
    print(f"Expected Answer: Rating is 5")
    
    try:
        # Make POST request
        payload = {
            "query": query,
            "fund_name": fund_name
        }
        
        print(f"\nSending request to: {BASE_URL}/query")
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        print("\n" + "="*60)
        print("Response:")
        print("="*60)
        print(f"Answer: {data['answer']}")
        print(f"\nSource URLs ({len(data['source_urls'])}):")
        for url in data['source_urls']:
            print(f"  - {url}")
        
        if data.get('retrieved_facts'):
            print(f"\nRetrieved Facts ({len(data['retrieved_facts'])}):")
            for i, fact in enumerate(data['retrieved_facts'], 1):
                print(f"  {i}. {fact['fact']}")
                print(f"     Category: {fact.get('category', 'N/A')}")
                print(f"     Similarity: {fact.get('similarity_score', 0):.3f}")
        
        # Check if answer contains "5" or "five"
        answer_lower = data['answer'].lower()
        contains_5 = '5' in data['answer'] or 'five' in answer_lower
        
        print("\n" + "="*60)
        print("Validation:")
        print("="*60)
        
        if contains_5:
            print("✓ PASS: Answer contains '5' or 'five'")
            print(f"  Answer: {data['answer']}")
            return True
        else:
            print("✗ FAIL: Answer does not contain '5' or 'five'")
            print(f"  Answer: {data['answer']}")
            print("\nChecking retrieved facts for rating...")
            
            # Check retrieved facts
            rating_found = False
            for fact in data.get('retrieved_facts', []):
                if 'rating' in fact.get('category', '').lower() or '5' in fact.get('fact', ''):
                    print(f"  Found rating fact: {fact['fact']}")
                    rating_found = True
            
            if not rating_found:
                print("  ✗ No rating fact found in retrieved facts")
                print("\nPossible issues:")
                print("  1. Rating not extracted during scraping")
                print("  2. Rating not in RAG data")
                print("  3. Vector store needs rebuilding")
            
            return False
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to API server")
        print("  Make sure the server is running:")
        print("    python api.py")
        return False
    except requests.exceptions.Timeout:
        print("\n✗ ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_first():
    """Test health endpoint first."""
    print("\n[Pre-check] Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        
        if health['status'] == 'healthy':
            print("  ✓ API is healthy")
            return True
        else:
            print(f"  ⚠ API status: {health['status']}")
            print(f"  Message: {health['message']}")
            return False
    except Exception as e:
        print(f"  ✗ Health check failed: {e}")
        return False


if __name__ == "__main__":
    print("ICICI Prudential AMC FAQ Assistant - Rating Query Test")
    print("="*60)
    
    # Pre-check
    if not test_health_first():
        print("\n⚠ API may not be ready, but continuing test...")
    
    # Run test
    success = test_rating_query()
    
    print("\n" + "="*60)
    if success:
        print("✓ TEST PASSED")
    else:
        print("✗ TEST FAILED")
        print("\nTroubleshooting:")
        print("1. Make sure you've scraped the data: python main.py")
        print("2. Make sure rating is extracted (check data/funds_data.json)")
        print("3. Rebuild vector store: python setup_backend.py")
        print("4. Check if rating is in RAG data: data/rag_data.json")
    print("="*60)
    
    sys.exit(0 if success else 1)



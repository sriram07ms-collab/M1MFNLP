"""
Test script to run 3 different queries against the FAQ Assistant API.
"""

import requests
import json
import time
from config import API_PORT

BASE_URL = f"http://localhost:{API_PORT}"

def test_query(query, fund_name=None):
    """Test a single query."""
    print("\n" + "="*70)
    print(f"Query: {query}")
    if fund_name:
        print(f"Fund: {fund_name}")
    print("="*70)
    
    try:
        payload = {
            "query": query,
        }
        if fund_name:
            payload["fund_name"] = fund_name
        
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        print(f"\nAnswer:")
        # Handle Unicode for Windows console
        answer_text = data['answer'].encode('ascii', 'replace').decode('ascii')
        print(f"  {answer_text}")
        
        print(f"\nSource URLs ({len(data['source_urls'])}):")
        for url in data['source_urls']:
            print(f"  - {url}")
        
        if data.get('retrieved_facts'):
            print(f"\nRetrieved Facts ({len(data['retrieved_facts'])}):")
            for i, fact in enumerate(data['retrieved_facts'], 1):
                fact_text = fact['fact'].encode('ascii', 'replace').decode('ascii')
                print(f"  {i}. {fact_text}")
                print(f"     Category: {fact.get('category', 'N/A')}")
        
        print(f"\nModel: {data.get('model', 'N/A')}")
        print(f"Context Used: {data.get('context_used', 0)} facts")
        if data.get('fallback_used'):
            print(f"Fallback Used: Yes (LLM unavailable)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to API server")
        print("Make sure the server is running: python api.py")
        return False
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def main():
    """Run 3 test queries."""
    print("="*70)
    print("ICICI Prudential AMC FAQ Assistant - Query Testing")
    print("="*70)
    
    # Wait for server to be ready
    print("\nChecking API server...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                health = response.json()
                print(f"[OK] Server is ready (Status: {health.get('status', 'unknown')})")
                break
        except:
            if i < max_retries - 1:
                print(f"Waiting for server... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("[ERROR] Server not responding. Please start it with: python api.py")
                return
    
    # Test queries
    queries = [
        {
            "query": "What is the rating for ICICI Prudential Large Cap Fund?",
            "fund_name": "ICICI Prudential Large Cap Fund",
            "description": "Test 1: Rating Query (Expected: Rating is 5)"
        },
        {
            "query": "What is the expense ratio?",
            "fund_name": "ICICI Prudential Large Cap Fund",
            "description": "Test 2: Expense Ratio Query"
        },
        {
            "query": "What is the minimum SIP amount and exit load?",
            "fund_name": None,
            "description": "Test 3: Multiple Information Query"
        }
    ]
    
    results = []
    for i, test in enumerate(queries, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST {i}: {test['description']}")
        print(f"{'#'*70}")
        success = test_query(test['query'], test.get('fund_name'))
        results.append((test['description'], success))
        time.sleep(1)  # Small delay between queries
    
    # Summary
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {desc}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All queries tested successfully!")
    else:
        print("\n[WARNING] Some queries failed")


if __name__ == "__main__":
    main()


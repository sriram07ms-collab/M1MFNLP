"""
Test script for the backend API.
Tests all endpoints and functionality.
"""

import requests
import json
import time
from config import API_PORT

BASE_URL = f"http://localhost:{API_PORT}"


def test_health():
    """Test health check endpoint."""
    print("\n[1] Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Status: {data['status']}")
        print(f"  ✓ Gemini Connected: {data['gemini_connected']}")
        print(f"  ✓ Vector Store Facts: {data['vector_store_stats']['total_facts']}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_funds():
    """Test funds list endpoint."""
    print("\n[2] Testing Funds List...")
    try:
        response = requests.get(f"{BASE_URL}/funds")
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Total Funds: {data['total']}")
        for fund in data['funds']:
            print(f"    - {fund}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_query_post():
    """Test query endpoint (POST)."""
    print("\n[3] Testing Query (POST)...")
    try:
        payload = {
            "query": "What is the expense ratio?",
            "fund_name": "ICICI Prudential Large Cap Fund"
        }
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Answer: {data['answer'][:100]}...")
        print(f"  ✓ Sources: {len(data['source_urls'])} URL(s)")
        print(f"  ✓ Context Used: {data['context_used']} fact(s)")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_query_get():
    """Test query endpoint (GET)."""
    print("\n[4] Testing Query (GET)...")
    try:
        params = {"q": "What is the minimum SIP amount?"}
        response = requests.get(f"{BASE_URL}/query", params=params)
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Answer: {data['answer'][:100]}...")
        print(f"  ✓ Sources: {len(data['source_urls'])} URL(s)")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_multiple_queries():
    """Test multiple different queries."""
    print("\n[5] Testing Multiple Queries...")
    queries = [
        "What is the exit load?",
        "What is the lock-in period?",
        "What is the benchmark?",
        "How can I download statements?"
    ]
    
    success_count = 0
    for query in queries:
        try:
            params = {"q": query}
            response = requests.get(f"{BASE_URL}/query", params=params)
            response.raise_for_status()
            data = response.json()
            print(f"  ✓ Q: {query}")
            print(f"    A: {data['answer'][:80]}...")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Q: {query} - Failed: {e}")
    
    print(f"\n  Results: {success_count}/{len(queries)} queries successful")
    return success_count == len(queries)


def main():
    """Run all tests."""
    print("="*60)
    print("Backend API Test Suite")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure the server is running (python api.py)")
    
    # Wait a bit for server to be ready
    print("\nWaiting for server...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Funds List", test_funds),
        ("Query (POST)", test_query_post),
        ("Query (GET)", test_query_get),
        ("Multiple Queries", test_multiple_queries),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())



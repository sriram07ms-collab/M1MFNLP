"""Test fallback directly without API server."""

from rag_pipeline import RAGPipeline

print("Testing Fallback Mechanism")
print("="*60)

pipeline = RAGPipeline()

# Test query
query = "What is the expense ratio?"
print(f"\nQuery: {query}")

try:
    result = pipeline.answer_query(query, fund_name="ICICI Prudential Large Cap Fund")
    
    print(f"\nAnswer:")
    # Handle Unicode for Windows console
    answer_text = result['answer'].encode('ascii', 'replace').decode('ascii')
    print(answer_text)
    print(f"\nModel: {result.get('model')}")
    print(f"Fallback Used: {result.get('fallback_used', False)}")
    print(f"Source URLs: {len(result.get('source_urls', []))}")
    if result.get('source_urls'):
        for url in result['source_urls']:
            print(f"  - {url}")
    
    if result.get('fallback_used'):
        print("\n[SUCCESS] Fallback mechanism is working!")
    else:
        print("\n[INFO] LLM generation worked (no fallback needed)")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()


"""
RAG (Retrieval-Augmented Generation) Pipeline.
Combines vector search with LLM generation.
"""

import re
from typing import Dict, List, Optional
from vector_store import VectorStore
from gemini_client import GeminiClient
from config import TOP_K_RESULTS


class RAGPipeline:
    """RAG pipeline for FAQ answering."""
    
    def __init__(self):
        """Initialize RAG pipeline with vector store and LLM client."""
        self.vector_store = VectorStore()
        self.llm_client = GeminiClient()
        
        # Ensure index is built
        if not self.vector_store.index:
            print("Building vector store index...")
            self.vector_store.build_index()
    
    def answer_query(self, query: str, fund_name: Optional[str] = None) -> Dict:
        """
        Answer a query using RAG pipeline.
        
        Args:
            query: User's question
            fund_name: Optional fund name to filter results
        
        Returns:
            Dict with answer, sources, and metadata
        """
        # Step 0: Check if query is asking for investment advice
        if self._is_investment_advice_query(query):
            return self._refuse_investment_advice()
        
        # Step 1: Retrieve relevant facts
        retrieved_facts = self.vector_store.search(query, top_k=TOP_K_RESULTS)
        
        if not retrieved_facts:
            return {
                "answer": "I don't have information about that in my knowledge base. Please check the official ICICI Prudential AMC website for more details.",
                "source_urls": [],
                "context_used": 0,
                "retrieved_facts": []
            }
        
        # Step 2: Filter by fund name if provided
        if fund_name:
            filtered_facts = [
                f for f in retrieved_facts
                if fund_name.lower() in f.get('fund_name', '').lower()
            ]
            if filtered_facts:
                retrieved_facts = filtered_facts
        
        # Step 3: Generate answer using LLM (with fallback to facts)
        try:
            result = self.llm_client.generate_answer(
                query=query,
                context_facts=retrieved_facts,
                fund_name=fund_name
            )
        except Exception as e:
            # Fallback: Generate answer from retrieved facts when LLM fails
            result = self._generate_fallback_answer(query, retrieved_facts, fund_name, str(e))
        
        # Step 4: Add retrieved facts for transparency
        result['retrieved_facts'] = [
            {
                'fact': f['fact'],
                'category': f.get('category', ''),
                'source_url': f.get('source_url', ''),
                'similarity_score': f.get('similarity_score', 0)
            }
            for f in retrieved_facts
        ]
        
        return result
    
    def _generate_fallback_answer(self, query: str, facts: List[Dict], fund_name: Optional[str], error: str) -> Dict:
        """
        Generate a fallback answer from retrieved facts when LLM fails.
        Extracts specific values based on query intent.
        """
        # Extract source URLs
        source_urls = list(set(f.get('source_url', '') for f in facts if f.get('source_url')))
        
        # Detect query intent and extract specific answer
        query_lower = query.lower()
        answer = self._extract_specific_answer(query_lower, facts, fund_name)
        
        # If no specific answer found, use the most relevant fact
        if not answer:
            # Find the most relevant fact (highest similarity score)
            if facts:
                best_fact = max(facts, key=lambda f: f.get('similarity_score', 0))
                answer = self._extract_value_from_fact(best_fact['fact'], best_fact.get('category', ''))
                if not answer:
                    answer = best_fact['fact']
            else:
                answer = "I don't have that information in my knowledge base."
        
        return {
            "answer": answer,
            "source_urls": source_urls,
            "context_used": len(facts),
            "model": "fallback (facts-based)",
            "llm_error": error,
            "fallback_used": True
        }
    
    def _extract_specific_answer(self, query_lower: str, facts: List[Dict], fund_name: Optional[str]) -> str:
        """
        Extract specific answer based on query intent.
        Returns only the relevant value, not all facts.
        """
        # Map query patterns to categories
        query_patterns = {
            'rating': ['rating', 'rate', 'star', 'grade'],
            'expense_ratio': ['expense ratio', 'expense', 'charges', 'fee', 'cost'],
            'minimum_sip': ['minimum sip', 'min sip', 'sip amount', 'minimum investment', 'min investment'],
            'exit_load': ['exit load', 'redemption', 'withdrawal', 'exit charge'],
            'riskometer': ['risk', 'riskometer', 'risk level'],
            'benchmark': ['benchmark', 'index'],
            'lock_in': ['lock in', 'lock-in', 'lockin period'],
            'statement_download': ['statement', 'download', 'account statement']
        }
        
        # Find matching category
        matched_category = None
        for category, patterns in query_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                matched_category = category
                break
        
        # If no specific category matched, try to find most relevant fact
        if not matched_category:
            if facts:
                best_fact = max(facts, key=lambda f: f.get('similarity_score', 0))
                return self._extract_value_from_fact(best_fact['fact'], best_fact.get('category', ''))
            return ""
        
        # Find facts matching the category
        matching_facts = [f for f in facts if f.get('category') == matched_category]
        
        if not matching_facts:
            return ""
        
        # Use the fact with highest similarity score
        best_fact = max(matching_facts, key=lambda f: f.get('similarity_score', 0))
        
        # Extract just the value
        return self._extract_value_from_fact(best_fact['fact'], matched_category)
    
    def _extract_value_from_fact(self, fact_text: str, category: str) -> str:
        """
        Extract just the value from a fact string.
        Examples:
        - "Rating: 5" -> "5"
        - "Minimum SIP: ₹100" -> "100"
        - "Expense ratio: 0.85%" -> "0.85%"
        """
        # Remove category label and extract value
        fact_lower = fact_text.lower()
        
        # For rating: extract number
        if category == 'rating':
            match = re.search(r'(\d+)', fact_text)
            if match:
                return match.group(1)
        
        # For minimum SIP: extract number (with or without currency)
        elif category == 'minimum_sip':
            # Match ₹100 or 100 or ₹ 100
            match = re.search(r'[₹]?\s*(\d+)', fact_text)
            if match:
                return match.group(1)
        
        # For expense ratio: extract percentage
        elif category == 'expense_ratio':
            # Match 0.85% or 0.85 %
            match = re.search(r'(\d+\.?\d*)\s*%', fact_text)
            if match:
                return match.group(1) + "%"
        
        # For other categories, try to extract after colon
        if ':' in fact_text:
            value = fact_text.split(':', 1)[1].strip()
            # Remove currency symbols if present but keep the number
            if '₹' in value:
                value = value.replace('₹', '').strip()
            return value
        
        return fact_text
    
    def _is_investment_advice_query(self, query: str) -> bool:
        """
        Detect if query is asking for investment advice.
        """
        query_lower = query.lower()
        
        # Patterns that indicate investment advice requests
        advice_patterns = [
            'should i',
            'should i buy',
            'should i sell',
            'should i invest',
            'is it good to',
            'is it safe to',
            'is it worth',
            'recommend',
            'recommendation',
            'what should i',
            'which fund should',
            'which is better',
            'which is best',
            'advice',
            'opinion',
            'portfolio',
            'what to invest',
            'where to invest',
            'how much to invest',
            'when to buy',
            'when to sell'
        ]
        
        return any(pattern in query_lower for pattern in advice_patterns)
    
    def _refuse_investment_advice(self) -> Dict:
        """
        Return a polite refusal for investment advice queries.
        """
        return {
            "answer": "I can only provide factual information about ICICI Prudential mutual funds. I cannot provide investment advice, recommendations, or opinions about whether you should buy, sell, or invest in any fund.\n\nFor investment guidance, please consult with a qualified financial advisor or visit the official ICICI Prudential AMC website: https://www.icicipruamc.com/",
            "source_urls": ["https://www.icicipruamc.com/"],
            "context_used": 0,
            "retrieved_facts": [],
            "model": "facts-only",
            "advice_refused": True
        }
    
    def get_available_funds(self) -> List[str]:
        """Get list of available fund names in the knowledge base."""
        if not self.vector_store.facts:
            return []
        
        fund_names = set()
        for fact in self.vector_store.facts:
            fund_name = fact.get('fund_name', '')
            if fund_name:
                fund_names.add(fund_name)
        
        return sorted(list(fund_names))
    
    def rebuild_index(self) -> bool:
        """Rebuild the vector store index."""
        return self.vector_store.build_index()


if __name__ == "__main__":
    # Test RAG pipeline
    print("Initializing RAG Pipeline...")
    pipeline = RAGPipeline()
    
    print("\n" + "="*60)
    print("Available Funds:")
    print("="*60)
    funds = pipeline.get_available_funds()
    for fund in funds:
        print(f"  - {fund}")
    
    print("\n" + "="*60)
    print("Testing FAQ Queries")
    print("="*60)
    
    test_queries = [
        "What is the expense ratio for ICICI Prudential Large Cap Fund?",
        "What is the minimum SIP amount?",
        "What is the exit load?",
        "What is the lock-in period?",
        "What is the benchmark?",
        "How can I download statements?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = pipeline.answer_query(query)
        
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources ({len(result['source_urls'])}):")
        for url in result['source_urls']:
            print(f"  - {url}")
        
        if result.get('retrieved_facts'):
            print(f"\nRetrieved Facts ({len(result['retrieved_facts'])}):")
            for i, fact in enumerate(result['retrieved_facts'], 1):
                print(f"  {i}. {fact['fact']} (similarity: {fact.get('similarity_score', 0):.3f})")


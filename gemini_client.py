"""
Gemini LLM client for FAQ Assistant.
Uses Gemini 2.0 Flash model for generating answers.
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_CONTEXT_LENGTH


class GeminiClient:
    """Client for interacting with Gemini 2.0 Flash model."""
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        from config import validate_gemini_key
        validate_gemini_key()  # Validate before using
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.generation_config = {
            "temperature": 0.3,  # Lower temperature for factual answers
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 500,  # Limit response length
        }
    
    def generate_answer(
        self,
        query: str,
        context_facts: List[Dict],
        fund_name: Optional[str] = None
    ) -> Dict:
        """
        Generate answer using RAG (Retrieval-Augmented Generation).
        
        Args:
            query: User's question
            context_facts: List of relevant facts with source URLs
            fund_name: Optional fund name for context
        
        Returns:
            Dict with answer and source URLs
        """
        # Build context from facts
        context_parts = []
        source_urls = set()
        
        for fact in context_facts:
            fact_text = fact.get('fact', '')
            source_url = fact.get('source_url', '')
            category = fact.get('category', '')
            
            context_parts.append(f"- {fact_text}")
            if source_url:
                source_urls.add(source_url)
        
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = self._build_prompt(query, context, fund_name)
        
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            answer = response.text.strip()
            
            return {
                "answer": answer,
                "source_urls": list(source_urls),
                "context_used": len(context_facts),
                "model": GEMINI_MODEL
            }
            
        except Exception as e:
            # Raise exception so RAG pipeline can catch it and use fallback
            # Don't return error message as answer
            error_msg = str(e)
            # Check if it's a quota/rate limit error
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                raise Exception("QUOTA_ERROR")
            else:
                raise Exception(f"API_ERROR: {error_msg}")
    
    def _build_prompt(self, query: str, context: str, fund_name: Optional[str] = None) -> str:
        """Build the prompt for Gemini model."""
        
        fund_context = ""
        if fund_name:
            fund_context = f"\nFund: {fund_name}\n"
        
        prompt = f"""You are a helpful FAQ assistant for ICICI Prudential AMC mutual funds. 
Your role is to answer factual questions about ICICI Prudential mutual funds using ONLY the provided information.

IMPORTANT RULES:
1. Answer ONLY using the facts provided below
2. Do NOT provide any financial advice or recommendations
3. Do NOT make up information not in the provided facts
4. Keep answers concise and factual - extract just the specific value when asked
5. If the information is not in the provided facts, say "I don't have that information in my knowledge base"
6. Always be accurate and cite that the information comes from official sources
7. If asked for investment advice (e.g., "should I buy/sell?"), politely refuse and direct to official resources

INVESTMENT ADVICE REFUSAL:
If the question asks for advice, recommendations, or opinions (e.g., "Should I buy?", "Is it good to invest?", "What should I do?"), respond with:
"I can only provide factual information about ICICI Prudential mutual funds. I cannot provide investment advice, recommendations, or opinions. For investment guidance, please consult with a qualified financial advisor or visit the official ICICI Prudential AMC website: https://www.icicipruamc.com/"

ANSWER FORMAT:
- For specific values (rating, expense ratio, minimum SIP), extract just the number/value
- Example: If asked "What is the rating?" and fact says "Rating: 5", answer "5"
- Example: If asked "What is the expense ratio?" and fact says "Expense ratio: 0.85%", answer "0.85%"
- Example: If asked "What is the minimum SIP?" and fact says "Minimum SIP: ₹100", answer "100"

{fund_context}
Relevant Facts:
{context}

Question: {query}

Answer (factual, concise, no advice, extract specific value if applicable):"""
        
        return prompt
    
    def test_connection(self) -> bool:
        """Test connection to Gemini API."""
        try:
            test_response = self.model.generate_content(
                "Say 'Hello' if you can read this.",
                generation_config={"max_output_tokens": 10}
            )
            return test_response.text is not None
        except Exception as e:
            print(f"Gemini API connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Test the Gemini client
    client = GeminiClient()
    
    if client.test_connection():
        print("✓ Gemini API connection successful")
        
        # Test with sample data
        test_facts = [
            {
                "fact": "Expense ratio: 0.85%",
                "source_url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
                "category": "expense_ratio"
            }
        ]
        
        result = client.generate_answer(
            "What is the expense ratio?",
            test_facts,
            "ICICI Prudential Large Cap Fund"
        )
        
        print(f"\nAnswer: {result['answer']}")
        print(f"Sources: {result['source_urls']}")
    else:
        print("✗ Gemini API connection failed")


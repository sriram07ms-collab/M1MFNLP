"""
FastAPI backend for ICICI Prudential AMC FAQ Assistant.
Provides REST API endpoints for querying fund information.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from rag_pipeline import RAGPipeline
from config import API_DEBUG
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="ICICI Prudential AMC FAQ Assistant API",
    description="FAQ Assistant for ICICI Prudential Mutual Funds using RAG with Gemini 2.0 Flash",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    # Mount static files (CSS, JS, etc.)
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML."""
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found"}
    
    # Serve CSS and JS files directly
    @app.get("/styles.css")
    async def serve_css():
        css_path = os.path.join(frontend_dir, "styles.css")
        if os.path.exists(css_path):
            return FileResponse(css_path, media_type="text/css")
        raise HTTPException(status_code=404, detail="CSS file not found")
    
    @app.get("/app.js")
    async def serve_js():
        js_path = os.path.join(frontend_dir, "app.js")
        if os.path.exists(js_path):
            return FileResponse(js_path, media_type="application/javascript")
        raise HTTPException(status_code=404, detail="JS file not found")

# Initialize RAG pipeline
rag_pipeline = None

def get_rag_pipeline():
    """Get or initialize RAG pipeline (lazy loading)."""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline()
    return rag_pipeline


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for FAQ query."""
    query: str = Field(..., description="User's question about ICICI Prudential funds")
    fund_name: Optional[str] = Field(None, description="Optional: Specific fund name to filter results")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "What is the expense ratio?",
                "fund_name": "ICICI Prudential Large Cap Fund"
            }
        }
    )


class SourceURL(BaseModel):
    """Source URL model."""
    url: str
    fund_name: Optional[str] = None


class RetrievedFact(BaseModel):
    """Retrieved fact model."""
    fact: str
    category: str
    source_url: str
    similarity_score: float


class QueryResponse(BaseModel):
    """Response model for FAQ query."""
    answer: str = Field(..., description="Generated answer")
    source_urls: List[str] = Field(..., description="List of source URLs")
    context_used: int = Field(..., description="Number of facts used as context")
    model: str = Field(..., description="LLM model used")
    retrieved_facts: Optional[List[RetrievedFact]] = Field(None, description="Retrieved facts for transparency")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    vector_store_stats: dict
    gemini_connected: bool


class FundsResponse(BaseModel):
    """Available funds response."""
    funds: List[str]
    total: int


# API Endpoints

@app.get("/api", tags=["Root"])
async def api_info():
    """API information endpoint."""
    return {
        "message": "ICICI Prudential AMC FAQ Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "funds": "/funds",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    pipeline = get_rag_pipeline()
    
    # Check Gemini connection
    gemini_connected = pipeline.llm_client.test_connection()
    
    # Get vector store stats
    stats = pipeline.vector_store.get_stats()
    
    status = "healthy" if gemini_connected and stats.get("index_built") else "degraded"
    message = "Service is operational" if status == "healthy" else "Service has issues"
    
    return HealthResponse(
        status=status,
        message=message,
        vector_store_stats=stats,
        gemini_connected=gemini_connected
    )


@app.post("/query", response_model=QueryResponse, tags=["FAQ"])
async def answer_query(request: QueryRequest):
    """
    Answer a FAQ query using RAG pipeline.
    
    - **query**: User's question about ICICI Prudential funds
    - **fund_name**: Optional fund name to filter results
    """
    try:
        pipeline = get_rag_pipeline()
        
        result = pipeline.answer_query(
            query=request.query,
            fund_name=request.fund_name
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/query", response_model=QueryResponse, tags=["FAQ"])
async def answer_query_get(
    q: str = Query(..., description="User's question"),
    fund_name: Optional[str] = Query(None, description="Optional fund name")
):
    """
    Answer a FAQ query using GET method (for simple testing).
    """
    try:
        pipeline = get_rag_pipeline()
        
        result = pipeline.answer_query(
            query=q,
            fund_name=fund_name
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/funds", response_model=FundsResponse, tags=["Funds"])
async def get_available_funds():
    """Get list of available funds in the knowledge base."""
    try:
        pipeline = get_rag_pipeline()
        funds = pipeline.get_available_funds()
        
        return FundsResponse(
            funds=funds,
            total=len(funds)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving funds: {str(e)}"
        )


@app.post("/rebuild-index", tags=["Admin"])
async def rebuild_index():
    """Rebuild the vector store index (admin endpoint)."""
    try:
        pipeline = get_rag_pipeline()
        success = pipeline.rebuild_index()
        
        if success:
            return {
                "status": "success",
                "message": "Vector store index rebuilt successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to rebuild index"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rebuilding index: {str(e)}"
        )


if __name__ == "__main__":
    from config import API_HOST, API_PORT
    
    uvicorn.run(
        "api:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG
    )


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedding_service import EmbeddingService
from typing import List, Optional

router = APIRouter()
embedding_service = EmbeddingService()

class SearchRequest(BaseModel):
    query: str
    knowledge_base_id: str
    top_k: int = 5
    embedding_model: str = "openai"

@router.post("/search")
async def search_embeddings(request: SearchRequest):
    """Search for similar documents in a knowledge base"""
    try:
        results = embedding_service.search_similar(
            query=request.query,
            knowledge_base_id=request.knowledge_base_id,
            top_k=request.top_k,
            embedding_model=request.embedding_model
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching embeddings: {str(e)}")

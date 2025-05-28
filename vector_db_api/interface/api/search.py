"""
Search API endpoints for vector similarity search within libraries.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vector_db_api.infrastructure.repo.in_memory_repository import repo_container


class SearchRequest(BaseModel):
    """Request model for vector similarity search."""
    query_vector: List[float]
    top_k: int = 10


class SearchResult(BaseModel):
    """Individual search result with chunk and similarity score."""
    chunk_id: UUID
    vector: List[float]
    metadata: dict
    document_id: UUID
    similarity_score: float


class SearchResponse(BaseModel):
    """Response model for search operations."""
    library_id: UUID
    query_vector: List[float]
    top_k: int
    results: List[SearchResult]
    total_chunks_searched: int


router = APIRouter()


@router.post("/libraries/{library_id}/search", response_model=SearchResponse)
async def search_library(library_id: UUID, request: SearchRequest) -> SearchResponse:
    """
    Search for similar chunks within a library using vector similarity.
    
    Args:
        library_id: Unique identifier of the library to search in
        request: Search request with query vector and optional top_k limit
        
    Returns:
        Search results with chunks ranked by similarity
        
    Raises:
        HTTPException: If library is not found or if query vector is invalid
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Validate query vector
    if not request.query_vector:
        raise HTTPException(status_code=422, detail="Query vector cannot be empty")
    
    # Perform vector similarity search
    try:
        search_results = await repo_container.chunk_repo.search_by_vector_similarity(
            library_id=library_id,
            query_vector=request.query_vector,
            top_k=request.top_k
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Search error: {str(e)}")
    
    # Get total chunks in library for metadata
    all_chunks = await repo_container.chunk_repo.list_by_library_id(library_id)
    total_chunks_searched = len(all_chunks)
    
    # Convert results to response format
    results = [
        SearchResult(
            chunk_id=chunk.id,
            vector=chunk.vector,
            metadata=chunk.metadata,
            document_id=chunk.document_id,
            similarity_score=similarity_score
        )
        for chunk, similarity_score in search_results
        if chunk.document_id is not None  # Ensure chunk belongs to a document
    ]
    
    return SearchResponse(
        library_id=library_id,
        query_vector=request.query_vector,
        top_k=request.top_k,
        results=results,
        total_chunks_searched=total_chunks_searched
    ) 

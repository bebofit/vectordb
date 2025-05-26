"""
Chunks API endpoints for vector operations within libraries.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vector_db_api.domain.models.chunk import Chunk
from .libraries import libraries_store


class CreateChunkRequest(BaseModel):
    """Request model for creating a new chunk."""
    vector: List[float]
    metadata: dict = {}
    document_id: Optional[UUID] = None


class ChunkResponse(BaseModel):
    """Response model for chunk operations."""
    id: UUID
    vector: List[float]
    metadata: dict
    document_id: Optional[UUID] = None
    dimension: int


# In-memory storage for demonstration (will be replaced with proper repository)
chunks_store: dict[UUID, Chunk] = {}

router = APIRouter()


@router.post("/libraries/{library_id}/chunks", response_model=ChunkResponse)
async def create_chunk_in_library(library_id: UUID, request: CreateChunkRequest) -> ChunkResponse:
    """
    Create a new chunk within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        request: Chunk creation request with vector and metadata
        
    Returns:
        Created chunk with generated ID
        
    Raises:
        HTTPException: If library is not found
    """
    if library_id not in libraries_store:
        raise HTTPException(status_code=404, detail="Library not found")
    
    chunk = Chunk(
        vector=request.vector,
        metadata=request.metadata,
        document_id=request.document_id,
    )
    
    chunks_store[chunk.id] = chunk
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


@router.get("/libraries/{library_id}/chunks/{chunk_id}", response_model=ChunkResponse)
async def get_chunk_in_library(library_id: UUID, chunk_id: UUID) -> ChunkResponse:
    """
    Retrieve a chunk by its ID within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        chunk_id: Unique identifier of the chunk
        
    Returns:
        Chunk data
        
    Raises:
        HTTPException: If library or chunk is not found
    """
    if library_id not in libraries_store:
        raise HTTPException(status_code=404, detail="Library not found")
    
    if chunk_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    chunk = chunks_store[chunk_id]
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


@router.get("/libraries/{library_id}/chunks", response_model=List[ChunkResponse])
async def list_chunks_in_library(library_id: UUID) -> List[ChunkResponse]:
    """
    List all chunks in a specific library.
    
    Args:
        library_id: Unique identifier of the library
        
    Returns:
        List of chunks in the library
        
    Raises:
        HTTPException: If library is not found
    """
    if library_id not in libraries_store:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # For now, return all chunks (in a real implementation, we'd filter by library)
    return [
        ChunkResponse(
            id=chunk.id,
            vector=chunk.vector,
            metadata=chunk.metadata,
            document_id=chunk.document_id,
            dimension=chunk.dimension,
        )
        for chunk in chunks_store.values()
    ]


@router.put("/libraries/{library_id}/chunks/{chunk_id}", response_model=ChunkResponse)
async def update_chunk_in_library(
    library_id: UUID, 
    chunk_id: UUID, 
    request: CreateChunkRequest
) -> ChunkResponse:
    """
    Update a chunk within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        chunk_id: Unique identifier of the chunk
        request: Chunk update request
        
    Returns:
        Updated chunk data
        
    Raises:
        HTTPException: If library or chunk is not found
    """
    if library_id not in libraries_store:
        raise HTTPException(status_code=404, detail="Library not found")
    
    if chunk_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Update the chunk
    updated_chunk = Chunk(
        id=chunk_id,
        vector=request.vector,
        metadata=request.metadata,
        document_id=request.document_id,
    )
    
    chunks_store[chunk_id] = updated_chunk
    
    return ChunkResponse(
        id=updated_chunk.id,
        vector=updated_chunk.vector,
        metadata=updated_chunk.metadata,
        document_id=updated_chunk.document_id,
        dimension=updated_chunk.dimension,
    )


@router.delete("/libraries/{library_id}/chunks/{chunk_id}")
async def delete_chunk_in_library(library_id: UUID, chunk_id: UUID) -> dict:
    """
    Delete a chunk within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        chunk_id: Unique identifier of the chunk to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If library or chunk is not found
    """
    if library_id not in libraries_store:
        raise HTTPException(status_code=404, detail="Library not found")
    
    if chunk_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    del chunks_store[chunk_id]
    
    return {"message": "Chunk deleted successfully"}


# Keep the original chunk endpoints for backward compatibility
@router.post("/chunks", response_model=ChunkResponse)
async def create_chunk(request: CreateChunkRequest) -> ChunkResponse:
    """
    Create a new chunk (legacy endpoint).
    
    Args:
        request: Chunk creation request with vector and metadata
        
    Returns:
        Created chunk with generated ID
    """
    chunk = Chunk(
        vector=request.vector,
        metadata=request.metadata,
        document_id=request.document_id,
    )
    
    chunks_store[chunk.id] = chunk
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


@router.get("/chunks/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(chunk_id: UUID) -> ChunkResponse:
    """
    Retrieve a chunk by its ID (legacy endpoint).
    
    Args:
        chunk_id: Unique identifier of the chunk
        
    Returns:
        Chunk data
        
    Raises:
        HTTPException: If chunk is not found
    """
    if chunk_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    chunk = chunks_store[chunk_id]
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


@router.get("/chunks", response_model=List[ChunkResponse])
async def list_chunks() -> List[ChunkResponse]:
    """
    List all chunks (legacy endpoint).
    
    Returns:
        List of all chunks
    """
    return [
        ChunkResponse(
            id=chunk.id,
            vector=chunk.vector,
            metadata=chunk.metadata,
            document_id=chunk.document_id,
            dimension=chunk.dimension,
        )
        for chunk in chunks_store.values()
    ]


@router.delete("/chunks/{chunk_id}")
async def delete_chunk(chunk_id: UUID) -> dict:
    """
    Delete a chunk by its ID (legacy endpoint).
    
    Args:
        chunk_id: Unique identifier of the chunk to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If chunk is not found
    """
    if chunk_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    del chunks_store[chunk_id]
    
    return {"message": "Chunk deleted successfully"} 

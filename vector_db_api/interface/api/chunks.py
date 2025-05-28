"""
Chunks API endpoints for vector operations within libraries and documents.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vector_db_api.domain.models.chunk import Chunk
from vector_db_api.domain.models.document import Document
from vector_db_api.infrastructure.repo.in_memory_repository import repo_container


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


router = APIRouter()


@router.post("/libraries/{library_id}/documents/{document_id}/chunks", response_model=ChunkResponse)
async def create_chunk_in_document(
    library_id: UUID, 
    document_id: UUID, 
    request: CreateChunkRequest
) -> ChunkResponse:
    """
    Create a new chunk within a specific document in a library.
    
    Args:
        library_id: Unique identifier of the library
        document_id: Unique identifier of the document
        request: Chunk creation request with vector and metadata
        
    Returns:
        Created chunk with generated ID
        
    Raises:
        HTTPException: If library or document is not found
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Check if document exists and belongs to library
    document = await repo_container.document_repo.get_by_id(document_id)
    if not document or document.library_id != library_id:
        raise HTTPException(status_code=404, detail="Document not found in this library")
    
    # Create chunk
    chunk = Chunk(
        vector=request.vector,
        metadata=request.metadata,
        document_id=document_id,
    )
    
    # Save chunk
    chunk = await repo_container.chunk_repo.create(chunk)
    
    # Add chunk to document
    document.add_chunk_id(chunk.id)
    await repo_container.document_repo.update(document)
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


@router.post("/libraries/{library_id}/chunks", response_model=ChunkResponse)
async def create_chunk_in_library(library_id: UUID, request: CreateChunkRequest) -> ChunkResponse:
    """
    Create a new chunk within a library (creates a default document if needed).
    
    Args:
        library_id: Unique identifier of the library
        request: Chunk creation request with vector and metadata
        
    Returns:
        Created chunk with generated ID
        
    Raises:
        HTTPException: If library is not found
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Create or use a default document for this library
    documents = await repo_container.document_repo.list_by_library_id(library_id)
    default_doc = None
    
    # Look for an existing default document
    for doc in documents:
        if doc.title.startswith("Default Document"):
            default_doc = doc
            break
    
    # Create default document if none exists
    if not default_doc:
        default_doc = Document(
            title="Default Document",
            content="Auto-created document for direct chunk uploads",
            metadata={"auto_created": True},
            library_id=library_id,
        )
        default_doc = await repo_container.document_repo.create(default_doc)
        
        # Add document to library
        library.add_document_id(default_doc.id)
        await repo_container.library_repo.update(library)
    
    # Create chunk
    chunk = Chunk(
        vector=request.vector,
        metadata=request.metadata,
        document_id=default_doc.id,
    )
    
    # Save chunk
    chunk = await repo_container.chunk_repo.create(chunk)
    
    # Add chunk to document
    default_doc.add_chunk_id(chunk.id)
    await repo_container.document_repo.update(default_doc)
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


@router.get("/libraries/{library_id}/documents/{document_id}/chunks", response_model=List[ChunkResponse])
async def list_chunks_in_document(library_id: UUID, document_id: UUID) -> List[ChunkResponse]:
    """
    List all chunks in a specific document within a library.
    
    Args:
        library_id: Unique identifier of the library
        document_id: Unique identifier of the document
        
    Returns:
        List of chunks in the document
        
    Raises:
        HTTPException: If library or document is not found
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Check if document exists and belongs to library
    document = await repo_container.document_repo.get_by_id(document_id)
    if not document or document.library_id != library_id:
        raise HTTPException(status_code=404, detail="Document not found in this library")
    
    # Get chunks
    chunks = await repo_container.chunk_repo.list_by_document_id(document_id)
    
    return [
        ChunkResponse(
            id=chunk.id,
            vector=chunk.vector,
            metadata=chunk.metadata,
            document_id=chunk.document_id,
            dimension=chunk.dimension,
        )
        for chunk in chunks
    ]


@router.get("/libraries/{library_id}/chunks", response_model=List[ChunkResponse])
async def list_chunks_in_library(library_id: UUID) -> List[ChunkResponse]:
    """
    List all chunks in a specific library (across all documents).
    
    Args:
        library_id: Unique identifier of the library
        
    Returns:
        List of chunks in the library
        
    Raises:
        HTTPException: If library is not found
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get all chunks in the library
    chunks = await repo_container.chunk_repo.list_by_library_id(library_id)
    
    return [
        ChunkResponse(
            id=chunk.id,
            vector=chunk.vector,
            metadata=chunk.metadata,
            document_id=chunk.document_id,
            dimension=chunk.dimension,
        )
        for chunk in chunks
    ]


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
        HTTPException: If library or chunk is not found, or chunk doesn't belong to library
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get chunk
    chunk = await repo_container.chunk_repo.get_by_id(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Verify chunk belongs to this library (through its document)
    if chunk.document_id:
        document = await repo_container.document_repo.get_by_id(chunk.document_id)
        if not document or document.library_id != library_id:
            raise HTTPException(status_code=404, detail="Chunk not found in this library")
    else:
        raise HTTPException(status_code=404, detail="Chunk not found in this library")
    
    return ChunkResponse(
        id=chunk.id,
        vector=chunk.vector,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
        dimension=chunk.dimension,
    )


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
        HTTPException: If library or chunk is not found, or chunk doesn't belong to library
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get chunk
    chunk = await repo_container.chunk_repo.get_by_id(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Verify chunk belongs to this library (through its document)
    if chunk.document_id:
        document = await repo_container.document_repo.get_by_id(chunk.document_id)
        if not document or document.library_id != library_id:
            raise HTTPException(status_code=404, detail="Chunk not found in this library")
    else:
        raise HTTPException(status_code=404, detail="Chunk not found in this library")
    
    # Update the chunk
    updated_chunk = Chunk(
        id=chunk_id,
        vector=request.vector,
        metadata=request.metadata,
        document_id=chunk.document_id,  # Keep original document association
    )
    
    updated_chunk = await repo_container.chunk_repo.update(updated_chunk)
    
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
        HTTPException: If library or chunk is not found, or chunk doesn't belong to library
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get chunk
    chunk = await repo_container.chunk_repo.get_by_id(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Verify chunk belongs to this library (through its document)
    if chunk.document_id:
        document = await repo_container.document_repo.get_by_id(chunk.document_id)
        if not document or document.library_id != library_id:
            raise HTTPException(status_code=404, detail="Chunk not found in this library")
        
        # Remove chunk from document
        document.remove_chunk_id(chunk_id)
        await repo_container.document_repo.update(document)
    else:
        raise HTTPException(status_code=404, detail="Chunk not found in this library")
    
    # Delete chunk
    await repo_container.chunk_repo.delete(chunk_id)
    
    return {"message": "Chunk deleted successfully"}


# Legacy endpoints for backward compatibility
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
    
    chunk = await repo_container.chunk_repo.create(chunk)
    
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
    chunk = await repo_container.chunk_repo.get_by_id(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
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
    # This is a simplified implementation that gets all chunks from all libraries
    # In a real implementation, you might want to paginate or filter this
    libraries = await repo_container.library_repo.list_all()
    all_chunks = []
    
    for library in libraries:
        chunks = await repo_container.chunk_repo.list_by_library_id(library.id)
        all_chunks.extend(chunks)
    
    return [
        ChunkResponse(
            id=chunk.id,
            vector=chunk.vector,
            metadata=chunk.metadata,
            document_id=chunk.document_id,
            dimension=chunk.dimension,
        )
        for chunk in all_chunks
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
    chunk = await repo_container.chunk_repo.get_by_id(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Remove chunk from document if it belongs to one
    if chunk.document_id:
        document = await repo_container.document_repo.get_by_id(chunk.document_id)
        if document:
            document.remove_chunk_id(chunk_id)
            await repo_container.document_repo.update(document)
    
    await repo_container.chunk_repo.delete(chunk_id)
    
    return {"message": "Chunk deleted successfully"} 

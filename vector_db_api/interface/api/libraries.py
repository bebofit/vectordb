"""
Libraries API endpoints for managing vector libraries.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vector_db_api.domain.models.library import Library
from vector_db_api.infrastructure.repo.in_memory_repository import repo_container


class CreateLibraryRequest(BaseModel):
    """Request model for creating a new library."""
    name: str
    description: Optional[str] = None
    metadata: dict = {}


class UpdateLibraryRequest(BaseModel):
    """Request model for updating a library."""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class LibraryResponse(BaseModel):
    """Response model for library operations."""
    id: UUID
    name: str
    description: Optional[str] = None
    metadata: dict
    document_ids: List[UUID]
    document_count: int


router = APIRouter()


@router.post("/libraries", response_model=LibraryResponse)
async def create_library(request: CreateLibraryRequest) -> LibraryResponse:
    """
    Create a new library.
    
    Args:
        request: Library creation request with name, description, and metadata
        
    Returns:
        Created library with generated ID
    """
    library = Library(
        name=request.name,
        description=request.description,
        metadata=request.metadata,
    )
    
    library = await repo_container.library_repo.create(library)
    
    return LibraryResponse(
        id=library.id,
        name=library.name,
        description=library.description,
        metadata=library.metadata,
        document_ids=library.document_ids,
        document_count=library.document_count,
    )


@router.get("/libraries/{library_id}", response_model=LibraryResponse)
async def get_library(library_id: UUID) -> LibraryResponse:
    """
    Retrieve a library by its ID.
    
    Args:
        library_id: Unique identifier of the library
        
    Returns:
        Library data
        
    Raises:
        HTTPException: If library is not found
    """
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    return LibraryResponse(
        id=library.id,
        name=library.name,
        description=library.description,
        metadata=library.metadata,
        document_ids=library.document_ids,
        document_count=library.document_count,
    )


@router.get("/libraries", response_model=List[LibraryResponse])
async def list_libraries() -> List[LibraryResponse]:
    """
    List all libraries.
    
    Returns:
        List of all libraries
    """
    libraries = await repo_container.library_repo.list_all()
    
    return [
        LibraryResponse(
            id=library.id,
            name=library.name,
            description=library.description,
            metadata=library.metadata,
            document_ids=library.document_ids,
            document_count=library.document_count,
        )
        for library in libraries
    ]


@router.put("/libraries/{library_id}", response_model=LibraryResponse)
async def update_library(library_id: UUID, request: UpdateLibraryRequest) -> LibraryResponse:
    """
    Update a library by its ID.
    
    Args:
        library_id: Unique identifier of the library
        request: Library update request with optional fields
        
    Returns:
        Updated library data
        
    Raises:
        HTTPException: If library is not found
    """
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Update only provided fields
    if request.name is not None:
        library.name = request.name
    if request.description is not None:
        library.description = request.description
    if request.metadata is not None:
        library.metadata = request.metadata
    
    library = await repo_container.library_repo.update(library)
    
    return LibraryResponse(
        id=library.id,
        name=library.name,
        description=library.description,
        metadata=library.metadata,
        document_ids=library.document_ids,
        document_count=library.document_count,
    )


@router.delete("/libraries/{library_id}")
async def delete_library(library_id: UUID) -> dict:
    """
    Delete a library by its ID.
    
    Args:
        library_id: Unique identifier of the library to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If library is not found
    """
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Delete all documents and their chunks in the library
    documents = await repo_container.document_repo.list_by_library_id(library_id)
    for document in documents:
        # Delete all chunks in the document
        chunks = await repo_container.chunk_repo.list_by_document_id(document.id)
        for chunk in chunks:
            await repo_container.chunk_repo.delete(chunk.id)
        
        # Delete the document
        await repo_container.document_repo.delete(document.id)
    
    # Delete the library
    success = await repo_container.library_repo.delete(library_id)
    if not success:
        raise HTTPException(status_code=404, detail="Library not found")
    
    return {"message": "Library deleted successfully"} 

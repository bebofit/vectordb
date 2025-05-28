"""
Documents API endpoints for managing documents within libraries.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vector_db_api.domain.models.document import Document
from vector_db_api.infrastructure.repo.in_memory_repository import repo_container


class CreateDocumentRequest(BaseModel):
    """Request model for creating a new document."""
    title: str
    content: Optional[str] = None
    metadata: dict = {}


class UpdateDocumentRequest(BaseModel):
    """Request model for updating a document."""
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None


class DocumentResponse(BaseModel):
    """Response model for document operations."""
    id: UUID
    title: str
    content: Optional[str] = None
    metadata: dict
    chunk_ids: List[UUID]
    chunk_count: int
    library_id: Optional[UUID] = None


router = APIRouter()


@router.post("/libraries/{library_id}/documents", response_model=DocumentResponse)
async def create_document_in_library(library_id: UUID, request: CreateDocumentRequest) -> DocumentResponse:
    """
    Create a new document within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        request: Document creation request with title, content, and metadata
        
    Returns:
        Created document with generated ID
        
    Raises:
        HTTPException: If library is not found
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Create document
    document = Document(
        title=request.title,
        content=request.content,
        metadata=request.metadata,
        library_id=library_id,
    )
    
    # Save document
    document = await repo_container.document_repo.create(document)
    
    # Add document to library
    library.add_document_id(document.id)
    await repo_container.library_repo.update(library)
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        content=document.content,
        metadata=document.metadata,
        chunk_ids=document.chunk_ids,
        chunk_count=document.chunk_count,
        library_id=document.library_id,
    )


@router.get("/libraries/{library_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_document_in_library(library_id: UUID, document_id: UUID) -> DocumentResponse:
    """
    Retrieve a document by its ID within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        document_id: Unique identifier of the document
        
    Returns:
        Document data
        
    Raises:
        HTTPException: If library or document is not found, or document doesn't belong to library
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get document
    document = await repo_container.document_repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document belongs to library
    if document.library_id != library_id:
        raise HTTPException(status_code=404, detail="Document not found in this library")
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        content=document.content,
        metadata=document.metadata,
        chunk_ids=document.chunk_ids,
        chunk_count=document.chunk_count,
        library_id=document.library_id,
    )


@router.get("/libraries/{library_id}/documents", response_model=List[DocumentResponse])
async def list_documents_in_library(library_id: UUID) -> List[DocumentResponse]:
    """
    List all documents in a specific library.
    
    Args:
        library_id: Unique identifier of the library
        
    Returns:
        List of documents in the library
        
    Raises:
        HTTPException: If library is not found
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get documents
    documents = await repo_container.document_repo.list_by_library_id(library_id)
    
    return [
        DocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content,
            metadata=document.metadata,
            chunk_ids=document.chunk_ids,
            chunk_count=document.chunk_count,
            library_id=document.library_id,
        )
        for document in documents
    ]


@router.put("/libraries/{library_id}/documents/{document_id}", response_model=DocumentResponse)
async def update_document_in_library(
    library_id: UUID, 
    document_id: UUID, 
    request: UpdateDocumentRequest
) -> DocumentResponse:
    """
    Update a document within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        document_id: Unique identifier of the document
        request: Document update request with optional fields
        
    Returns:
        Updated document data
        
    Raises:
        HTTPException: If library or document is not found, or document doesn't belong to library
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get document
    document = await repo_container.document_repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document belongs to library
    if document.library_id != library_id:
        raise HTTPException(status_code=404, detail="Document not found in this library")
    
    # Update only provided fields
    if request.title is not None:
        document.title = request.title
    if request.content is not None:
        document.content = request.content
    if request.metadata is not None:
        document.metadata = request.metadata
    
    # Save updated document
    document = await repo_container.document_repo.update(document)
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        content=document.content,
        metadata=document.metadata,
        chunk_ids=document.chunk_ids,
        chunk_count=document.chunk_count,
        library_id=document.library_id,
    )


@router.delete("/libraries/{library_id}/documents/{document_id}")
async def delete_document_in_library(library_id: UUID, document_id: UUID) -> dict:
    """
    Delete a document within a specific library.
    
    Args:
        library_id: Unique identifier of the library
        document_id: Unique identifier of the document to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If library or document is not found, or document doesn't belong to library
    """
    # Check if library exists
    library = await repo_container.library_repo.get_by_id(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get document
    document = await repo_container.document_repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if document belongs to library
    if document.library_id != library_id:
        raise HTTPException(status_code=404, detail="Document not found in this library")
    
    # Delete all chunks in the document first
    chunks = await repo_container.chunk_repo.list_by_document_id(document_id)
    for chunk in chunks:
        await repo_container.chunk_repo.delete(chunk.id)
    
    # Remove document from library
    library.remove_document_id(document_id)
    await repo_container.library_repo.update(library)
    
    # Delete document
    await repo_container.document_repo.delete(document_id)
    
    return {"message": "Document deleted successfully"} 

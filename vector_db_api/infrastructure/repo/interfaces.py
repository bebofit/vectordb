"""
Repository interfaces for data access layer.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from vector_db_api.domain.models.library import Library
from vector_db_api.domain.models.document import Document
from vector_db_api.domain.models.chunk import Chunk


class LibraryRepository(ABC):
    """Abstract repository interface for library operations."""
    
    @abstractmethod
    async def create(self, library: Library) -> Library:
        """Create a new library."""
        pass
    
    @abstractmethod
    async def get_by_id(self, library_id: UUID) -> Optional[Library]:
        """Get library by ID."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Library]:
        """List all libraries."""
        pass
    
    @abstractmethod
    async def update(self, library: Library) -> Library:
        """Update an existing library."""
        pass
    
    @abstractmethod
    async def delete(self, library_id: UUID) -> bool:
        """Delete a library. Returns True if deleted, False if not found."""
        pass


class DocumentRepository(ABC):
    """Abstract repository interface for document operations."""
    
    @abstractmethod
    async def create(self, document: Document) -> Document:
        """Create a new document."""
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        pass
    
    @abstractmethod
    async def list_by_library_id(self, library_id: UUID) -> List[Document]:
        """List all documents in a library."""
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        """Update an existing document."""
        pass
    
    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        """Delete a document. Returns True if deleted, False if not found."""
        pass


class ChunkRepository(ABC):
    """Abstract repository interface for chunk operations."""
    
    @abstractmethod
    async def create(self, chunk: Chunk) -> Chunk:
        """Create a new chunk."""
        pass
    
    @abstractmethod
    async def get_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get chunk by ID."""
        pass
    
    @abstractmethod
    async def list_by_document_id(self, document_id: UUID) -> List[Chunk]:
        """List all chunks in a document."""
        pass
    
    @abstractmethod
    async def list_by_library_id(self, library_id: UUID) -> List[Chunk]:
        """List all chunks in a library (across all documents)."""
        pass
    
    @abstractmethod
    async def update(self, chunk: Chunk) -> Chunk:
        """Update an existing chunk."""
        pass
    
    @abstractmethod
    async def delete(self, chunk_id: UUID) -> bool:
        """Delete a chunk. Returns True if deleted, False if not found."""
        pass
    
    @abstractmethod
    async def search_by_vector_similarity(
        self, 
        library_id: UUID, 
        query_vector: List[float], 
        top_k: int = 10
    ) -> List[tuple[Chunk, float]]:
        """Search for similar chunks by vector similarity in a library."""
        pass 

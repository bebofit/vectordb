"""
In-memory implementations of repository interfaces.
"""

from typing import List, Optional, Dict
from uuid import UUID
import threading

from vector_db_api.domain.models.library import Library
from vector_db_api.domain.models.document import Document
from vector_db_api.domain.models.chunk import Chunk
from .interfaces import LibraryRepository, DocumentRepository, ChunkRepository


class InMemoryLibraryRepository(LibraryRepository):
    """Thread-safe in-memory implementation of LibraryRepository."""
    
    def __init__(self):
        self._store: Dict[UUID, Library] = {}
        self._lock = threading.RLock()
    
    async def create(self, library: Library) -> Library:
        """Create a new library."""
        with self._lock:
            self._store[library.id] = library
            return library
    
    async def get_by_id(self, library_id: UUID) -> Optional[Library]:
        """Get library by ID."""
        with self._lock:
            return self._store.get(library_id)
    
    async def list_all(self) -> List[Library]:
        """List all libraries."""
        with self._lock:
            return list(self._store.values())
    
    async def update(self, library: Library) -> Library:
        """Update an existing library."""
        with self._lock:
            self._store[library.id] = library
            return library
    
    async def delete(self, library_id: UUID) -> bool:
        """Delete a library. Returns True if deleted, False if not found."""
        with self._lock:
            if library_id in self._store:
                del self._store[library_id]
                return True
            return False


class InMemoryDocumentRepository(DocumentRepository):
    """Thread-safe in-memory implementation of DocumentRepository."""
    
    def __init__(self):
        self._store: Dict[UUID, Document] = {}
        self._lock = threading.RLock()
    
    async def create(self, document: Document) -> Document:
        """Create a new document."""
        with self._lock:
            self._store[document.id] = document
            return document
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        with self._lock:
            return self._store.get(document_id)
    
    async def list_by_library_id(self, library_id: UUID) -> List[Document]:
        """List all documents in a library."""
        with self._lock:
            return [
                doc for doc in self._store.values()
                if doc.library_id == library_id
            ]
    
    async def update(self, document: Document) -> Document:
        """Update an existing document."""
        with self._lock:
            self._store[document.id] = document
            return document
    
    async def delete(self, document_id: UUID) -> bool:
        """Delete a document. Returns True if deleted, False if not found."""
        with self._lock:
            if document_id in self._store:
                del self._store[document_id]
                return True
            return False


class InMemoryChunkRepository(ChunkRepository):
    """Thread-safe in-memory implementation of ChunkRepository."""
    
    def __init__(self, document_repo: DocumentRepository):
        self._store: Dict[UUID, Chunk] = {}
        self._lock = threading.RLock()
        self._document_repo = document_repo
    
    async def create(self, chunk: Chunk) -> Chunk:
        """Create a new chunk."""
        with self._lock:
            self._store[chunk.id] = chunk
            return chunk
    
    async def get_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get chunk by ID."""
        with self._lock:
            return self._store.get(chunk_id)
    
    async def list_by_document_id(self, document_id: UUID) -> List[Chunk]:
        """List all chunks in a document."""
        with self._lock:
            return [
                chunk for chunk in self._store.values()
                if chunk.document_id == document_id
            ]
    
    async def list_by_library_id(self, library_id: UUID) -> List[Chunk]:
        """List all chunks in a library (across all documents)."""
        # First get all documents in the library
        documents = await self._document_repo.list_by_library_id(library_id)
        document_ids = {doc.id for doc in documents}
        
        with self._lock:
            # Return chunks that belong to documents in this library
            return [
                chunk for chunk in self._store.values()
                if chunk.document_id in document_ids
            ]
    
    async def update(self, chunk: Chunk) -> Chunk:
        """Update an existing chunk."""
        with self._lock:
            self._store[chunk.id] = chunk
            return chunk
    
    async def delete(self, chunk_id: UUID) -> bool:
        """Delete a chunk. Returns True if deleted, False if not found."""
        with self._lock:
            if chunk_id in self._store:
                del self._store[chunk_id]
                return True
            return False
    
    async def search_by_vector_similarity(
        self, 
        library_id: UUID, 
        query_vector: List[float], 
        top_k: int = 10
    ) -> List[tuple[Chunk, float]]:
        """Search for similar chunks by vector similarity in a library."""
        # Get all chunks in the library
        chunks = await self.list_by_library_id(library_id)
        
        if not chunks:
            return []
        
        # Create a temporary chunk for similarity calculation
        from vector_db_api.domain.models.chunk import Chunk as ChunkModel
        query_chunk = ChunkModel(vector=query_vector)
        
        # Calculate similarities
        similarities = []
        for chunk in chunks:
            try:
                similarity = query_chunk.similarity_to(chunk)
                similarities.append((chunk, similarity))
            except ValueError:
                # Skip chunks with different dimensions
                continue
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


class RepositoryContainer:
    """Container for managing repository instances and their dependencies."""
    
    def __init__(self):
        self.library_repo = InMemoryLibraryRepository()
        self.document_repo = InMemoryDocumentRepository()
        self.chunk_repo = InMemoryChunkRepository(self.document_repo)


# Global repository container instance
repo_container = RepositoryContainer() 

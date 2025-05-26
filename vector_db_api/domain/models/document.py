"""
Document domain model representing a collection of chunks with metadata.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from .chunk import Chunk


class Document(BaseModel):
    """
    A document represents a collection of chunks with associated metadata.
    
    This is a core domain entity that groups related chunks together,
    typically representing a single document that has been chunked for
    vector processing.
    """
    
    model_config = ConfigDict()
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the document")
    title: str = Field(..., description="Document title")
    content: Optional[str] = Field(None, description="Original document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    chunk_ids: List[UUID] = Field(default_factory=list, description="List of chunk IDs belonging to this document")
    library_id: Optional[UUID] = Field(None, description="Reference to parent library")
    
    @property
    def chunk_count(self) -> int:
        """Get the number of chunks in this document."""
        return len(self.chunk_ids)
    
    def add_chunk_id(self, chunk_id: UUID) -> None:
        """
        Add a chunk ID to this document.
        
        Args:
            chunk_id: UUID of the chunk to add
        """
        if chunk_id not in self.chunk_ids:
            self.chunk_ids.append(chunk_id)
    
    def remove_chunk_id(self, chunk_id: UUID) -> bool:
        """
        Remove a chunk ID from this document.
        
        Args:
            chunk_id: UUID of the chunk to remove
            
        Returns:
            True if chunk was removed, False if it wasn't found
        """
        try:
            self.chunk_ids.remove(chunk_id)
            return True
        except ValueError:
            return False
    
    def has_chunk(self, chunk_id: UUID) -> bool:
        """
        Check if this document contains a specific chunk.
        
        Args:
            chunk_id: UUID of the chunk to check
            
        Returns:
            True if the document contains the chunk
        """
        return chunk_id in self.chunk_ids 

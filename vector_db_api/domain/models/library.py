"""
Library domain model representing a collection of documents with metadata.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class Library(BaseModel):
    """
    A library represents a collection of documents with associated metadata.
    
    This is a core domain entity that groups related documents together,
    providing a top-level organization structure for vector databases.
    """
    
    model_config = ConfigDict()
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the library")
    name: str = Field(..., description="Library name")
    description: Optional[str] = Field(None, description="Library description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Library metadata")
    document_ids: List[UUID] = Field(default_factory=list, description="List of document IDs in this library")
    
    @property
    def document_count(self) -> int:
        """Get the number of documents in this library."""
        return len(self.document_ids)
    
    def add_document_id(self, document_id: UUID) -> None:
        """
        Add a document ID to this library.
        
        Args:
            document_id: UUID of the document to add
        """
        if document_id not in self.document_ids:
            self.document_ids.append(document_id)
    
    def remove_document_id(self, document_id: UUID) -> bool:
        """
        Remove a document ID from this library.
        
        Args:
            document_id: UUID of the document to remove
            
        Returns:
            True if document was removed, False if it wasn't found
        """
        try:
            self.document_ids.remove(document_id)
            return True
        except ValueError:
            return False
    
    def has_document(self, document_id: UUID) -> bool:
        """
        Check if this library contains a specific document.
        
        Args:
            document_id: UUID of the document to check
            
        Returns:
            True if the library contains the document
        """
        return document_id in self.document_ids
    
    def clear_documents(self) -> None:
        """Remove all documents from this library."""
        self.document_ids.clear() 

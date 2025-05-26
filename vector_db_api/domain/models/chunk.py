"""
Chunk domain model representing a vector with metadata.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, Field, ConfigDict, field_validator


class Chunk(BaseModel):
    """
    A chunk represents a vector with associated metadata.
    
    This is a core domain entity that encapsulates a vector embedding
    along with its metadata and unique identifier.
    """
    
    model_config = ConfigDict()
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the chunk")
    vector: List[float] = Field(..., description="Vector embedding as a list of floats")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Associated metadata")
    document_id: Optional[UUID] = Field(None, description="Reference to parent document")
    
    @field_validator('vector')
    @classmethod
    def validate_vector_not_empty(cls, v: List[float]) -> List[float]:
        """Validate that vector is not empty."""
        if not v:
            raise ValueError("Vector cannot be empty")
        return v
    
    @property
    def vector_array(self) -> np.ndarray:
        """Get vector as numpy array for mathematical operations."""
        return np.array(self.vector, dtype=np.float32)
    
    @property
    def dimension(self) -> int:
        """Get the dimension of the vector."""
        return len(self.vector)
    
    def distance_to(self, other: "Chunk") -> float:
        """
        Calculate Euclidean distance to another chunk.
        
        Args:
            other: Another chunk to calculate distance to
            
        Returns:
            Euclidean distance between the two vectors
        """
        if self.dimension != other.dimension:
            raise ValueError("Cannot calculate distance between vectors of different dimensions")
        
        return float(np.linalg.norm(self.vector_array - other.vector_array))
    
    def similarity_to(self, other: "Chunk") -> float:
        """
        Calculate cosine similarity to another chunk.
        
        Args:
            other: Another chunk to calculate similarity to
            
        Returns:
            Cosine similarity between the two vectors (0-1)
        """
        if self.dimension != other.dimension:
            raise ValueError("Cannot calculate similarity between vectors of different dimensions")
        
        dot_product = np.dot(self.vector_array, other.vector_array)
        norm_a = np.linalg.norm(self.vector_array)
        norm_b = np.linalg.norm(other.vector_array)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b)) 

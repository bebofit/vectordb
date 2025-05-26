"""
Unit tests for domain models (Chunk, Document, Library).
"""

import pytest
from uuid import UUID, uuid4
from pydantic import ValidationError

from vector_db_api.domain.models.chunk import Chunk
from vector_db_api.domain.models.document import Document
from vector_db_api.domain.models.library import Library


class TestChunk:
    """Test cases for the Chunk model."""
    
    def test_chunk_creation_valid(self):
        """Test creating a chunk with valid data."""
        vector = [1.0, 2.0, 3.0]
        metadata = {"text": "test chunk", "source": "test"}
        
        chunk = Chunk(vector=vector, metadata=metadata)
        
        assert isinstance(chunk.id, UUID)
        assert chunk.vector == vector
        assert chunk.metadata == metadata
        assert chunk.document_id is None
        assert chunk.dimension == 3
    
    def test_chunk_creation_with_document_id(self):
        """Test creating a chunk with a document ID."""
        vector = [1.0, 2.0]
        document_id = uuid4()
        
        chunk = Chunk(vector=vector, document_id=document_id)
        
        assert chunk.document_id == document_id
        assert chunk.dimension == 2
    
    def test_chunk_creation_empty_vector_invalid(self):
        """Test that creating a chunk with empty vector fails."""
        with pytest.raises(ValidationError):
            Chunk(vector=[])
    
    def test_chunk_creation_invalid_vector_type(self):
        """Test that creating a chunk with invalid vector type fails."""
        with pytest.raises(ValidationError):
            Chunk(vector="not a list")
    
    def test_chunk_creation_invalid_vector_elements(self):
        """Test that creating a chunk with invalid vector elements fails."""
        with pytest.raises(ValidationError):
            Chunk(vector=[1.0, "not a number", 3.0])
    
    def test_chunk_distance_calculation(self):
        """Test distance calculation between chunks."""
        chunk1 = Chunk(vector=[0.0, 0.0])
        chunk2 = Chunk(vector=[3.0, 4.0])
        
        distance = chunk1.distance_to(chunk2)
        assert distance == 5.0  # 3-4-5 triangle
    
    def test_chunk_similarity_calculation(self):
        """Test similarity calculation between chunks."""
        chunk1 = Chunk(vector=[1.0, 0.0])
        chunk2 = Chunk(vector=[1.0, 0.0])
        
        similarity = chunk1.similarity_to(chunk2)
        assert similarity == 1.0  # Identical vectors
    
    def test_chunk_distance_different_dimensions_fails(self):
        """Test that distance calculation fails for different dimensions."""
        chunk1 = Chunk(vector=[1.0, 2.0])
        chunk2 = Chunk(vector=[1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError, match="different dimensions"):
            chunk1.distance_to(chunk2)
    
    def test_chunk_similarity_different_dimensions_fails(self):
        """Test that similarity calculation fails for different dimensions."""
        chunk1 = Chunk(vector=[1.0, 2.0])
        chunk2 = Chunk(vector=[1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError, match="different dimensions"):
            chunk1.similarity_to(chunk2)


class TestDocument:
    """Test cases for the Document model."""
    
    def test_document_creation_valid(self):
        """Test creating a document with valid data."""
        title = "Test Document"
        content = "This is test content"
        metadata = {"author": "test", "category": "test"}
        
        document = Document(title=title, content=content, metadata=metadata)
        
        assert isinstance(document.id, UUID)
        assert document.title == title
        assert document.content == content
        assert document.metadata == metadata
        assert document.chunk_ids == []
        assert document.library_id is None
        assert document.chunk_count == 0
    
    def test_document_creation_minimal(self):
        """Test creating a document with minimal required data."""
        document = Document(title="Minimal Doc")
        
        assert document.title == "Minimal Doc"
        assert document.content is None
        assert document.metadata == {}
        assert document.chunk_count == 0
    
    def test_document_creation_missing_title_fails(self):
        """Test that creating a document without title fails."""
        with pytest.raises(ValidationError):
            Document()
    
    def test_document_creation_invalid_title_type_fails(self):
        """Test that creating a document with invalid title type fails."""
        with pytest.raises(ValidationError):
            Document(title=123)
    
    def test_document_add_chunk_id(self):
        """Test adding chunk IDs to a document."""
        document = Document(title="Test Doc")
        chunk_id = uuid4()
        
        document.add_chunk_id(chunk_id)
        
        assert chunk_id in document.chunk_ids
        assert document.chunk_count == 1
    
    def test_document_add_duplicate_chunk_id(self):
        """Test that adding duplicate chunk ID doesn't create duplicates."""
        document = Document(title="Test Doc")
        chunk_id = uuid4()
        
        document.add_chunk_id(chunk_id)
        document.add_chunk_id(chunk_id)  # Add same ID again
        
        assert document.chunk_ids.count(chunk_id) == 1
        assert document.chunk_count == 1
    
    def test_document_remove_chunk_id(self):
        """Test removing chunk IDs from a document."""
        document = Document(title="Test Doc")
        chunk_id = uuid4()
        
        document.add_chunk_id(chunk_id)
        result = document.remove_chunk_id(chunk_id)
        
        assert result is True
        assert chunk_id not in document.chunk_ids
        assert document.chunk_count == 0
    
    def test_document_remove_nonexistent_chunk_id(self):
        """Test removing non-existent chunk ID returns False."""
        document = Document(title="Test Doc")
        chunk_id = uuid4()
        
        result = document.remove_chunk_id(chunk_id)
        
        assert result is False
    
    def test_document_has_chunk(self):
        """Test checking if document has a specific chunk."""
        document = Document(title="Test Doc")
        chunk_id = uuid4()
        
        assert document.has_chunk(chunk_id) is False
        
        document.add_chunk_id(chunk_id)
        assert document.has_chunk(chunk_id) is True


class TestLibrary:
    """Test cases for the Library model."""
    
    def test_library_creation_valid(self):
        """Test creating a library with valid data."""
        name = "Test Library"
        description = "This is a test library"
        metadata = {"owner": "test", "category": "test"}
        
        library = Library(name=name, description=description, metadata=metadata)
        
        assert isinstance(library.id, UUID)
        assert library.name == name
        assert library.description == description
        assert library.metadata == metadata
        assert library.document_ids == []
        assert library.document_count == 0
    
    def test_library_creation_minimal(self):
        """Test creating a library with minimal required data."""
        library = Library(name="Minimal Library")
        
        assert library.name == "Minimal Library"
        assert library.description is None
        assert library.metadata == {}
        assert library.document_count == 0
    
    def test_library_creation_missing_name_fails(self):
        """Test that creating a library without name fails."""
        with pytest.raises(ValidationError):
            Library()
    
    def test_library_creation_invalid_name_type_fails(self):
        """Test that creating a library with invalid name type fails."""
        with pytest.raises(ValidationError):
            Library(name=123)
    
    def test_library_add_document_id(self):
        """Test adding document IDs to a library."""
        library = Library(name="Test Library")
        document_id = uuid4()
        
        library.add_document_id(document_id)
        
        assert document_id in library.document_ids
        assert library.document_count == 1
    
    def test_library_add_duplicate_document_id(self):
        """Test that adding duplicate document ID doesn't create duplicates."""
        library = Library(name="Test Library")
        document_id = uuid4()
        
        library.add_document_id(document_id)
        library.add_document_id(document_id)  # Add same ID again
        
        assert library.document_ids.count(document_id) == 1
        assert library.document_count == 1
    
    def test_library_remove_document_id(self):
        """Test removing document IDs from a library."""
        library = Library(name="Test Library")
        document_id = uuid4()
        
        library.add_document_id(document_id)
        result = library.remove_document_id(document_id)
        
        assert result is True
        assert document_id not in library.document_ids
        assert library.document_count == 0
    
    def test_library_remove_nonexistent_document_id(self):
        """Test removing non-existent document ID returns False."""
        library = Library(name="Test Library")
        document_id = uuid4()
        
        result = library.remove_document_id(document_id)
        
        assert result is False
    
    def test_library_has_document(self):
        """Test checking if library has a specific document."""
        library = Library(name="Test Library")
        document_id = uuid4()
        
        assert library.has_document(document_id) is False
        
        library.add_document_id(document_id)
        assert library.has_document(document_id) is True
    
    def test_library_clear_documents(self):
        """Test clearing all documents from a library."""
        library = Library(name="Test Library")
        document_id1 = uuid4()
        document_id2 = uuid4()
        
        library.add_document_id(document_id1)
        library.add_document_id(document_id2)
        assert library.document_count == 2
        
        library.clear_documents()
        assert library.document_count == 0
        assert library.document_ids == [] 

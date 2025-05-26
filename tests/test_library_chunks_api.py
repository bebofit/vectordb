"""
API tests for library-specific chunk operations.
"""

import pytest
from fastapi.testclient import TestClient

from vector_db_api.interface.main import app

client = TestClient(app)


class TestLibraryChunksAPI:
    """Test cases for library-specific chunk API endpoints."""
    
    def setup_method(self):
        """Set up a test library for each test."""
        library_data = {"name": "Test Library for Chunks"}
        response = client.post("/api/v1/libraries", json=library_data)
        assert response.status_code == 200
        self.library_id = response.json()["id"]
    
    def test_create_chunk_in_library_valid(self):
        """Test creating a chunk within a library."""
        chunk_data = {
            "vector": [1.0, 2.0, 3.0],
            "metadata": {"text": "test chunk in library", "source": "test"}
        }
        
        response = client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["vector"] == [1.0, 2.0, 3.0]
        assert data["metadata"] == {"text": "test chunk in library", "source": "test"}
        assert data["dimension"] == 3
    
    def test_create_chunk_in_nonexistent_library_fails(self):
        """Test creating a chunk in a non-existent library fails."""
        fake_library_id = "00000000-0000-0000-0000-000000000000"
        chunk_data = {"vector": [1.0, 2.0, 3.0]}
        
        response = client.post(f"/api/v1/libraries/{fake_library_id}/chunks", json=chunk_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_create_chunk_in_library_invalid_vector_fails(self):
        """Test creating a chunk with invalid vector fails."""
        chunk_data = {"vector": "not a list"}
        
        response = client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_chunk_in_library_valid(self):
        """Test retrieving a chunk within a library."""
        # First create a chunk
        chunk_data = {"vector": [4.0, 5.0, 6.0], "metadata": {"test": "data"}}
        
        create_response = client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk_data)
        assert create_response.status_code == 200
        chunk_id = create_response.json()["id"]
        
        # Then retrieve it
        get_response = client.get(f"/api/v1/libraries/{self.library_id}/chunks/{chunk_id}")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["id"] == chunk_id
        assert data["vector"] == [4.0, 5.0, 6.0]
        assert data["metadata"] == {"test": "data"}
    
    def test_get_chunk_in_nonexistent_library_fails(self):
        """Test retrieving a chunk from a non-existent library fails."""
        fake_library_id = "00000000-0000-0000-0000-000000000000"
        fake_chunk_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.get(f"/api/v1/libraries/{fake_library_id}/chunks/{fake_chunk_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_get_nonexistent_chunk_in_library_fails(self):
        """Test retrieving a non-existent chunk from a library fails."""
        fake_chunk_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.get(f"/api/v1/libraries/{self.library_id}/chunks/{fake_chunk_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Chunk not found"
    
    def test_list_chunks_in_library_empty(self):
        """Test listing chunks in a library when none exist."""
        response = client.get(f"/api/v1/libraries/{self.library_id}/chunks")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_chunks_in_library_with_data(self):
        """Test listing chunks in a library when some exist."""
        # Create a few chunks
        chunk1_data = {"vector": [1.0, 2.0]}
        chunk2_data = {"vector": [3.0, 4.0]}
        
        client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk1_data)
        client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk2_data)
        
        response = client.get(f"/api/v1/libraries/{self.library_id}/chunks")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the two we created
    
    def test_list_chunks_in_nonexistent_library_fails(self):
        """Test listing chunks in a non-existent library fails."""
        fake_library_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.get(f"/api/v1/libraries/{fake_library_id}/chunks")
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_update_chunk_in_library_valid(self):
        """Test updating a chunk within a library."""
        # First create a chunk
        chunk_data = {"vector": [1.0, 2.0], "metadata": {"original": True}}
        
        create_response = client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk_data)
        assert create_response.status_code == 200
        chunk_id = create_response.json()["id"]
        
        # Then update it
        update_data = {"vector": [3.0, 4.0], "metadata": {"updated": True}}
        
        update_response = client.put(
            f"/api/v1/libraries/{self.library_id}/chunks/{chunk_id}", 
            json=update_data
        )
        assert update_response.status_code == 200
        
        data = update_response.json()
        assert data["vector"] == [3.0, 4.0]
        assert data["metadata"] == {"updated": True}
        assert data["dimension"] == 2
    
    def test_update_chunk_in_nonexistent_library_fails(self):
        """Test updating a chunk in a non-existent library fails."""
        fake_library_id = "00000000-0000-0000-0000-000000000000"
        fake_chunk_id = "11111111-1111-1111-1111-111111111111"
        update_data = {"vector": [1.0, 2.0]}
        
        response = client.put(
            f"/api/v1/libraries/{fake_library_id}/chunks/{fake_chunk_id}", 
            json=update_data
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_update_nonexistent_chunk_in_library_fails(self):
        """Test updating a non-existent chunk in a library fails."""
        fake_chunk_id = "11111111-1111-1111-1111-111111111111"
        update_data = {"vector": [1.0, 2.0]}
        
        response = client.put(
            f"/api/v1/libraries/{self.library_id}/chunks/{fake_chunk_id}", 
            json=update_data
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Chunk not found"
    
    def test_delete_chunk_in_library_valid(self):
        """Test deleting a chunk within a library."""
        # First create a chunk
        chunk_data = {"vector": [1.0, 2.0]}
        
        create_response = client.post(f"/api/v1/libraries/{self.library_id}/chunks", json=chunk_data)
        assert create_response.status_code == 200
        chunk_id = create_response.json()["id"]
        
        # Then delete it
        delete_response = client.delete(f"/api/v1/libraries/{self.library_id}/chunks/{chunk_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Chunk deleted successfully"
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/libraries/{self.library_id}/chunks/{chunk_id}")
        assert get_response.status_code == 404
    
    def test_delete_chunk_in_nonexistent_library_fails(self):
        """Test deleting a chunk from a non-existent library fails."""
        fake_library_id = "00000000-0000-0000-0000-000000000000"
        fake_chunk_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.delete(f"/api/v1/libraries/{fake_library_id}/chunks/{fake_chunk_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_delete_nonexistent_chunk_in_library_fails(self):
        """Test deleting a non-existent chunk from a library fails."""
        fake_chunk_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.delete(f"/api/v1/libraries/{self.library_id}/chunks/{fake_chunk_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Chunk not found" 

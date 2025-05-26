"""
API tests for the libraries endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from vector_db_api.interface.main import app

client = TestClient(app)


class TestLibrariesAPI:
    """Test cases for the libraries API endpoints."""
    
    def test_create_library_valid(self):
        """Test creating a library with valid data."""
        library_data = {
            "name": "Test Library",
            "description": "A test library for unit testing",
            "metadata": {"owner": "test", "category": "testing"}
        }
        
        response = client.post("/api/v1/libraries", json=library_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Library"
        assert data["description"] == "A test library for unit testing"
        assert data["metadata"] == {"owner": "test", "category": "testing"}
        assert data["document_ids"] == []
        assert data["document_count"] == 0
    
    def test_create_library_minimal(self):
        """Test creating a library with minimal required data."""
        library_data = {"name": "Minimal Library"}
        
        response = client.post("/api/v1/libraries", json=library_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Minimal Library"
        assert data["description"] is None
        assert data["metadata"] == {}
    
    def test_create_library_missing_name_fails(self):
        """Test that creating a library without name fails."""
        library_data = {"description": "No name library"}
        
        response = client.post("/api/v1/libraries", json=library_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_library_invalid_name_type_fails(self):
        """Test that creating a library with invalid name type fails."""
        library_data = {"name": 123}
        
        response = client.post("/api/v1/libraries", json=library_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_library_valid(self):
        """Test retrieving a library by ID."""
        # First create a library
        library_data = {
            "name": "Get Test Library",
            "description": "Library for get testing"
        }
        
        create_response = client.post("/api/v1/libraries", json=library_data)
        assert create_response.status_code == 200
        library_id = create_response.json()["id"]
        
        # Then retrieve it
        get_response = client.get(f"/api/v1/libraries/{library_id}")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["id"] == library_id
        assert data["name"] == "Get Test Library"
        assert data["description"] == "Library for get testing"
    
    def test_get_library_not_found(self):
        """Test retrieving a non-existent library returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/libraries/{fake_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_get_library_invalid_uuid_fails(self):
        """Test retrieving a library with invalid UUID fails."""
        response = client.get("/api/v1/libraries/invalid-uuid")
        assert response.status_code == 422  # Validation error
    
    def test_list_libraries_empty(self):
        """Test listing libraries when none exist."""
        # Clear any existing libraries by creating a new client
        response = client.get("/api/v1/libraries")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_libraries_with_data(self):
        """Test listing libraries when some exist."""
        # Create a few libraries
        library1_data = {"name": "Library 1"}
        library2_data = {"name": "Library 2"}
        
        client.post("/api/v1/libraries", json=library1_data)
        client.post("/api/v1/libraries", json=library2_data)
        
        response = client.get("/api/v1/libraries")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the two we created
    
    def test_update_library_valid(self):
        """Test updating a library with valid data."""
        # First create a library
        library_data = {"name": "Original Name", "description": "Original description"}
        
        create_response = client.post("/api/v1/libraries", json=library_data)
        assert create_response.status_code == 200
        library_id = create_response.json()["id"]
        
        # Then update it
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "metadata": {"updated": True}
        }
        
        update_response = client.put(f"/api/v1/libraries/{library_id}", json=update_data)
        assert update_response.status_code == 200
        
        data = update_response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["metadata"] == {"updated": True}
    
    def test_update_library_partial(self):
        """Test updating a library with partial data."""
        # First create a library
        library_data = {
            "name": "Original Name",
            "description": "Original description",
            "metadata": {"original": True}
        }
        
        create_response = client.post("/api/v1/libraries", json=library_data)
        assert create_response.status_code == 200
        library_id = create_response.json()["id"]
        
        # Then update only the name
        update_data = {"name": "Partially Updated Name"}
        
        update_response = client.put(f"/api/v1/libraries/{library_id}", json=update_data)
        assert update_response.status_code == 200
        
        data = update_response.json()
        assert data["name"] == "Partially Updated Name"
        assert data["description"] == "Original description"  # Should remain unchanged
        assert data["metadata"] == {"original": True}  # Should remain unchanged
    
    def test_update_library_not_found(self):
        """Test updating a non-existent library returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Updated Name"}
        
        response = client.put(f"/api/v1/libraries/{fake_id}", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found"
    
    def test_delete_library_valid(self):
        """Test deleting a library."""
        # First create a library
        library_data = {"name": "Library to Delete"}
        
        create_response = client.post("/api/v1/libraries", json=library_data)
        assert create_response.status_code == 200
        library_id = create_response.json()["id"]
        
        # Then delete it
        delete_response = client.delete(f"/api/v1/libraries/{library_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Library deleted successfully"
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/libraries/{library_id}")
        assert get_response.status_code == 404
    
    def test_delete_library_not_found(self):
        """Test deleting a non-existent library returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.delete(f"/api/v1/libraries/{fake_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Library not found" 

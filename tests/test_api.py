"""
Basic API tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from vector_db_api.interface.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns expected response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to StakeAI Vector Database API"
    assert data["version"] == "0.1.0"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_detailed_health_check():
    """Test the detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data
    assert "system" in data


def test_create_chunk():
    """Test creating a new chunk."""
    chunk_data = {
        "vector": [1.0, 2.0, 3.0],
        "metadata": {"text": "test chunk", "source": "test"}
    }
    
    response = client.post("/api/v1/chunks", json=chunk_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert data["vector"] == [1.0, 2.0, 3.0]
    assert data["metadata"] == {"text": "test chunk", "source": "test"}
    assert data["dimension"] == 3


def test_get_chunk():
    """Test retrieving a chunk by ID."""
    # First create a chunk
    chunk_data = {
        "vector": [4.0, 5.0, 6.0],
        "metadata": {"text": "another test chunk"}
    }
    
    create_response = client.post("/api/v1/chunks", json=chunk_data)
    assert create_response.status_code == 200
    chunk_id = create_response.json()["id"]
    
    # Then retrieve it
    get_response = client.get(f"/api/v1/chunks/{chunk_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == chunk_id
    assert data["vector"] == [4.0, 5.0, 6.0]


def test_list_chunks():
    """Test listing all chunks."""
    response = client.get("/api/v1/chunks")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_chunk():
    """Test retrieving a non-existent chunk returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/chunks/{fake_id}")
    assert response.status_code == 404 

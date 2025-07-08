import pytest
from fastapi.testclient import TestClient
import os
import sys
import json
from unittest.mock import patch, AsyncMock

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns a healthy status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "CultureBot"}

def test_health_endpoint():
    """Test the health endpoint returns detailed status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CultureBot"
    assert data["model"] == "mistralai/Mistral-7B-Instruct"
    assert "version" in data

@patch('app.models.CultureModel.get_answer')
def test_ask_endpoint_success(mock_get_answer):
    """Test the ask endpoint with a valid question."""
    # Setup the mock to return a specific answer
    mock_get_answer.return_value = AsyncMock(return_value="This is a test answer about culture.")
    
    # Send a test question
    response = client.post(
        "/ask",
        json={"question": "What is the cultural significance of the Taj Mahal?"}
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data

def test_ask_endpoint_missing_question():
    """Test the ask endpoint with a missing question."""
    response = client.post("/ask", json={})
    assert response.status_code == 400
    assert "Question is required" in response.json()["detail"]

@patch('app.models.CultureModel.get_answer')
def test_ask_endpoint_model_error(mock_get_answer):
    """Test the ask endpoint when the model raises an error."""
    # Setup the mock to raise an exception
    mock_get_answer.side_effect = AsyncMock(side_effect=Exception("Test model error"))
    
    # Send a test question
    response = client.post(
        "/ask",
        json={"question": "What is the cultural significance of the Taj Mahal?"}
    )
    
    # Check the response
    assert response.status_code == 500
    assert "Error generating answer" in response.json()["detail"]

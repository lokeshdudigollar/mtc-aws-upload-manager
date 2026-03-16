import pytest
import json
from unittest.mock import patch, MagicMock
from src.handlers.delete_image import handler

@pytest.fixture
def mock_service():
    with patch("src.handlers.delete_image.get_image_service") as mocked_factory:
        mock_svc = MagicMock()
        mocked_factory.return_value = mock_svc
        yield mock_svc

def test_delete_image_success(mock_service):
    # Setup
    event = {
        "pathParameters": {
            "userId": "user123",
            "imageId": "img123"
        }
    }
    
    # Act
    response = handler(event, None)
    
    # Assert
    assert response["statusCode"] == 204
    # Ensure service was called correctly
    mock_service.delete_image.assert_called_with(user_id="user123", image_id="img123")

def test_delete_image_missing_params(mock_service):
    # Event missing userId
    event = {"pathParameters": {"imageId": "img123"}}
    
    response = handler(event, None)
    
    assert response["statusCode"] == 400
    assert "userId and imageId are required" in response["body"]
    mock_service.delete_image.assert_not_called()

def test_delete_image_not_found(mock_service):
    # Simulate service raising ValueError when image doesn't exist
    mock_service.delete_image.side_effect = ValueError("Image not found")
    
    event = {
        "pathParameters": {
            "userId": "user123",
            "imageId": "unknown"
        }
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 404
    assert "Image not found" in response["body"]

def test_delete_image_internal_error(mock_service):
    # Simulate an unexpected server error
    mock_service.delete_image.side_effect = Exception("Database crash")
    
    event = {
        "pathParameters": {
            "userId": "user123",
            "imageId": "img123"
        }
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 500
    assert "Internal server error" in response["body"]
import pytest
import json
from unittest.mock import patch, MagicMock
from src.handlers.get_image import handler

@pytest.fixture
def mock_service():
    with patch("src.handlers.get_image.get_image_service") as mocked_factory:
        mock_svc = MagicMock()
        mocked_factory.return_value = mock_svc
        yield mock_svc

def test_get_image_success(mock_service):
    # Setup mock service response
    expected_result = {
        "imageId": "img123",
        "title": "Sunset",
        "downloadUrl": "https://signed-url"
    }
    mock_service.get_image.return_value = expected_result
    
    # Simulate API Gateway event with path parameters
    event = {
        "pathParameters": {
            "userId": "user123",
            "imageId": "img123"
        }
    }
    
    # Act
    response = handler(event, None)
    
    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == expected_result
    mock_service.get_image.assert_called_with(user_id="user123", image_id="img123", expiration=3600)

def test_get_image_missing_params(mock_service):
    # Event missing pathParameters
    event = {"pathParameters": {}}
    
    response = handler(event, None)
    
    assert response["statusCode"] == 400
    assert "userId and imageId are required" in response["body"]
    mock_service.get_image.assert_not_called()

def test_get_image_not_found(mock_service):
    # Mock the service to raise a ValueError (simulating 'not found')
    mock_service.get_image.side_effect = ValueError("Image not found")
    
    event = {
        "pathParameters": {
            "userId": "user123",
            "imageId": "nonexistent"
        }
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 404
    assert "Image not found" in response["body"]

def test_get_image_internal_error(mock_service):
    # Mock a generic unexpected exception
    mock_service.get_image.side_effect = Exception("Boom!")
    
    event = {
        "pathParameters": {
            "userId": "user123",
            "imageId": "img123"
        }
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 500
    assert "Internal server error" in response["body"]
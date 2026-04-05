import pytest
import json
from unittest.mock import patch, MagicMock
from src.handlers.list_images import handler

@pytest.fixture
def mock_service():
    with patch("src.handlers.list_images.get_image_service") as mocked_factory:
        mock_svc = MagicMock()
        mocked_factory.return_value = mock_svc
        yield mock_svc

def test_list_images_success(mock_service):
    # Setup mock service response
    mock_service.list_images.return_value = {
        "items": [{"imageId": "123", "title": "Test", "status": "READY"}],
        "nextToken": "eyJ1c2VySWQiOiAidXNlcjEyMyJ9"
    }
    
    event = {
        "queryStringParameters": {
            "userId": "user123",
            "limit": "10"
        }
    }
    
    # Act
    response = handler(event, None)
    
    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body["items"]) == 1
    assert body["nextToken"] is not None
    mock_service.list_images.assert_called_with(user_id="user123", limit=10, last_key=None)

def test_list_images_missing_userid(mock_service):
    event = {"queryStringParameters": {}}
    
    response = handler(event, None)
    
    assert response["statusCode"] == 400
    assert "userId header is required" in response["body"]
    mock_service.list_images.assert_not_called()

def test_list_images_invalid_limit(mock_service):
    event = {
        "queryStringParameters": {
            "userId": "user123",
            "limit": "not-a-number"
        }
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 400
    assert "limit must be a number" in response["body"]

def test_list_images_with_token(mock_service):
    # Mock decoding logic
    with patch("src.handlers.list_images.decode_token", return_value={"imageId": "abc"}):
        event = {
            "queryStringParameters": {
                "userId": "user123",
                "nextToken": "some-encoded-token"
            }
        }
        
        handler(event, None)
        
        # Verify that last_key was passed correctly
        mock_service.list_images.assert_called_with(
            user_id="user123", limit=20, last_key={"imageId": "abc"}
        )
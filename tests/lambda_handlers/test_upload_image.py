import pytest
import json
import base64
from unittest.mock import patch, MagicMock
from src.handlers.upload_image import handler

@pytest.fixture
def mock_service():
    """Patches the factory to return a mock service."""
    with patch("src.handlers.upload_image.get_image_service") as mocked_factory:
        mock_svc = MagicMock()
        mocked_factory.return_value = mock_svc
        yield mock_svc

def test_handler_success(mock_service):
    """Test successful image upload flow."""
    # Configure mock service behavior
    mock_service.upload_image.return_value = {"imageId": "ulid123", "status": "READY"}
    
    event = {
        "headers": {
            "userid": "user_1",
            "title": "Sunset",
            "content-type": "image/jpeg",
            "filename": "sunset.jpg"
        },
        "isBase64Encoded": False,
        "body": "fake-image-bytes"
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["imageId"] == "ulid123"
    mock_service.upload_image.assert_called_once()

def test_handler_missing_userid(mock_service):
    """Test that missing userId returns 400."""
    event = {
        "headers": {"content-type": "image/jpeg"},
        "body": "some-data"
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 400
    assert "userId header is required" in response["body"]
    mock_service.upload_image.assert_not_called()

def test_handler_unsupported_file_type(mock_service):
    """Test validation of MIME types."""
    event = {
        "headers": {
            "userid": "user_1",
            "content-type": "application/pdf"
        },
        "body": "data"
    }
    
    response = handler(event, None)
    
    assert response["statusCode"] == 400
    assert "Unsupported file type" in response["body"]

def test_handler_base64_decoding(mock_service):
    """Test if the handler correctly handles isBase64Encoded flag."""
    raw_data = b"image-content"
    encoded_data = base64.b64encode(raw_data).decode('utf-8')
    
    event = {
        "isBase64Encoded": True,
        "headers": {
            "userid": "user1",
            "content-type": "image/png"
        },
        "body": encoded_data
    }
    
    handler(event, None)
    
    # Verify the service received the correctly decoded bytes
    args, _ = mock_service.upload_image.call_args
    assert args[3] == raw_data  # index 3 is file_bytes
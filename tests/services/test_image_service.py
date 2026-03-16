import pytest
from unittest.mock import MagicMock
from src.services.image_service import ImageService
from botocore.exceptions import ClientError

@pytest.fixture
def service():
    # Setup mocks for dependencies
    db_mock = MagicMock()
    s3_mock = MagicMock()
    return ImageService(db_repo=db_mock, s3_repo=s3_mock)

def test_list_images_empty_result(service):
    # Setup
    service.db.list_images.return_value = {"items": [], "lastEvaluatedKey": None}
    
    # Act
    result = service.list_images("user123")
    
    # Assert
    assert result["items"] == []
    assert result["nextToken"] is None
    
def test_list_images_filters_ready_only(service):
    # Setup: DB returns a mix of READY and UPLOADING
    service.db.list_images.return_value = {
        "items": [
            {"imageId": "1", "status": "READY"},
            {"imageId": "2", "status": "UPLOADING"},
            {"imageId": "3", "status": "READY"}
        ],
        "lastEvaluatedKey": {"imageId": "3"}
    }
    
    # Act
    result = service.list_images("user123")
    
    # Assert
    # Filtered out status "UPLOADING"
    assert len(result["items"]) == 2
    assert result["items"][0]["status"] == "READY"
    assert result["items"][1]["status"] == "READY"
    # Verify nextToken exists (encoded from the lastEvaluatedKey)
    assert result["nextToken"] is not None

def test_upload_image_happy_path(service):
    # Setup
    service.s3.upload_image.return_value = "s3-key-123"
    
    # Act
    result = service.upload_image(
        user_id="user1",
        title="Test Image",
        tags=["nature", "test"],
        file_bytes=b"fake-bytes",
        content_type="image/jpeg",
        file_name="test.jpg"
    )
    
    # Assert
    assert result["status"] == "READY"
    assert result["s3Key"] == "s3-key-123"
    service.db.save_metadata.assert_called()
    service.db.update_metadata.assert_called()

def test_upload_image_idempotency_skip(service):
    # Setup: simulate existing image in DB
    service.db.get_by_idempotency_key.return_value = {
        "imageId": "existing-id",
        "status": "READY"
    }
    
    # Act
    result = service.upload_image(
        user_id="user1", title="Dupe", tags=[], 
        file_bytes=b"data", content_type="img", file_name="f.jpg"
    )
    
    # Assert
    assert result["imageId"] == "existing-id"
    service.s3.upload_image.assert_not_called()

def test_upload_image_s3_failure_rollback(service):
    # Setup: S3 upload fails
    service.s3.upload_image.side_effect = Exception("S3 upload failed")
    
    # Act & Assert
    with pytest.raises(Exception, match="S3 upload failed"):
        service.upload_image(
            user_id="user1", title="Fail", tags=[], 
            file_bytes=b"data", content_type="img", file_name="f.jpg"
        )
    
    # Verify rollback: status set to ERROR
    # We check if update_metadata was called with status=ERROR
    error_update = [
        call for call in service.db.update_metadata.call_args_list 
        if call.kwargs['expression_attribute_values'][':status'] == "ERROR"
    ]
    assert len(error_update) == 1

def test_upload_image_db_conditional_failure(service):
    # Setup: Simulate ConditionalCheckFailedException during save
    # Create a custom botocore error
    error_response = {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Exists'}}
    exception = ClientError(error_response, 'PutItem')
    
    service.db.save_metadata.side_effect = exception
    service.db.get_by_idempotency_key.return_value = {"imageId": "found-id", "status": "UPLOADING"}
    
    # Act
    result = service.upload_image(
        user_id="user1", title="...", tags=[], 
        file_bytes=b"data", content_type="img", file_name="f.jpg"
    )
    
    # Assert
    assert result["imageId"] == "found-id"
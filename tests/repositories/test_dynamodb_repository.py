import pytest
from src.repositories.dynamodb_repository import DynamoDBRepository

def test_save_and_get_metadata(dynamodb_table):
    repo = DynamoDBRepository(dynamodb_table)
    
    test_item = {
        "userId": "user_1",
        "imageId": "img_123",
        "status": "READY"
    }
    
    # Act
    repo.save_metadata(test_item)
    
    # Assert
    retrieved = repo.get_image_metadata("user_1", "img_123")
    assert retrieved["status"] == "READY"
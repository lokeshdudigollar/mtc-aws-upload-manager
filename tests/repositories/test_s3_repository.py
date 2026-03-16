import pytest
import os
from src.repositories.s3_repository import S3Repository
from src.config import S3_BUCKET

def test_upload_image(s3_client):
    # Arrange
    repo = S3Repository(s3_client)
    # The bucket MUST exist in the moto session before uploading
    s3_client.create_bucket(Bucket=S3_BUCKET)
    file_data = b"fake-image-bytes"
    
    # Act
    key = repo.upload_image(file_data, "test-id", "image/jpeg")
    
    # Assert
    assert key == "images/test-id"
    # Verify the object actually exists in the mock S3
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    assert response["Body"].read() == file_data
    assert response["ContentType"] == "image/jpeg"

def test_generate_presigned_url(s3_client):
    # Arrange
    repo = S3Repository(s3_client)
    s3_key = "images/test-id"
    
    # Act
    url = repo.generate_presigned_url(s3_key)
    
    if os.environ.get("ENVIRONMENT") == "localstack":
        url = url.replace("localstack:4566", "localhost:4566")
    
    return url
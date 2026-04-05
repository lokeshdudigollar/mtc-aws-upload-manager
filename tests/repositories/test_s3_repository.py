import pytest
from src.repositories.s3_repository import S3Repository
from src.config import S3_BUCKET

def test_upload_image(s3_client):
    repo = S3Repository(s3_client,S3_BUCKET)
    s3_client.create_bucket(Bucket=S3_BUCKET)

    file_data = b"fake-image-bytes"

    key = repo.upload_image(file_data, "test-id", "image/jpeg")

    assert key == "images/test-id"

    response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    assert response["Body"].read() == file_data
    assert response["ContentType"] == "image/jpeg"


def test_generate_presigned_url(s3_client):
    repo = S3Repository(s3_client,S3_BUCKET)
    s3_client.create_bucket(Bucket=S3_BUCKET)

    s3_key = "images/test-id"

    url = repo.generate_presigned_url(s3_key, expiration=3600)

    assert isinstance(url, str)
    assert "images/test-id" in url
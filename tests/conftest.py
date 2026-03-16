import pytest
import os
import boto3
from moto import mock_aws

@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for all tests."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="session")
def s3_client(aws_credentials):
    with mock_aws():
        client = boto3.client(
            "s3", 
            region_name="us-east-1"
        )
        client.create_bucket(Bucket="my-test-bucket")
        yield client

@pytest.fixture(scope="session")
def dynamodb_table(aws_credentials):
    with mock_aws():
        import boto3
        # Use the resource wrapper
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="ImagesMetadata",
            KeySchema=[{"AttributeName": "userId", "KeyType": "HASH"}, 
                       {"AttributeName": "imageId", "KeyType": "RANGE"}],
            AttributeDefinitions=[{"AttributeName": "userId", "AttributeType": "S"},
                                  {"AttributeName": "imageId", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        yield table # Yield the table object directly
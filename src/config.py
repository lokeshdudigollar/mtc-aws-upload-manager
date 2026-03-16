import boto3
import os
REGION = "us-east-1"
#ENDPOINT_URL = "http://localstack:4566" or "http://host.docker.internal:4566" or "http://localhost:4566"
ENDPOINT_URL = os.getenv("AWS_ENDPOINT", "http://localstack:4566")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "Images")
S3_BUCKET = os.getenv("S3_BUCKET", "image-bucket")

#dynamodb client
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

#s3 client
s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)
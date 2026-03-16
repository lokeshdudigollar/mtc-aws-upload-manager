from src.repositories.dynamodb_repository import DynamoDBRepository
from src.repositories.s3_repository import S3Repository
from src.services.image_service import ImageService
from src.config import dynamodb, DYNAMO_TABLE, s3, S3_BUCKET

def get_image_service():
    table = dynamodb.Table(DYNAMO_TABLE)
    db_repo = DynamoDBRepository(table)
    s3_repo = S3Repository(s3, S3_BUCKET)
    return ImageService(db_repo, s3_repo)
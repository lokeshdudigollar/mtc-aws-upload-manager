import datetime
import hashlib
import ulid

from src.utils.pagination import encode_token
from botocore.exceptions import ClientError
from src.models.image_model import Image

class ImageService:
    """
    Dependency Inversion Principle
    """
    def __init__(self, db_repo, s3_repo):
        self.db = db_repo
        self.s3 = s3_repo

    def upload_image(self,user_id, title, tags, file_bytes, content_type, file_name):
        """
        Coordinates the multi-step process of saving image metadata and uploading to S3.
        
        Args:
            user_id (str): ID of the owner.
            title (str): Image title.
            tags (list): List of strings.
            file_bytes (bytes): Raw image data.
            content_type (str): MIME type.
            file_name (str): Original filename for idempotency calculation.
        
        Returns:
            dict: The image ID and final status.
        """
        if not user_id:
            raise ValueError("User ID is required")
        if not file_bytes:
            raise ValueError("image file is required")

        # Generate ULID for high-performance sorting/uniqueness
        image_id = str(ulid.new())
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Generate idempotency key to prevent duplicate processing of the same file
        raw = file_bytes + user_id.encode() # prevents two users uploading the same image from colliding.
        idempotency_key = hashlib.sha256(raw).hexdigest()
        existing = self.db.get_by_idempotency_key(idempotency_key)
        if existing and existing.get("status") == "READY":
            return {
                "imageId": existing["imageId"],
                "status": existing["status"]
            }
        
        #save initial metadata with status=UPLOADING
        
        image = Image(
            userId=user_id,
            imageId=image_id,
            createdAt=created_at,
            title=title,
            tags=tags,
            status="UPLOADING",
            idempotencyKey=idempotency_key
        )
        try:
            self.db.save_metadata(image.to_dict())
        except ClientError as error:
            existing = self.db.get_by_idempotency_key(idempotency_key)
            return existing


        try:
            # Upload image to S3 (using image_id as the storage key)
            s3Key = self.s3.upload_image(
                file_bytes= file_bytes,
                image_id= image_id,
                content_type= content_type
            )
            # update metadata with status change to READY
            self.db.update_metadata(
                user_id= user_id,
                image_id= image_id,
                update_expression= "SET #s = :status, s3Key= :s3Key",
                expression_attribute_values= {
                    ":status": "READY",
                    ":s3Key": s3Key
                }
            )

        except Exception as error:
            # Rollback status to ERROR if S3 upload fails
            self.db.update_metadata(
                user_id= user_id,
                image_id= image_id,
                update_expression= "SET #s = :status",
                expression_attribute_values= {
                    ":status": "ERROR"
                }
            )
            raise

        return Image(
            userId=user_id,
            imageId=image_id,
            createdAt=created_at,
            status="READY",
            title=title,
            tags=tags,
            s3Key=s3Key
        ).to_dict()
    
    def list_images(self,user_id, limit= 20, last_key= None):
        """
        Retrieves a paginated list of images for a user.
        """
        dbQueryResult = self.db.list_images(
            user_id,
            limit,
            last_key
        )
        # Users should only see:
        # status = READY
        items = [item for item in dbQueryResult["items"] if item.get("status") == "READY"]
        next_token = None    
        last_evaluated_key = dbQueryResult.get("lastEvaluatedKey")
        if last_evaluated_key:
            next_token = encode_token(last_evaluated_key)
        
        return {
            "items": items,
            "nextToken": next_token
        }
    
    def get_image(self,user_id, image_id):
        """
        Fetches image metadata and generates a temporary download link.
        """
        item = self.db.get_image_metadata(user_id, image_id)

        if not item:
            raise ValueError("image not found")
        if item.get("status") != "READY":
            raise ValueError("Image not available")
        
        s3Key = item.get("s3Key")
        if not s3Key:
            raise ValueError("Image storage path missing")
        
        presigned_download_url = self.s3.generate_presigned_url(s3Key)
        return {
            "imageId": image_id,
            "title": item.get("title"),
            "downloadURL": presigned_download_url
        }
    
    def delete_image(self,user_id, image_id):
        """
        Removes image from storage and deletes metadata from the database.
        """
        item = self.db.get_image_metadata(user_id, image_id)

        # If item doesn't exist, treat as already deleted
        if not item:
            return

        s3Key = item.get("s3Key")
        # Delete from S3 first
        if s3Key:
            self.s3.delete_image(s3Key)

        # Delete metadat from DynamoDB
        self.db.delete_image_metadata(user_id, image_id)
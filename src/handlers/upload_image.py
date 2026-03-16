import base64
import json

from src.utils.image_service_factory import get_image_service

def handler(event, context):
    """
    AWS Lambda handler for image uploads.
    
    Expects a multipart/form-data request or a base64-encoded binary body.
    """
    image_service = get_image_service()
    try:
        # Handle the body based on the encoding flag
        is_base64 = event.get('isBase64Encoded', False)
        body = event.get('body', '')

        if not body:
            raise ValueError("Request body is empty")
        
        if is_base64:
            file_bytes = base64.b64decode(body)
        else:
            file_bytes = body.encode('utf-8')
        
        # normalize headers to lowercase
        headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
        # Retrieve metadata from headers
        user_id = headers.get("userid")
        title = headers.get("title")
        tags = headers.get("tags", [])
        file_name = headers.get("filename")
        content_type = headers.get("content-type")

        if not user_id:
            raise ValueError("userId header is required")
        
        allowed_types = ["image/jpeg", "image/png"]
        if content_type not in allowed_types:
            raise ValueError("Unsupported file type")

        
        MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB > to avoid memory overflow
        if len(file_bytes) > MAX_IMAGE_SIZE:
            raise ValueError("File size exceeds the limit of 5MB")
        
        # if tags arrive as a string, split it into a list:
        if isinstance(tags, str):
            tags = tags.split(",")
        
        uploadResult = image_service.upload_image(
            user_id,
            title,
            tags,
            file_bytes,
            content_type,
            file_name
        )

        return {
            "statusCode": 201,
            "body": json.dumps(uploadResult)
        }
        
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"Bad request error": str(e)})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"Internal Server Error": str(e)})
        }
import base64
import json

from src.utils.image_service_factory import get_image_service
import src.utils.constants as constants

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
            raise ValueError(constants.ERR_MISSING_BODY)
        
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
            raise ValueError(constants.ERR_MISSING_USER_ID)
        

        if content_type not in constants.ALLOWED_CONTENT_TYPES:
            raise ValueError(constants.ERR_UNSUPPORTED_FILE)

        
        if len(file_bytes) > constants.MAX_IMAGE_SIZE_BYTES:
            raise ValueError(constants.ERR_FILE_TOO_LARGE)
        
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
            "statusCode": constants.HTTP_CREATED,
            "body": json.dumps(uploadResult)
        }
        
    except ValueError as e:
        return {
            "statusCode": constants.HTTP_BAD_REQUEST,
            "body": json.dumps({constants.ERR_BAD_REQUEST: str(e)})
        }

    except Exception as e:
        return {
            "statusCode": constants.HTTP_INTERNAL_ERROR,
            "body": json.dumps({constants.ERR_INTERNAL_SERVER: str(e)})
        }
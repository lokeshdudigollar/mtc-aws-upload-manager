import json

from src.utils.image_service_factory import get_image_service
from src.utils.pagination import decode_token
import src.utils.constants as constants

"""
Example request: GET /images?userId=user123&limit=10&lastKey=XYZ

Example response:
{
  "items": [
    {
      "imageId": "01HV9YJ6ZK9W4H7X2A",
      "title": "Sunset",
      "createdAt": "2026-03-14T10:30:00Z",
      "status": "READY"
    }
  ],
  "lastEvaluatedKey": {
    "userId": "user123",
    "imageId": "01HV9YJ6ZK9W4H7X2A"
  }
}
"""
def handler(event, context):
    """
    Lambda handler to list images for a specific user with pagination support.
    
    Expected Query Params:
        userId (str): Required. The owner of the images.
        limit (int): Optional. Number of items (default 20).
        lastKey (str): Optional. Base64-encoded JSON string for pagination.
    """
    image_service = get_image_service()
    try:
        query_params = event.get("queryStringParameters") or {}
        token = query_params.get("nextToken")
        last_key = None
        if token:
            last_key = decode_token(token)
        
        userId = query_params.get("userId")
        limit = query_params.get("limit", 20)
        #last_key = query_params.get("lastKey")
        
        if not userId:
            return {
                "statusCode": constants.HTTP_BAD_REQUEST,
                "body": json.dumps({"error": constants.ERR_MISSING_USER_ID})
            }
        # try converting limit to int
        try:
            limit = int(limit)
        except ValueError:
            return {
                "statusCode": constants.HTTP_BAD_REQUEST,
                "body": json.dumps({"error": constants.ERR_INVALID_LIMIT})
            }
        res = image_service.list_images(
            user_id= userId,
            limit= limit,
            last_key= last_key
        )
        
        return {
            "statusCode": constants.HTTP_OK,
            "body": json.dumps(res, default=str) # 'default=str' handles datetime objects
        }

    except Exception as e:
        return {
            "statusCode": constants.HTTP_INTERNAL_ERROR,
            "body": json.dumps({"error": constants.ERR_INTERNAL_SERVER, "details": str(e)})
        }
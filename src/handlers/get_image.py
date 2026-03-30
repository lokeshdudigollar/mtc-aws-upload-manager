import json

from src.utils.image_service_factory import get_image_service
import src.utils.constants as constants

"""
Example request: GET /images/user123/01HV9YJ6ZK9W4H7X2A
Example response:
{
  "imageId": "01HV9YJ6ZK9W4H7X2A",
  "title": "Sunset",
  "tags": ["nature"],
  "createdAt": "2026-03-14T10:30:00Z",
  "downloadUrl": "https://signed-url"
}

"""
def handler(event, context):
    """
    Lambda handler to retrieve image details (presigned URL).
    
    Path Parameters:
        userId (str): The owner ID.
        imageId (str): The specific image ID.
    """
    image_service = get_image_service()
    try:
        path_params = event.get("pathParameters") or {}

        user_id = path_params.get("userId")
        image_id = path_params.get("imageId")

        # Validate path parameters
        if not user_id or not image_id:
            return {
                "statusCode": constants.HTTP_BAD_REQUEST,
                "body": json.dumps({"error": constants.ERR_MISSING_USER_IMAGE_ID})
            }
        # Fetch image metadata and presigned URL
        res = image_service.get_image(
            user_id= user_id,
            image_id= image_id
        )
        
        return {
            "statusCode": constants.HTTP_OK,
            "body": json.dumps(res)
        }

    except ValueError as error:
        # Maps business logic 'not found' or 'not ready' to 404
        return {
            "statusCode": constants.HTTP_NOT_FOUND,
            "body": json.dumps({"error": str(error)})
        }

    except Exception:
        return {
            "statusCode": constants.HTTP_INTERNAL_ERROR,
            "body": json.dumps({"error": constants.ERR_INTERNAL_SERVER})
        }
import json

from src.utils.image_service_factory import get_image_service
import src.utils.constants as constants
from src.utils.validators import validate_image_request

"""
Example request: DELETE /images/user123/01HV9YJ6ZK9W4H7X2A
Example response:
204 No Content
"""
def handler(event, context):
    """
    Lambda handler to delete an image.
    
    Path Parameters:
        userId (str): The owner ID.
        imageId (str): The specific image ID.
    """
    image_service = get_image_service()
    try:
        path_params = event.get("pathParameters") or {}

        user_id = path_params.get("userId")
        image_id = path_params.get("imageId")

        try:
            # Validate path parameters
            validate_image_request(user_id, image_id)
        except ValueError as ve:
            return {
                "statusCode": constants.HTTP_BAD_REQUEST,
                "body": json.dumps({"error": str(ve)})
            }
        # Delete image
        res = image_service.delete_image(
            user_id= user_id,
            image_id= image_id
        )
        return {
            "statusCode": constants.HTTP_NO_CONTENT
        }

    except ValueError as error:
        return {
            "statusCode": constants.HTTP_NOT_FOUND,
            "body": json.dumps({"error": str(error)})
        }
    except Exception:
        return {
            "statusCode": constants.HTTP_INTERNAL_ERROR,
            "body": json.dumps({"error": constants.ERR_INTERNAL_SERVER})
        }
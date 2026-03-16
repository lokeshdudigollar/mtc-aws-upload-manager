import json

from src.utils.image_service_factory import get_image_service

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

        # Validate path parameters
        if not user_id or not image_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "userId and imageId are required"})
            }
        # Delete image
        res = image_service.delete_image(
            user_id= user_id,
            image_id= image_id
        )
        return {
            "statusCode": 204
        }

    except ValueError as error:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": str(error)})
        }
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
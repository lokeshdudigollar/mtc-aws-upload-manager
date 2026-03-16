from src.config import dynamodb, DYNAMO_TABLE
from boto3.dynamodb.conditions import Key
table = dynamodb.Table(DYNAMO_TABLE)


"""
Expample of item uploaded to dynamoDB
item = {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "imageId": "123e4567-e89b-12d3-a456-426614174000",
    "createdAt": "2022-01-01T00:00:00Z",
    "title": "image1",
    "tags": ["tag1", "tag2"],
    "status": "UPLOADING",
    "idempotencyKey": "123e4567-e89b-12d3-a456-426614174000"
}

Then updated to 
{
    "status": "READY",
    "s3Key": "images/{imageId}.jpg"
}

"""
class DynamoDBRepository:
    def __init__(self, table):
        self.table = table

    def get_by_idempotency_key(self, key):

        response = self.table.query(
            IndexName="IdempotencyKeyIndex",
            KeyConditionExpression=Key("idempotencyKey").eq(key),
            Limit=1
        )
        items = response.get("Items", [])
        if not items:
            return None
        return items[0]

    def save_metadata(self, item):
        """
        Stores a new metadata record in the DynamoDB table.
        sets ConditionExpression to avoid race condition
        if two requests arrive at the same time
        Args:
            item (dict): The dictionary containing the item attributes to save.
        """
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(imageId)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise
            else:
                raise e
        

    def update_metadata(self, user_id, image_id, update_expression, expression_attribute_values):
        """
        Updates an existing metadata record in the DynamoDB table.

        Args:
            user_id (str): The ID of the user.
            image_id (str): The ID of the image.
            update_expression (str): The update expression.
            expression_attribute_values (dict): The expression attribute values.
        """
        self.table.update_item(
            Key = {
                "userId": user_id,
                "imageId": image_id
            },
            UpdateExpression = update_expression,
            ExpressionAttributeNames={"#s": "status"}, # Added to handle reserved keyword
            ExpressionAttributeValues = expression_attribute_values
        )

    def get_image_metadata(self, user_id, image_id):
        """
        Fetches metadata for a specific image.

        Args:
            user_id (str): The ID of the user.
            image_id (str): The ID of the image.

        Returns:
            dict or None: The item attributes if found, else None.
        """
        image_metadata_response = self.table.get_item(
            Key = {
                "userId": user_id,
                "imageId": image_id
            }
        )

        return image_metadata_response.get("Item")

    def list_images(self, user_id, limit=20, last_key=None):
        """
        Queries and lists images associated with a specific user.

        Args:
            user_id (str): The ID of the user.
            limit (int, optional): Max number of items to return. Defaults to 20.
            last_key (dict, optional): The ExclusiveStartKey for pagination.

        Returns:
            dict: A dictionary containing 'items' (list) and 'last_key' (dict/None).
        """
        query_params = {
            "KeyConditionExpression": Key("userId").eq(user_id), #Key("userId").eq(uid),  #"userId = :uid"
            "Limit": limit
        }

        if last_key:
            query_params["ExclusiveStartKey"] = last_key
        
        res = self.table.query(**query_params)
        
        return {
            "items": res.get("Items", []),
            "last_key": res.get("LastEvaluatedKey")
        }
    
    def delete_image_metadata(self, user_id, image_id):
        """
        Deletes the metadata record for a specific image from the table.

        Args:
            user_id (str): The ID of the user.
            image_id (str): The ID of the image.
        """
        self.table.delete_item(
            Key = {
                "userId": user_id,
                "imageId": image_id
            }
        )
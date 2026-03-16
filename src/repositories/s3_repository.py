#from src.config import s3, S3_BUCKET

class S3Repository:
    def __init__(self, s3_client, bucket_name):
        self.s3 = s3_client
        self.bucket_name = bucket_name
    
    def upload_image(self, file_bytes, image_id, content_type):
        """
        Uploads image content to an S3 bucket.

        Args:
            file_bytes (bytes): The raw file data to upload.
            s3_key (str): The full path/key where the file will be stored.
            content_type (str): The MIME type of the file (e.g., 'image/jpeg').

        Returns:
            str: The s3_key of the uploaded file.
        """
        s3_key = f"images/{image_id}" # extension for image not attacched to accomodate all types
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type
        )
        return s3_key

    def delete_image(self, s3_key):
        """
        Deletes image from S3.

        Args:
            s3_key (str): The path of the image to delete.
        """
        self.s3.delete_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )

    def generate_presigned_url(self, s3_key, expiration=3600):
        """
        Generates a secure, time-limited URL for downloading image.

        Args:
            s3_key (str): The path of the image.
            expiration (int): Time in seconds before the URL expires. Defaults to 3600.

        Returns:
            str: The pre-signed URL.
        """
        url = self.s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name, 
                "Key": s3_key
            },
            ExpiresIn=expiration
        )
        # replace localstack url with localhost to enable browser view
        url = url.replace("localstack:4566", "localhost:4566")
        return url
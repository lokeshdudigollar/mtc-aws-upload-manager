# Upload Statuses
STATUS_UPLOADING = "UPLOADING"
STATUS_READY = "READY"
STATUS_ERROR = "ERROR"

# Validation
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# Error Messages
ERR_MISSING_BODY = "Request body is empty"
ERR_MISSING_USER_ID = "userId header is required"
ERR_MISSING_USER_IMAGE_ID = "userId and imageId are required"
ERR_UNSUPPORTED_FILE = "Unsupported file type"
ERR_FILE_TOO_LARGE = "File size exceeds the limit of 5MB"
ERR_INVALID_LIMIT = "limit must be a number"
ERR_MISSING_FILE = "image file is required"
ERR_IMAGE_NOT_FOUND = "image not found"
ERR_IMAGE_NOT_AVAILABLE = "Image not available"
ERR_S3_KEY_MISSING = "Image storage path missing"
ERR_INTERNAL_SERVER = "Internal server error"
ERR_BAD_REQUEST = "Bad request error"
ERR_S3_STORAGE_KEY_ERROR = "Image storage path missing"

DEFAULT_EXPIRATION = 3600 # 1 hour
MIN_EXPIRATION = 60 # 1 minute
MAX_EXPIRATION = 86400 # 24 hours

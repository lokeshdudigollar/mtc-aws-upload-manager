import src.utils.constants as const

def validate_user_id(user_id):
    if not user_id:
        raise ValueError(const.ERR_MISSING_USER_ID)

def validate_image_request(user_id, image_id):
    if not user_id or not image_id:
        raise ValueError(const.ERR_MISSING_USER_IMAGE_ID)

def validate_upload(body, user_id, content_type, file_bytes):
    if not body:
        raise ValueError(const.ERR_MISSING_BODY)
    validate_user_id(user_id)
    if content_type not in const.ALLOWED_CONTENT_TYPES:
        raise ValueError(const.ERR_UNSUPPORTED_FILE)
    if len(file_bytes) > const.MAX_IMAGE_SIZE_BYTES:
        raise ValueError(const.ERR_FILE_TOO_LARGE)
    if not file_bytes:
        raise ValueError(const.ERR_MISSING_FILE)

def validate_pagination_limit(limit):
    try:
        return int(limit)
    except ValueError:
        raise ValueError(const.ERR_INVALID_LIMIT)

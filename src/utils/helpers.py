import ulid
import datetime
import hashlib
import base64
import json

def generate_image_id():
    """Generates a ULID string for high-performance sorting/uniqueness."""
    return str(ulid.new())

def get_current_timestamp():
    """Returns the current UTC timestamp in ISO format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def generate_idempotency_key(file_bytes, user_id):
    """Generates a SHA-256 hash to prevent duplicate uploads."""
    raw = file_bytes + user_id.encode()
    return hashlib.sha256(raw).hexdigest()

def encode_token(key):
    """Encodes a DynamoDB LastEvaluatedKey dictionary into a base64 token string."""
    return base64.b64encode(json.dumps(key).encode()).decode()

def decode_token(token):
    """Decodes a base64 token string back into a DynamoDB ExclusiveStartKey dictionary."""
    return json.loads(base64.b64decode(token).decode())

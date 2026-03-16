import base64
import json

def encode_token(key):
    return base64.b64encode(json.dumps(key).encode()).decode()

def decode_token(token):
    return json.loads(base64.b64decode(token).decode())
import ulid

def generate_image_id():
    return str(ulid.new())
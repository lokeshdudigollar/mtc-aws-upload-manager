# API Documentation


### API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/images` | Upload image |
| GET | `/images` | List images |
| GET | `/images/{image_id}` | View image |
| DELETE | `/images/{image_id}` | Delete image |



### Supported Image Formats

- JPEG/JPG
- PNG

### File Size Limits

- **Maximum**: 10 MB per image

### Error Codes

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 403 | Forbidden (invalid API key) |
| 404 | Not Found (resource doesn't exist) |
| 500 | Internal Server Error |

# APIs

## Upload Image
Uploads a binary image file and creates a metadata record in the system.

- Endpoint: `POST /images`
- Headers:
    - `userId`: (Required) The unique identifier of the user.

    - `title`: (Required) A descriptive name for the image.

    - `fileName`: (Required) Original name of the file.

    - `Content-Type`: image/jpeg or image/png
- Body: Binary image data

**Example request**
```
curl --location 'http://localhost:4566/restapis/yojqtb9pqw/dev/_user_request_/images' \
--header 'userId: user003' \
--header 'Content-Type: image/jpeg' \
--header 'title: My Test Image3' \
--header 'fileName: test003.jpg' \
--data-binary '@postman-cloud:///1f12cfcd-21d4-43b0-a84d-c947b4c7dd34'
```

**Success Response:**
- Code: `201 Created`
- Content:
```
{
    "userId": "user003",
    "imageId": "01KNFG6GM4BSZ0GMZ3PRX1SHB8",
    "createdAt": "2026-04-05T18:59:02.405003+00:00",
    "status": "READY",
    "title": "My Test Image3",
    "tags": [],
    "s3Key": "images/01KNFG6GM4BSZ0GMZ3PRX1SHB8",
    "idempotencyKey": null
}
```

## List Images
Retrieves a paginated list of all images belonging to a specific user.
- Endpoint: `GET /images`
- Query Parameters:
    - `userId`: (Required) The ID of the user whose images you want to retrieve.

**Example request**
```
curl --location 'http://localhost:4566/restapis/yojqtb9pqw/dev/_user_request_/images?userId=user003'
```
**Success Response:**
- Code: `200 OK`
- Content:
```
{
    "items": [
        {
            "createdAt": "2026-04-05T18:59:02.405003+00:00",
            "imageId": "01KNFG6GM4BSZ0GMZ3PRX1SHB8",
            "s3Key": "images/01KNFG6GM4BSZ0GMZ3PRX1SHB8",
            "idempotencyKey": "ebb4891abf34...",
            "title": "My Test Image3",
            "userId": "user003",
            "status": "READY",
            "tags": []
        }
    ],
    "nextToken": null
}
```

## Get Image Details
Retrieves metadata for a specific image, including a temporary presigned URL for downloading the file directly from storage.

- Endpoint: `GET /images/{userId}/{imageId}`
- Path Parameters:
    - `userId`: The unique identifier of the user.
    - `imageId`: The unique identifier of the image.

**example request**
```
curl --location 'http://localhost:4566/restapis/yojqtb9pqw/dev/_user_request_/images/user003/01KNFG6GM4BSZ0GMZ3PRX1SHB8'
```

**Success Response:**
- Code: `200 OK`
- Content:
```
{
    "imageId": "01KNFG6GM4BSZ0GMZ3PRX1SHB8",
    "title": "My Test Image3",
    "downloadURL": "http://localhost:4566/image-bucket/images/01KNFG6GM4BSZ0GMZ3PRX1SHB8?..."
}
```

## Delete Image
Removes an image and its associated metadata from the system.

- Endpoint: `DELETE /images/{userId}/{imageId}`
- Path Parameters:
    - `userId`: The unique identifier of the user.
    - `imageId`: The unique identifier of the image.

**Success Response:**
- Code: `204 No Content`
- Content: (Empty)
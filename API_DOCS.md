# API Documentation


### API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/images` | Upload image | Yes |
| GET | `/images` | List images | Yes |
| GET | `/images/{image_id}` | View image | Yes |
| DELETE | `/images/{image_id}` | Delete image | Yes |



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

### Example Requests

```
curl -X POST \
http://localhost:4566/restapis/{API\*ID}/dev/\_user*request*/images \
-H "userId: user123" \
-H "title: My Test Image" \
-H "fileName: test.jpg" \
-H "Content-Type: image/jpeg" \
--data-binary @test.jpg
```

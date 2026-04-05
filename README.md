# Image Service Manager

This project implements a scalable, serverless image management service using:

- AWS Lambda (compute)
- API Gateway (HTTP interface)
- DynamoDB (metadata store)
- S3 (object storage)

The system supports:
```
* Image upload
* Image listing (paginated)
* Secure image retrieval via presigned URLs
* Image deletion (idempotent)
```

The project is fully runnable locally using LocalStack.

# Architecture Overview
       ┌──────────────────┐
       │      Client      │
       │ (Postman/Browser)│
       └────────┬─────────┘
                │
              HTTP
                ▼
       ┌──────────────────┐
       │   API Gateway    │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ Lambda Handlers  │
       └────────┬─────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
    ┌─────────────┐   ┌─────────────┐
    │  DynamoDB   │   │     S3      │
    │  Metadata   │   │ Image File  │
    └─────────────┘   └─────────────┘

# System Components:

- API Gateway HTTP entry point
- Lambda Executes business logic
- DynamoDB Stores image metadata
- S3 Stores image files
- LocalStack Simulates AWS services locally

# DynamoDB Table Design

**Table: Images**

| Field | Key Type | Description |
| :--- | :--- | :--- |
| `userId` | **Partition Key** | Unique identifier for the user |
| `imageId` | **Sort Key** | Unique identifier for the image |
| `createdAt` | — | Upload timestamp |
| `title` | — | Image title |
| `tags` | — | Image tags |
| `status` | — | Upload status |
| `s3Key` | — | S3 object key |
| `idempotencyKey` | — | Prevents duplicate uploads |

## Global Secondary Index
```
Used for idempotent uploads.

IndexName: IdempotencyKeyIndex
PartitionKey: idempotencyKey
```

# API Design:

### API Base URL

`
http://localhost:4566/restapis/{API_ID}/dev/_user_request_
`

### Upload Image

`POST /images`

**Headers**
```
userId
title
fileName
Content-Type
```

**Body**
```
Binary image file
```

**Response[201 created]**
```
{
"imageId": "01KKRS9QFVA0GNKEKY7FP3JXXS",
"status": "READY"
}
```

**Error codes**
- 400: Bad request
- 500 : Internal Server Error

### List Images

`GET /images?userId={userId}&limit=2&nextToken=...`

**Response[200 OK]**
```
{
"items": [...],
"nextToken": null
}
```
**Error codes**
- 400: Bad request
- 500 : Internal Server Error

### Get Image

`GET /images/{userId}/{imageId}`

**Response[200 OK]**
```
{
"imageId": "...",
"title": "...",
"downloadURL": "presigned S3 URL"
}
```

**Error codes**
- 400: Bad request
- 404: Image not found
- 500 : Internal Server Error

### Delete Image

`DELETE /images/{userId}/{imageId}`

**Response**

`204 No Content`

**Error codes**
- 400: Bad request
- 404: Image not found
- 500 : Internal Server Error

# Project Structure
```
image-service/
│
├── src/
│ ├── handlers/
│ │ ├── upload_image.py
│ │ ├── list_images.py
│ │ ├── get_image.py
│ │ └── delete_image.py
│ │
│ ├── services/
│ │ └── image_service.py
│ │
│ ├── repositories/
│ │ ├── dynamodb_repository.py
│ │ └── s3_repository.py
│ │
│ ├── models/
│ │ └── image_model.py
│ │
│ └── utils/
│ └── pagination.py
│ └── image_service_factory.py
│ 
|
├── scripts/
│ ├── package.ps1
│ ├── build-layer.ps1
│ └── setup_localstack.ps1
│ └── start.ps1
│ └── watch.ps1
|
├── requirements.txt
├── docker-compose.yml
└── README.md
```
# How to Run the Project Locally

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for LocalStack)
  - Docker Desktop (includes `docker compose` v2) - Recommended
  - OR standalone `docker-compose` v1
- AWS CLI (for LocalStack setup and AWS deployment)

### 1. Install dependencies
` pip install requirements.txt`

### 2. create env file

### 3.  AWS setup
Just run start.ps1(./scripts/start.ps1)

1. it will run docker setup

2. create packages
   ./scripts/package.ps1

3. setup localstack
   ./scripts/setup_localstack.ps1

4. deploys lambda
   ```
   awslocal lambda update-function-code \
   --function-name upload-image \
   --zip-file fileb://lambda.zip
   ```
5. Creates and deploys API gateway

### 4. Run the APIs in Postman

### 5. Running tests
Run this command in terminal `pytest`

if you want to view coverage run `pytest --cov=src`

# Techstack Used:

- Python 3.11
- AWS Lambda
- API Gateway
- DynamoDB
- S3
- LocalStack
- boto3

# Key design decisions and Trade offs
### 1. S3 vs DynamoDB for image storage
Current design: Store images in S3 and metadata in DynamoDB
why?
- DynamoDB has 400KB limit
- S3 optimized for large binary storage
- Keeps DB queries fast

### 2. Lambda upload vs Presigned upload
Current Design: Client -> Lambda -> S3

Why?
- Simpler and Controlled

Cons:
- Higher latency

Alternative: Client -> Presigned Url -> S3

Why?
- Scalable and faster

Cons:
- A bit more complex than current


### 3. API Design choice:
Current: /images

Why:
- Easy to implement for assigment purpose

Alternative: `/users/{userId}/images`

Why?
- hierarchical design is more scalable

### Idempotency

The system ensures safe retries using:

- SHA256(userId + fileBytes) → idempotencyKey
- DynamoDB GSI lookup
- Conditional writes

**Why:**
- Prevents duplicate uploads under retries and concurrent requests

## Concurrency Handling

- Idempotency keys prevent logical duplication
- DynamoDB conditional writes prevent race conditions


## Scalability considerations:

### Lambda
- scales per request[horizontal scaling]
- No infra management


### DynamoDB
- Partitions based scaling
- Handles high throughput automatically

### API Gateway
10,000 requests/second (soft limit, can be increased)

### S3
Almost unlimited storage

## System Limitations:
- Hot partition risk if a single user generates high traffic
- Lambda concurrency limits (1000 by default)
- Synchronous upload increases latency
- Lambda cold starts can add latency[**can use provisioned concurrency to overcome**]


# Future Improvements:

- Generate image thumbnails
- Add authentication (JWT / Cognito)
- Introduce SQS for async image processing
`
Client → Lambda → SQS → Worker Lambda → S3
`

- Add CDN (CloudFront) for image delivery
- Add image validation and compression


# Troubleshooting

### LocalStack Issues

- **Port conflicts**: Ensure port 4566 is not in use
- **Resource creation fails**: Check LocalStack logs: `docker logs localstack`
- **Connection errors**: Verify LocalStack is running: `curl http://localhost:4566/_localstack/health`

### Lambda Issues

- **Timeout errors**: Increase Lambda timeout
- **Memory errors**: Increase Lambda memory allocation
- **Permission errors**: Check IAM role policies

### API Gateway Issues

- **403 errors**: Verify API key is correct
- **CORS errors**: Check CORS configuration
- **502 errors**: Check Lambda function logs in CloudWatch


### Checking logs for localstack

get all logs from localstack
`docker logs -f localstack> `

get logs for a specific lambda
`docker logs localstack 2>&1 | Select-String "upload-image"`

check localstack health
`check health: http://localhost:4566/_localstack/health`

get logs from log group
`awslocal logs describe-log-streams /aws/lambda/list-images`

## AWS commands
### dynamoDB
scan a dynamoDB table
`awslocal dynamodb scan --table-name Images`

list dynamodb tables
`awslocal dynamodb list-tables`

### Lambda create
```
awslocal lambda create-function `
--function-name upload-image `
--runtime python3.11 `
--role arn:aws:iam::000000000000:role/lambda-role `
--handler src.handlers.upload_image.handler `
--zip-file fileb://lambda.zip

```

### lambda update
update lambda code
```
awslocal lambda update-function-code `
--function-name list-images `
--zip-file fileb://lambda.zip
```

Update lambda configuration
```
awslocal lambda update-function-configuration `
  --function-name list-images `
  --timeout 300
```

### lambda invoke manually
```
awslocal lambda invoke `
--function-name upload-image `
--payload file://event.json `
response.json
```

### awslocal
Get all APIs
`awslocal apigateway get-rest-apis`

Get all lambdas created
`awslocal lambda list-functions`

Get s3 bucket names
`awslocal s3 ls`

Get all content of a bucket
`awslocal s3 ls s3://image-bucket/ --recursive`



### Image Service API

---

A serverless image management API built using AWS Lambda, API Gateway, DynamoDB, and S3.
The service supports uploading images, listing images, retrieving images via presigned URLs, and deleting images.

The project runs locally using LocalStack, allowing AWS services to be simulated without deploying to AWS.

## Architecture Overview

┌─────────────┐
│ Client │
│ (Postman / │
│ Browser) │
└──────┬──────┘
│ HTTP
▼
┌─────────────┐
│ API Gateway │
└──────┬──────┘
│
▼
┌─────────────┐
│ Lambda │
│ Handlers │
└──────┬──────┘
│
┌────────┴────────┐
▼ ▼
┌─────────────┐ ┌─────────────┐
│ DynamoDB │ │ S3 │
│ Metadata │ │ Image File │
└─────────────┘ └─────────────┘

## System Components:

# Component Purpose

API Gateway HTTP entry point
Lambda Executes business logic
DynamoDB Stores image metadata
S3 Stores image files
LocalStack Simulates AWS services locally

## DynamoDB Table Design

# Table: Images

# Attribute Description

userId Partition Key
imageId Sort Key
createdAt Upload timestamp
title Image title
tags Image tags
status Upload status
s3Key S3 object key
idempotencyKey Prevents duplicate uploads

## Global Secondary Index

Used for idempotent uploads.

IndexName: IdempotencyKeyIndex
PartitionKey: idempotencyKey

## API Endpoints:

# Upload Image

POST /images

Headers:
userId
title
fileName
Content-Type

Body:
Binary image file

Response:

{
"imageId": "01KKRS9QFVA0GNKEKY7FP3JXXS",
"status": "READY"
}

# List Images

GET /images?userId={userId}

Response:

{
"items": [...],
"nextToken": null
}

# Get Image

GET /images/{userId}/{imageId}

Response:

{
"imageId": "...",
"title": "...",
"downloadURL": "presigned S3 URL"
}

# Delete Image

DELETE /images/{userId}/{imageId}

Response:

204 No Content

## Project Structure

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
│ └── id_generator.py
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

## Running the Project Locally

Just run start.ps1

1. it will run docker setup

2. create packages
   ./scripts/package.ps1

3. setup localstack
   ./scripts/setup_localstack.ps1

4. deploy lambda
   awslocal lambda update-function-code \
   --function-name upload-image \
   --zip-file fileb://lambda.zip

** Repeat for other Lambda functions **

## API Base URL

http://localhost:4566/restapis/{API\*ID}/dev/\_user*request*

## Example Requests

Upload Image
curl -X POST \
http://localhost:4566/restapis/{API\*ID}/dev/\_user*request*/images \
-H "userId: user123" \
-H "title: My Test Image" \
-H "fileName: test.jpg" \
-H "Content-Type: image/jpeg" \
--data-binary @test.jpg

# Status Lifecycle for upload image

UPLOADING → READY → DELETED

If an upload fails:

UPLOADING → ERROR

## Technologies Used:

Python 3.11
AWS Lambda
API Gateway
DynamoDB
S3
LocalStack
boto3

## TEST COVERAGE

## Name Stmts Miss Cover Missing

src\_\_init**.py 0 0 100%
src\config.py 8 0 100%
src\handlers\_\_init**.py 0 0 100%
src\handlers\delete_image.py 18 0 100%
src\handlers\get_image.py 18 0 100%
src\handlers\list_images.py 28 3 89% 73-75
src\handlers\upload_image.py 37 3 92% 19, 46, 50
src\models\image_model.py 10 0 100%
src\repositories\_\_init**.py 0 0 100%
src\repositories\dynamodb_repository.py 34 15 56% 31-39, 66, 108-119, 132
src\repositories\s3_repository.py 14 1 93% 35
src\services\_\_init**.py 0 0 100%
src\services\image_service.py 75 20 73% 34, 36, 76, 148-160,170-182
src\utils\_\_init\_\_.py 0 0 100%
src\utils\id_generator.py 4 4 0% 1-6
src\utils\image_service_factory.py 5 1 80% 6
src\utils\pagination.py 6 1 83% 8

---

TOTAL 257 48 81%
========= 25 passed ===============

## Future Improvements:

Generate image thumbnails

Add authentication (JWT / Cognito)

Introduce SQS for async image processing

Add CDN (CloudFront) for image delivery

Add image validation and compression

Write-Host "Setting up LocalStack resources..."

$REGION="us-east-1"

# -------------------------
# Create S3 Bucket
# -------------------------
Write-Host "Creating S3 bucket..."

awslocal s3 mb s3://image-bucket 2>$null

# -------------------------
# Create DynamoDB Table
# -------------------------
Write-Host "Creating DynamoDB table..."

awslocal dynamodb create-table `
--table-name Images `
--attribute-definitions `
AttributeName=userId,AttributeType=S `
AttributeName=imageId,AttributeType=S `
AttributeName=idempotencyKey,AttributeType=S `
--key-schema `
AttributeName=userId,KeyType=HASH `
AttributeName=imageId,KeyType=RANGE `
--global-secondary-indexes `
"[{
\"IndexName\":\"IdempotencyKeyIndex\",
\"KeySchema\":[{\"AttributeName\":\"idempotencyKey\",\"KeyType\":\"HASH\"}],
\"Projection\":{\"ProjectionType\":\"ALL\"}
}]" `
--billing-mode PAY_PER_REQUEST `
2>$null

# -------------------------------------------------------
# If above command does not create the dynamoDB with GSI
# -------------------------------------------------------
Write-Host "Create the file with explicit formatting that PowerShell won't touch"

$gsiJson = @'
[
  {
    "IndexName": "IdempotencyKeyIndex",
    "KeySchema": [
      {
        "AttributeName": "idempotencyKey",
        "KeyType": "HASH"
      }
    ],
    "Projection": {
      "ProjectionType": "ALL"
    }
  }
]
'@

$gsiJson | Out-File -FilePath gsi.json -Encoding ascii

Write-Host "Now call it using the file parameter"

awslocal dynamodb create-table `
    --table-name Images `
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=imageId,AttributeType=S AttributeName=idempotencyKey,AttributeType=S `
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=imageId,KeyType=RANGE `
    --global-secondary-indexes file://gsi.json `
    --billing-mode PAY_PER_REQUEST
2>$null

# -------------------------
# Create Lambda Functions
# -------------------------
Write-Host "Creating Lambda functions..."

$ROLE="arn:aws:iam::000000000000:role/lambda-role"

awslocal lambda create-function `
--function-name upload-image `
--runtime python3.11 `
--role $ROLE `
--handler src.handlers.upload_image.handler `
--zip-file fileb://lambda.zip `
2>$null

awslocal lambda create-function `
--function-name list-images `
--runtime python3.11 `
--role $ROLE `
--handler src.handlers.list_images.handler `
--zip-file fileb://lambda.zip `
2>$null

awslocal lambda create-function `
--function-name get-image `
--runtime python3.11 `
--role $ROLE `
--handler src.handlers.get_image.handler `
--zip-file fileb://lambda.zip `
2>$null

awslocal lambda create-function `
--function-name delete-image `
--runtime python3.11 `
--role $ROLE `
--handler src.handlers.delete_image.handler `
--zip-file fileb://lambda.zip `
2>$null

# -------------------------
# Create API Gateway
# -------------------------
Write-Host "Creating API Gateway..."

$api = awslocal apigateway create-rest-api --name image-api | ConvertFrom-Json
$API_ID = $api.id

$resources = awslocal apigateway get-resources --rest-api-id $API_ID | ConvertFrom-Json
$ROOT_ID = $resources.items[0].id

$images = awslocal apigateway create-resource `
--rest-api-id $API_ID `
--parent-id $ROOT_ID `
--path-part images | ConvertFrom-Json

$IMAGES_ID = $images.id

# POST /images → upload-image
awslocal apigateway put-method `
--rest-api-id $API_ID `
--resource-id $IMAGES_ID `
--http-method POST `
--authorization-type NONE

awslocal apigateway put-integration `
--rest-api-id $API_ID `
--resource-id $IMAGES_ID `
--http-method POST `
--type AWS_PROXY `
--integration-http-method POST `
--uri arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:000000000000:function:upload-image/invocations

# Deploy API
awslocal apigateway create-deployment `
--rest-api-id $API_ID `
--stage-name dev

Write-Host "Setup complete!"
Write-Host ""
Write-Host "API Endpoint:"
Write-Host "http://localhost:4566/restapis/$API_ID/dev/_user_request_/images"
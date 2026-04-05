# -------------------------
# Set Environment Variables for LocalStack
# -------------------------
$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="us-east-1"

Write-Host "Setting up LocalStack resources in $env:AWS_DEFAULT_REGION..."

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

# Array of functions with specific metadata
$functions = @(
    @{ name="upload-image"; handler="src.handlers.upload_image.handler"; timeout=3000 },
    @{ name="list-images";  handler="src.handlers.list_images.handler";  timeout=3000 },
    @{ name="get-image";   handler="src.handlers.get_image.handler";   timeout=3000 },
    @{ name="delete-image"; handler="src.handlers.delete_image.handler"; timeout=3000 }
)

foreach ($func in $functions) {
    Write-Host "Creating Lambda function: $($func.name)"
    awslocal lambda create-function `
    --function-name $func.name `
    --runtime python3.11 `
    --role $ROLE `
    --handler $func.handler `
    --zip-file fileb://lambda.zip `
    --timeout $func.timeout `
    2>$null
}

Write-Host "successfully created lambda functions..."
# -------------------------
# Create API Gateway
# -------------------------
Write-Host "Creating API Gateway..."

# 1. Create the API
$api = awslocal apigateway create-rest-api --name montycloud-image-service | ConvertFrom-Json
$API_ID = $api.id

# 2. Get Root Resource ID
$resources = awslocal apigateway get-resources --rest-api-id $API_ID | ConvertFrom-Json
$ROOT_ID = $resources.items[0].id

# 3. Create resources

# Create /images resource to get IMAGE ID
$images = awslocal apigateway create-resource `
--rest-api-id $API_ID `
--parent-id $ROOT_ID `
--path-part images | ConvertFrom-Json

$IMAGES_ID = $images.id

# -- create resources for dynamic user and image id --

# create images/{userId}
$userId = awslocal apigateway create-resource `
--rest-api-id $API_ID `
--parent-id $IMAGES_ID `
--path-part "{userId}" | ConvertFrom-Json

$USER_ID = $userId.id

# create images/{userId}/{imageId}
$imageId = awslocal apigateway create-resource `
--rest-api-id $API_ID `
--parent-id $USER_ID `
--path-part "{imageId}" | ConvertFrom-Json

$DYNAMIC_IMAGE_ID = $imageId.id

# 4. Create Methods for the lambdas

# POST /images
awslocal apigateway put-method `
--rest-api-id $API_ID `
--resource-id $IMAGES_ID `
--http-method POST `
--authorization-type "NONE"

# GET list-images
awslocal apigateway put-method `
--rest-api-id $API_ID `
--resource-id $IMAGES_ID `
--http-method GET `
--authorization-type NONE

# GET /images/{imageId}
awslocal apigateway put-method `
--rest-api-id $API_ID `
--resource-id $DYNAMIC_IMAGE_ID `
--http-method GET `
--authorization-type "NONE"

# DELETE /images/{imageId}/{userId}
awslocal apigateway put-method `
--rest-api-id $API_ID `
--resource-id $DYNAMIC_IMAGE_ID `
--http-method DELETE `
--authorization-type NONE

# 5. Build the urls

# use $env:AWS_DEFAULT_REGION to match global config
$CURRENT_REGION = $env:AWS_DEFAULT_REGION
write-Host "Building url for api gateway deploy: $($CURRENT_REGION)"
# Build the Lambda ARN and the Gateway-to-Lambda URI for all lambdas
$UPLOAD_LAMBDA_ARN = "arn:aws:lambda:$($CURRENT_REGION):000000000000:function:upload-image"
$LIST_LAMBDA_ARN = "arn:aws:lambda:$($CURRENT_REGION):000000000000:function:list-images"
$GET_LAMBDA_ARN = "arn:aws:lambda:$($CURRENT_REGION):000000000000:function:get-image"
$DELETE_LAMBDA_ARN = "arn:aws:lambda:$($CURRENT_REGION):000000000000:function:delete-image"

$UPLOAD_INTEGRATION_URI = "arn:aws:apigateway:$($CURRENT_REGION):lambda:path/2015-03-31/functions/$($UPLOAD_LAMBDA_ARN)/invocations"
$LIST_INTEGRATION_URI = "arn:aws:apigateway:$($CURRENT_REGION):lambda:path/2015-03-31/functions/$($LIST_LAMBDA_ARN)/invocations"
$GET_INTEGRATION_URI = "arn:aws:apigateway:$($CURRENT_REGION):lambda:path/2015-03-31/functions/$($GET_LAMBDA_ARN)/invocations"
$DELETE_INTEGRATION_URI = "arn:aws:apigateway:$($CURRENT_REGION):lambda:path/2015-03-31/functions/$($DELETE_LAMBDA_ARN)/invocations"


# 6. adding permissions

# Grant API Gateway permission to invoke the upload Lambda
awslocal lambda add-permission `
    --function-name upload-image `
    --statement-id apigateway-access `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    2>$null

# Grant API Gateway permission to invoke the list Lambda
awslocal lambda add-permission `
    --function-name list-images `
    --statement-id apigateway-access `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    2>$null

# Grant API Gateway permission to invoke the get Lambda
awslocal lambda add-permission `
    --function-name get-image `
    --statement-id apigateway-access `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    2>$null

# Grant API Gateway permission to invoke the delete Lambda
awslocal lambda add-permission `
    --function-name delete-image `
    --statement-id apigateway-access `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    2>$null


# 7. create api integrations for the lambdas

Write-Host "Linking Lambdas to API Gateway..."

#upload-image
awslocal apigateway put-integration `
--rest-api-id $API_ID `
--resource-id $IMAGES_ID `
--http-method POST `
--type AWS_PROXY `
--integration-http-method POST `
--uri $UPLOAD_INTEGRATION_URI

# Give LocalStack a second to settle the integration
Start-Sleep -Seconds 1

# list-images
awslocal apigateway put-integration `
--rest-api-id $API_ID `
--resource-id $IMAGES_ID `
--http-method GET `
--type AWS_PROXY `
--integration-http-method POST `
--uri $LIST_INTEGRATION_URI

# Give LocalStack a second to settle the integration
Start-Sleep -Seconds 2

# get-image
awslocal apigateway put-integration `
--rest-api-id $API_ID `
--resource-id $DYNAMIC_IMAGE_ID `
--http-method GET `
--type AWS_PROXY `
--integration-http-method POST `
--uri $GET_INTEGRATION_URI

# Give LocalStack a second to settle the integration
Start-Sleep -Seconds 2

# delete-image
awslocal apigateway put-integration `
--rest-api-id $API_ID `
--resource-id $DYNAMIC_IMAGE_ID `
--http-method DELETE `
--type AWS_PROXY `
--integration-http-method POST `
--uri $DELETE_INTEGRATION_URI

# Give LocalStack a second to settle the integration
Start-Sleep -Seconds 2


# 8. Deploy API
Write-Host "Deploying API to 'dev' stage for app: $API_ID"
awslocal apigateway create-deployment `
--rest-api-id $API_ID `
--stage-name dev

Write-Host "Setup complete!"
Write-Host ""
Write-Host "API Endpoint:"
Write-Host "http://localhost:4566/restapis/$API_ID/dev/_user_request_/images"
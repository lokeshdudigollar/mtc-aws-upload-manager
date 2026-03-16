Write-Host "Starting Image Service Environment..."

# Start LocalStack
Write-Host "Starting LocalStack..."
docker-compose up -d

Start-Sleep -Seconds 5

# Package Lambda
Write-Host "Packaging Lambda..."
.\scripts\package.ps1

# Setup AWS resources
Write-Host "Setting up AWS resources..."
.\scripts\setup_localstack.ps1

Write-Host ""
Write-Host "Environment Ready!"
Write-Host ""
Write-Host "API endpoint:"
Write-Host "http://localhost:4566/restapis/{API_ID}/dev/_user_request_/images"
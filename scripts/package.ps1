Write-Host "Starting Lambda packaging..."

# 1. Clean previous builds
Write-Host "Cleaning old build files..."
if (Test-Path "package") { Remove-Item "package" -Recurse -Force }
if (Test-Path "lambda.zip") { Remove-Item "lambda.zip" -Force }

# 2. Install dependencies (Manual Step 1)
Write-Host "Installing dependencies to ./package..."
# Using ulid-py specifically as per your manual steps
pip install -r requirements.txt -t package

# 3. Create zip package (Manual Step 2)
Write-Host "Creating lambda.zip from src and package..."
# This command takes the CONTENTS of both folders and puts them at the root of the zip
Compress-Archive -Path src,package\* -DestinationPath lambda.zip

Write-Host "Lambda package created successfully!"
Write-Host "Output: lambda.zip"
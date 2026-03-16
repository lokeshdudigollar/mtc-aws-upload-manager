Write-Host "Starting Lambda packaging..."

# Clean previous builds
Write-Host "Cleaning old build..."
Remove-Item build -Recurse -Force -ErrorAction Ignore
Remove-Item lambda.zip -ErrorAction Ignore

# Create build directory
Write-Host "Creating build directory..."
New-Item -ItemType Directory -Path build | Out-Null

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt -t build

# Copy source code
Write-Host "Copying source code..."
Copy-Item src -Recurse build

# Create zip package
Write-Host "Creating lambda.zip..."
Compress-Archive -Path build\* -DestinationPath lambda.zip -Force

Write-Host "Lambda package created successfully!"
Write-Host "Output: lambda.zip"
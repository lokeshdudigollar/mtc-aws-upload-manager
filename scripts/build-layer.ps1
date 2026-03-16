# discared due to insufficient time
Write-Host "Building Lambda Layer..."

Remove-Item layer -Recurse -Force -ErrorAction Ignore
Remove-Item layer.zip -ErrorAction Ignore

New-Item -ItemType Directory -Path layer/python | Out-Null

pip install -r requirements.txt -t layer/python

Compress-Archive -Path layer\* -DestinationPath layer.zip -Force

Write-Host "Layer created: layer.zip"

## if you want to execute this
## first run this
## then create a layer in local stack and save the ARN
## Attach the layer to lambda
## This will load the dependecies
## simplify the package.ps1 to just zip the code
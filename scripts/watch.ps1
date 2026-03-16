Write-Host "Watching for changes..."

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "src"
$watcher.Filter = "*.py"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

function Deploy-Lambda($file) {

    if ($file -like "*upload_image.py") {
        $function = "upload-image"
    }
    elseif ($file -like "*list_images.py") {
        $function = "list-images"
    }
    elseif ($file -like "*get_image.py") {
        $function = "get-image"
    }
    elseif ($file -like "*delete_image.py") {
        $function = "delete-image"
    }
    else {
        # service / repository changes affect all lambdas
        $function = "all"
    }

    Write-Host "File changed: $file"

    & "$PSScriptRoot/package.ps1"

    if ($function -eq "all") {

        Write-Host "Updating all lambdas..."

        awslocal lambda update-function-code --function-name upload-image --zip-file fileb://lambda.zip | Out-Null
        awslocal lambda update-function-code --function-name list-images --zip-file fileb://lambda.zip | Out-Null
        awslocal lambda update-function-code --function-name get-image --zip-file fileb://lambda.zip | Out-Null
        awslocal lambda update-function-code --function-name delete-image --zip-file fileb://lambda.zip | Out-Null
    }
    else {

        Write-Host "Updating lambda: $function"

        awslocal lambda update-function-code `
        --function-name $function `
        --zip-file fileb://lambda.zip | Out-Null
    }

    Write-Host "Deployment complete."
}

$action = {
    $file = $Event.SourceEventArgs.FullPath
    Deploy-Lambda $file
}

Register-ObjectEvent $watcher Changed -Action $action

while ($true) { Start-Sleep 2 }
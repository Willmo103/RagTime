# Path: .\startup.ps1
# Description: This script is used to start the ollama container and pull the required models.

# Make sure that the docker command is available
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed. Please install Docker and try again."
}

# # use docker to start and run the ollama container in the background
# docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:latest

# # use the docker exec command to pull the required models: [mistral:latest]
# docker exec -it ollama ollama pull mistral:latest

# if theres not an existing .env file, create one, adding the following line:
if (-not (Test-Path .env)) {
    Write-Output "OLLAMA_API_URL=http://localhost:11434\n///data/db.sqlite3" > .env
}

# # wait 30 seconds for the container to start
# Start-Sleep -s 30

# make a http request to the base url and make sure the respoonse contains "ollama is running"
$response = Invoke-RestMethod -Uri "http://localhost:11434" -Method Get
if ($response -notlike "*ollama is running*") {
    throw "ollama is not running"
}
else {
    Write-Host "ollama is running"
    Write-Host "Startup complete!"
}

#end of startup.ps1

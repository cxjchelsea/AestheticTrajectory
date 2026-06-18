# Start Ollama with an ASCII-only model directory.
# Required when the Windows username contains non-ASCII characters.

$ModelsDir = "E:\projectIDEA\AestheticTrajectory\ollama-models"
$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

if (-not (Test-Path $OllamaExe)) {
    Write-Error "Ollama not found at $OllamaExe. Install it first: winget install Ollama.Ollama"
    exit 1
}

New-Item -ItemType Directory -Force -Path $ModelsDir | Out-Null
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ModelsDir, "User")
$env:OLLAMA_MODELS = $ModelsDir

Get-Process ollama* -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process $OllamaExe
Start-Sleep -Seconds 5

Write-Host "OLLAMA_MODELS=$ModelsDir"
& $OllamaExe list

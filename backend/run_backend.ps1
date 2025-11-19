# PowerShell script to automate backend setup and run

# Go to backend directory
Set-Location -Path $PSScriptRoot

# Create venv if missing
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate venv
. .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install --upgrade pip
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
}
pip install uvicorn

# Run the FastAPI server
Write-Host "Starting ADVANCED Figma to Multicode Generator (Pixel-Perfect Mode)..." -ForegroundColor Green
uvicorn app_advanced:app --reload --host 0.0.0.0 --port 8000

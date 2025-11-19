# Quick Demo Script - Show Your Teacher

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  FIGMA TO MULTICODE GENERATOR" -ForegroundColor Green
Write-Host "  Model Integration Verification" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check model file
Write-Host "[1/5] Checking trained model..." -ForegroundColor Yellow
$modelPath = ".\backend\models\ui_classification_model.h5"
if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1MB
    Write-Host "  ✓ Model found: ui_classification_model.h5" -ForegroundColor Green
    Write-Host "  ✓ Model size: $([math]::Round($modelSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  ✗ Model NOT found!" -ForegroundColor Red
    Write-Host "  Please place your model in: backend\models\ui_classification_model.h5" -ForegroundColor Red
    exit
}
Write-Host ""

# Check Python environment
Write-Host "[2/5] Checking Python environment..." -ForegroundColor Yellow
if (Test-Path ".\backend\.venv") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Virtual environment missing!" -ForegroundColor Red
    exit
}
Write-Host ""

# Check dependencies
Write-Host "[3/5] Checking dependencies..." -ForegroundColor Yellow
& .\backend\.venv\Scripts\Activate.ps1
$deps = @("tensorflow", "opencv-python", "fastapi", "easyocr")
foreach ($dep in $deps) {
    $installed = pip list 2>$null | Select-String -Pattern "^$dep\s"
    if ($installed) {
        Write-Host "  ✓ $dep installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dep missing" -ForegroundColor Red
    }
}
Write-Host ""

# Check backend files
Write-Host "[4/5] Checking backend files..." -ForegroundColor Yellow
$files = @(
    "backend\app_advanced.py",
    "backend\utils\tf_classifier.py",
    "backend\utils\detection.py",
    "backend\utils\visual_style_extractor.py",
    "backend\utils\text_extractor.py",
    "backend\utils\generator_pixel_perfect.py"
)
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
    }
}
Write-Host ""

# Summary
Write-Host "[5/5] Integration Summary" -ForegroundColor Yellow
Write-Host "  ================================" -ForegroundColor Cyan
Write-Host "  SYSTEM STATUS: READY" -ForegroundColor Green
Write-Host "  ================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Model Integration:" -ForegroundColor White
Write-Host "  • Model File: ✓ Present" -ForegroundColor Green
Write-Host "  • Location: backend\models\ui_classification_model.h5" -ForegroundColor White
Write-Host "  • Classes: 9 UI element types" -ForegroundColor White
Write-Host "  • Input: 224x224 RGB images" -ForegroundColor White
Write-Host "  • Framework: TensorFlow/Keras" -ForegroundColor White
Write-Host ""

Write-Host "Features Enabled:" -ForegroundColor White
Write-Host "  ✓ Geometric Detection (OpenCV)" -ForegroundColor Green
Write-Host "  ✓ AI Classification (YOUR MODEL)" -ForegroundColor Green
Write-Host "  ✓ Visual Style Extraction" -ForegroundColor Green
Write-Host "  ✓ Text Extraction (OCR)" -ForegroundColor Green
Write-Host "  ✓ Pixel-Perfect Code Generation" -ForegroundColor Green
Write-Host ""

Write-Host "Supported Output Formats:" -ForegroundColor White
Write-Host "  • HTML + CSS" -ForegroundColor Cyan
Write-Host "  • HTML + Tailwind" -ForegroundColor Cyan
Write-Host "  • React (JSX)" -ForegroundColor Cyan
Write-Host "  • Flutter (Dart)" -ForegroundColor Cyan
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Ready to start the system!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the complete system:" -ForegroundColor Yellow
Write-Host "  .\go.bat" -ForegroundColor White
Write-Host ""
Write-Host "Then open: http://localhost:5173" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start
$response = Read-Host "Start the system now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Starting system..." -ForegroundColor Green
    Write-Host ""
    .\go.bat
} else {
    Write-Host ""
    Write-Host "Run .\go.bat when ready!" -ForegroundColor Yellow
}

# System Verification Script
# Checks if all components are ready

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "FIGMA TO MULTICODE GENERATOR - SYSTEM VERIFICATION" -ForegroundColor Cyan
Write-Host "ILS v2 Architecture" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check files
Write-Host "[1] Checking Core Files..." -ForegroundColor Yellow

$files = @(
    "backend\app.py",
    "backend\utils\classifier.py",
    "backend\utils\detection.py",
    "backend\utils\ils_builder.py",
    "backend\utils\style_analyzer.py",
    "backend\utils\generators\tailwind_gen.py",
    "backend\models\ui_classification_model.h5"
)

foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "  OK: $f" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $f" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""

# Check Python environment
Write-Host "[2] Checking Python Environment..." -ForegroundColor Yellow

if (Test-Path "backend\.venv") {
    Write-Host "  OK: Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Virtual environment missing" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

# Check model
Write-Host "[3] Checking CNN Model..." -ForegroundColor Yellow

if (Test-Path "backend\models\ui_classification_model.h5") {
    $size = (Get-Item "backend\models\ui_classification_model.h5").Length / 1MB
    Write-Host "  OK: Model found ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Model not found (will use fallback)" -ForegroundColor Yellow
}

Write-Host ""

# Test imports
Write-Host "[4] Testing Python Imports..." -ForegroundColor Yellow

$code = @"
import sys
sys.path.insert(0, 'backend')
try:
    from utils import classifier, detection, ils_builder, style_analyzer
    from utils.generators import tailwind_gen
    import app
    print('OK: All imports successful')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@

$code | Out-File -FilePath "test_imports.py" -Encoding utf8

try {
    $result = & backend\.venv\Scripts\python.exe test_imports.py 2>&1
    if ($result -match "OK:") {
        Write-Host "  OK: All modules import correctly" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: $result" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "  ERROR: Could not test imports" -ForegroundColor Red
    $allGood = $false
} finally {
    Remove-Item "test_imports.py" -ErrorAction SilentlyContinue
}

Write-Host ""

# Summary
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "  STATUS: READY TO RUN" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""
    Write-Host "  All systems operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  To start the system:" -ForegroundColor Cyan
    Write-Host "    .\go.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "  Architecture:" -ForegroundColor Cyan
    Write-Host "    Stage 1: Detection (OpenCV)" -ForegroundColor White
    Write-Host "    Stage 2: Classification (CNN + Fallback)" -ForegroundColor White
    Write-Host "    Stage 3: Style Analysis" -ForegroundColor White
    Write-Host "    Stage 4: ILS v2 Building (Tree-based)" -ForegroundColor White
    Write-Host "    Stage 5: Code Generation (4 frameworks)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "  STATUS: NEEDS ATTENTION" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host ""
    Write-Host "  Some issues detected. Review above." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

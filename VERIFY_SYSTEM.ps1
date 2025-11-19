# ============================================================================
# FIGMA TO MULTICODE GENERATOR - SYSTEM VERIFICATION
# ILS v2 Architecture - Complete Validation Script
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   FIGMA TO MULTICODE GENERATOR - SYSTEM VERIFICATION      ║" -ForegroundColor Cyan
Write-Host "║   ILS v2 Architecture - Production Ready                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# ============================================================================
# 1. FILE STRUCTURE VERIFICATION
# ============================================================================

Write-Host "[1/8] Verifying File Structure..." -ForegroundColor Yellow
Write-Host ""

$requiredFiles = @(
    "backend\app.py",
    "backend\config.py",
    "backend\utils\classifier.py",
    "backend\utils\detection.py",
    "backend\utils\ils_builder.py",
    "backend\utils\style_analyzer.py",
    "backend\utils\generators\__init__.py",
    "backend\utils\generators\tailwind_gen.py",
    "backend\utils\generator_html_css_enhanced.py",
    "backend\utils\generator_react_enhanced.py",
    "backend\utils\generator_flutter_enhanced.py",
    "backend\models\ui_classification_model.h5",
    "DESIGN_NOTES.md",
    "go.bat"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING" -ForegroundColor Red
        $missingFiles += $file
        $allPassed = $false
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✓ All core files present" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# 2. VIRTUAL ENVIRONMENT CHECK
# ============================================================================

Write-Host "[2/8] Checking Virtual Environment..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "backend\.venv") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
    
    # Check if key packages are installed
    & backend\.venv\Scripts\Activate.ps1
    
    $packages = @("fastapi", "uvicorn", "opencv-python", "numpy", "pillow")
    $missingPackages = @()
    
    foreach ($pkg in $packages) {
        $installed = pip list 2>$null | Select-String -Pattern "^$pkg\s"
        if ($installed) {
            Write-Host "  ✓ $pkg installed" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $pkg NOT installed" -ForegroundColor Red
            $missingPackages += $pkg
            $allPassed = $false
        }
    }
    
    # Check optional packages
    Write-Host ""
    Write-Host "  Optional packages:" -ForegroundColor Cyan
    $optionalPackages = @("tensorflow", "easyocr")
    foreach ($pkg in $optionalPackages) {
        $installed = pip list 2>$null | Select-String -Pattern "^$pkg\s"
        if ($installed) {
            Write-Host "  ✓ $pkg installed" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $pkg not installed (fallback mode will be used)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ✗ Virtual environment NOT found" -ForegroundColor Red
    Write-Host "  Run: cd backend; python -m venv .venv" -ForegroundColor Yellow
    $allPassed = $false
}

Write-Host ""

# ============================================================================
# 3. PYTHON IMPORTS TEST
# ============================================================================

Write-Host "[3/8] Testing Python Imports..." -ForegroundColor Yellow
Write-Host ""

$testScript = @"
import sys
sys.path.insert(0, 'backend')

try:
    from utils import classifier
    print('✓ classifier module')
    
    from utils import detection
    print('✓ detection module')
    
    from utils import ils_builder
    print('✓ ils_builder module')
    
    from utils import style_analyzer
    print('✓ style_analyzer module')
    
    from utils.generators import tailwind_gen
    print('✓ tailwind_gen module')
    
    import app
    print('✓ app module')
    
    print('SUCCESS: All modules import correctly')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@

$testScript | Set-Content -Path "temp_import_test.py"

try {
    & backend\.venv\Scripts\python.exe temp_import_test.py 2>&1 | ForEach-Object {
        if ($_ -match "✓") {
            Write-Host "  $_" -ForegroundColor Green
        } elseif ($_ -match "ERROR") {
            Write-Host "  $_" -ForegroundColor Red
            $allPassed = $false
        } elseif ($_ -match "SUCCESS") {
            Write-Host "  $_" -ForegroundColor Green
        } else {
            Write-Host "  $_"
        }
    }
} catch {
    Write-Host "  ✗ Import test failed" -ForegroundColor Red
    $allPassed = $false
} finally {
    Remove-Item "temp_import_test.py" -ErrorAction SilentlyContinue
}

Write-Host ""

# ============================================================================
# 4. CNN MODEL CHECK
# ============================================================================

Write-Host "[4/8] Checking CNN Model..." -ForegroundColor Yellow
Write-Host ""

$modelPath = "backend\models\ui_classification_model.h5"
if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1MB
    Write-Host "  ✓ Model file found" -ForegroundColor Green
    Write-Host "  ✓ Model size: $([math]::Round($modelSize, 2)) MB" -ForegroundColor Green
    Write-Host "  ✓ Model location: $modelPath" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Model file NOT found at: $modelPath" -ForegroundColor Yellow
    Write-Host "  ℹ System will use geometric fallback classifier" -ForegroundColor Cyan
}

Write-Host ""

# ============================================================================
# 5. ILS V2 ARCHITECTURE CHECK
# ============================================================================

Write-Host "[5/8] Verifying ILS v2 Architecture..." -ForegroundColor Yellow
Write-Host ""

$ilsContent = Get-Content "backend\utils\ils_builder.py" -Raw

$ilsFeatures = @{
    "ILSNode dataclass" = "class ILSNode"
    "detect_navbar function" = "def detect_navbar"
    "detect_hero function" = "def detect_hero"
    "detect_form_sections function" = "def detect_form_sections"
    "detect_card_sections function" = "def detect_card_sections"
    "build_ils function" = "def build_ils"
}

foreach ($feature in $ilsFeatures.GetEnumerator()) {
    if ($ilsContent -match [regex]::Escape($feature.Value)) {
        Write-Host "  ✓ $($feature.Key)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($feature.Key) NOT found" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host ""

# ============================================================================
# 6. GENERATOR ARCHITECTURE CHECK
# ============================================================================

Write-Host "[6/8] Verifying Generator Architecture..." -ForegroundColor Yellow
Write-Host ""

$generatorChecks = @{
    "Tailwind generator" = "backend\utils\generators\tailwind_gen.py"
    "HTML+CSS generator" = "backend\utils\generator_html_css_enhanced.py"
    "React generator" = "backend\utils\generator_react_enhanced.py"
    "Flutter generator" = "backend\utils\generator_flutter_enhanced.py"
}

foreach ($gen in $generatorChecks.GetEnumerator()) {
    if (Test-Path $gen.Value) {
        Write-Host "  ✓ $($gen.Key)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($gen.Key) NOT found" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host ""

# ============================================================================
# 7. DOCUMENTATION CHECK
# ============================================================================

Write-Host "[7/8] Checking Documentation..." -ForegroundColor Yellow
Write-Host ""

$docs = @{
    "README.md" = "Project overview"
    "DESIGN_NOTES.md" = "ILS v2 architecture guide"
    "MODEL_INTEGRATION.md" = "CNN model integration"
    "PIXEL_PERFECT_GUIDE.md" = "Pixel-perfect features"
    "QUICKSTART.md" = "Quick start guide"
}

foreach ($doc in $docs.GetEnumerator()) {
    if (Test-Path $doc.Key) {
        Write-Host "  ✓ $($doc.Key) - $($doc.Value)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $($doc.Key) - $($doc.Value) (missing)" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================================================
# 8. FRONTEND CHECK
# ============================================================================

Write-Host "[8/8] Checking Frontend..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "frontend\package.json") {
    Write-Host "  ✓ Frontend package.json exists" -ForegroundColor Green
    
    if (Test-Path "frontend\node_modules") {
        Write-Host "  ✓ Node modules installed" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Node modules NOT installed" -ForegroundColor Yellow
        Write-Host "  Run: cd frontend; npm install" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Frontend not configured" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    VERIFICATION SUMMARY                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($allPassed) {
    Write-Host "  🎉 SYSTEM STATUS: FULLY OPERATIONAL" -ForegroundColor Green
    Write-Host ""
    Write-Host "  All critical components verified!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ✓ File structure complete" -ForegroundColor Green
    Write-Host "  ✓ Virtual environment ready" -ForegroundColor Green
    Write-Host "  ✓ All modules importable" -ForegroundColor Green
    Write-Host "  ✓ ILS v2 architecture in place" -ForegroundColor Green
    Write-Host "  ✓ All generators present" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Ready to start:" -ForegroundColor Cyan
    Write-Host "    .\go.bat" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "  ⚠ SYSTEM STATUS: ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Some components need attention." -ForegroundColor Yellow
    Write-Host "  Review the output above for details." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                   ARCHITECTURE SUMMARY                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ILS v2 Pipeline:" -ForegroundColor Cyan
Write-Host "    1. Detection       → OpenCV block detection" -ForegroundColor White
Write-Host "    2. Classification  → CNN (or geometric fallback)" -ForegroundColor White
Write-Host "    3. Style Analysis  → Colors, spacing, typography" -ForegroundColor White
Write-Host "    4. ILS Building    → Tree structure with sections" -ForegroundColor White
Write-Host "    5. Code Generation → Tailwind, HTML, React, Flutter" -ForegroundColor White
Write-Host ""
Write-Host "  Supported Sections:" -ForegroundColor Cyan
Write-Host "    • Navbar    • Hero      • Forms" -ForegroundColor White
Write-Host "    • Cards     • Sidebar   • Footer" -ForegroundColor White
Write-Host ""
Write-Host "  Layout Modes:" -ForegroundColor Cyan
Write-Host "    • Vertical  • Horizontal  • Grid  • Absolute" -ForegroundColor White
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Return exit code
if ($allPassed) {
    exit 0
} else {
    exit 1
}

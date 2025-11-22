# Test the PDF automation setup

Write-Host "Testing PDF to Quarto Automation Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check directory structure
Write-Host "`n1. Checking directory structure..." -ForegroundColor Yellow

$requiredDirs = @(
    "automation\scripts",
    "automation\config", 
    "automation\logs",
    "source_pdfs",
    "chapters\optimization",
    "chapters\statistics", 
    "chapters\machine_learning",
    "temp\processed_markdown"
)

$allDirsExist = $true
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "✓ $dir exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $dir missing" -ForegroundColor Red
        $allDirsExist = $false
    }
}

# Check script files
Write-Host "`n2. Checking script files..." -ForegroundColor Yellow

$requiredFiles = @(
    "automation\scripts\batch_convert.ps1",
    "automation\scripts\pdf_to_quarto.py",
    "automation\scripts\validate_output.py",
    "automation\config\conversion_config.json",
    "automation\README.md"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# Check Python availability
Write-Host "`n3. Checking Python availability..." -ForegroundColor Yellow

try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python available: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python not found in PATH" -ForegroundColor Red
        Write-Host "  Install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "✗ Python not installed" -ForegroundColor Red
    Write-Host "  Install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
}

# Check Quarto config
Write-Host "`n4. Checking Quarto configuration..." -ForegroundColor Yellow

if (Test-Path "_quarto.yml") {
    $quartoContent = Get-Content "_quarto.yml" -Raw
    if ($quartoContent -match "chapters/optimization") {
        Write-Host "✓ _quarto.yml updated for multi-book structure" -ForegroundColor Green
    } else {
        Write-Host "✗ _quarto.yml needs updating" -ForegroundColor Red
    }
} else {
    Write-Host "✗ _quarto.yml not found" -ForegroundColor Red
}

# Summary
Write-Host "`n5. Setup Summary" -ForegroundColor Yellow
Write-Host "================" -ForegroundColor Yellow

if ($allDirsExist -and $allFilesExist) {
    Write-Host "✓ Setup completed successfully!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Install Python if not already installed"
    Write-Host "2. Add PDF files to the 'source_pdfs' directory"  
    Write-Host "3. Run: .\automation\scripts\batch_convert.ps1"
    Write-Host "4. Validate with: python .\automation\scripts\validate_output.py"
    Write-Host "5. Build book with: quarto render"
    Write-Host "`nSee automation\README.md for detailed instructions."
} else {
    Write-Host "✗ Setup incomplete. Please check the errors above." -ForegroundColor Red
}

Write-Host "`nSetup test completed!" -ForegroundColor Green
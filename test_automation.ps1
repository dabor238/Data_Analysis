Write-Host "PDF to Quarto Automation - Setup Test" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check directories
Write-Host ""
Write-Host "Checking directories:" -ForegroundColor Yellow
$dirs = @("automation\scripts", "source_pdfs", "chapters\optimization")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "✗ $dir" -ForegroundColor Red
    }
}

# Check key files
Write-Host ""
Write-Host "Checking key files:" -ForegroundColor Yellow
$files = @("automation\scripts\batch_convert.ps1", "automation\config\conversion_config.json", "_quarto.yml")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file" -ForegroundColor Red
    }
}

# Check Python
Write-Host ""
Write-Host "Checking Python:" -ForegroundColor Yellow
try {
    $result = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python is available" -ForegroundColor Green
    } else {
        Write-Host "✗ Python not found" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Python not installed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup test completed!" -ForegroundColor Green
Write-Host "Read automation\README.md for usage instructions." -ForegroundColor Cyan
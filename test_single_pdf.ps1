# Simple PDF Converter Test
# Let's convert your first PDF manually

Write-Host "PDF to Quarto Conversion Test" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

# Check if PDF exists
$pdfFile = "source_pdfs\01_intro.pdf"
if (Test-Path $pdfFile) {
    Write-Host "✓ Found: $pdfFile" -ForegroundColor Green
    $pdfInfo = Get-Item $pdfFile
    Write-Host "  Size: $([math]::Round($pdfInfo.Length / 1KB, 1)) KB" -ForegroundColor Cyan
} else {
    Write-Host "✗ PDF file not found: $pdfFile" -ForegroundColor Red
    exit 1
}

# Try to find Python
Write-Host "`nLooking for Python..." -ForegroundColor Yellow

# Try different Python commands
$pythonCommands = @("python", "python3", "py")
$pythonFound = $false
$pythonCmd = ""

foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Found Python: $cmd ($version)" -ForegroundColor Green
            $pythonCmd = $cmd
            $pythonFound = $true
            break
        }
    } catch {
        # Continue trying
    }
}

if (-not $pythonFound) {
    Write-Host "✗ Python not found. Please install Python first." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  After installation, restart PowerShell and try again." -ForegroundColor Yellow
    exit 1
}

# Install required packages
Write-Host "`nInstalling required packages..." -ForegroundColor Yellow
try {
    & $pythonCmd -m pip install --quiet marker-pdf pymupdf pandas pyyaml
    Write-Host "✓ Packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Package installation may have issues, continuing..." -ForegroundColor Yellow
}

# Try to convert the PDF
Write-Host "`nConverting PDF..." -ForegroundColor Yellow
try {
    & $pythonCmd "automation\scripts\pdf_to_quarto.py" $pdfFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Conversion completed!" -ForegroundColor Green
        
        # Check output
        Write-Host "`nChecking output files..." -ForegroundColor Yellow
        Get-ChildItem "chapters" -Recurse -Name "*.qmd" | ForEach-Object {
            Write-Host "✓ Created: chapters\$_" -ForegroundColor Green
        }
    } else {
        Write-Host "✗ Conversion failed" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Error running conversion: $_" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Cyan
#!/usr/bin/env powershell
# PowerShell script to set up and run Nougat conversion

param(
    [Parameter(Mandatory=$true)]
    [string]$PdfPath,
    
    [string]$OutputPath = "",
    [string]$Title = "",
    [string]$TempDir = "temp/nougat_output"
)

Write-Host "🚀 Starting Nougat PDF Conversion Process" -ForegroundColor Green

# Activate virtual environment
Write-Host "📦 Activating Python environment..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Install Nougat if needed
Write-Host "🔍 Checking Nougat installation..." -ForegroundColor Blue
python -c "import nougat" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📥 Installing Nougat OCR..." -ForegroundColor Yellow
    pip install nougat-ocr
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Nougat" -ForegroundColor Red
        exit 1
    }
}

# Set default output path if not provided
if ([string]::IsNullOrEmpty($OutputPath)) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($PdfPath)
    $OutputPath = "chapters\optimization\${baseName}_nougat.qmd"
}

# Set default title if not provided
if ([string]::IsNullOrEmpty($Title)) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($PdfPath)
    $Title = "Chapter: $($baseName.Replace('_', ' '))"
}

Write-Host "🔄 Converting PDF with Nougat..." -ForegroundColor Blue
Write-Host "   📄 Input: $PdfPath" -ForegroundColor Gray
Write-Host "   📝 Output: $OutputPath" -ForegroundColor Gray
Write-Host "   📁 Temp: $TempDir" -ForegroundColor Gray

# Run the Python converter
python "automation\scripts\nougat_pdf_converter.py" $PdfPath -o $OutputPath -t $Title --temp-dir $TempDir

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Conversion completed successfully!" -ForegroundColor Green
    Write-Host "🔧 Testing Quarto compilation..." -ForegroundColor Blue
    
    # Test compile the new file
    quarto render $OutputPath --to html
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🎉 Quarto compilation successful!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Conversion complete but Quarto compilation had issues" -ForegroundColor Yellow
        Write-Host "   Manual review may be needed" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Conversion failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   ✅ Nougat conversion: Complete" -ForegroundColor Green
Write-Host "   📝 Generated file: $OutputPath" -ForegroundColor White
Write-Host "   🔍 Next: Review mathematical expressions for accuracy" -ForegroundColor Blue
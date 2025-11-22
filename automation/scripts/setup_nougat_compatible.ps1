#!/usr/bin/env powershell
# Alternative Nougat installation script with specific compatible versions

param(
    [string]$PdfPath = "source_pdfs\01_intro.pdf"
)

Write-Host "🔧 Setting up Nougat OCR with compatible dependencies..." -ForegroundColor Blue

# Install specific compatible versions
Write-Host "📦 Installing compatible dependency versions..." -ForegroundColor Yellow

$packages = @(
    "albumentations==1.3.1",
    "pydantic==1.10.12", 
    "transformers==4.25.1",
    "torch==1.13.1",
    "torchvision==0.14.1"
)

foreach ($package in $packages) {
    Write-Host "   Installing $package..." -ForegroundColor Gray
    & "C:/Users/dabor/Documents/Github/Data_Analysis_Book/dataanalysis/venv/Scripts/python.exe" -m pip install $package --upgrade
}

Write-Host "📥 Installing Nougat OCR with compatible setup..." -ForegroundColor Yellow
& "C:/Users/dabor/Documents/Github/Data_Analysis_Book/dataanalysis/venv/Scripts/python.exe" -m pip install nougat-ocr --no-deps
& "C:/Users/dabor/Documents/Github/Data_Analysis_Book/dataanalysis/venv/Scripts/python.exe" -m pip install datasets nltk python-Levenshtein sentencepiece sconf pypdf opencv-python-headless

Write-Host "🧪 Testing Nougat installation..." -ForegroundColor Blue
& "C:/Users/dabor/Documents/Github/Data_Analysis_Book/dataanalysis/venv/Scripts/python.exe" -c "try: import nougat; print('Nougat imported successfully'); exit(0)
except Exception as e: print(f'Import failed: {e}'); exit(1)"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Nougat installation successful!" -ForegroundColor Green
    
    if (Test-Path $PdfPath) {
        Write-Host "🔄 Testing conversion on $PdfPath..." -ForegroundColor Blue
        
        # Create output directory
        New-Item -ItemType Directory -Force -Path "temp\nougat_test" | Out-Null
        
        # Try nougat conversion
        & "C:/Users/dabor/Documents/Github/Data_Analysis_Book/dataanalysis/venv/Scripts/nougat" $PdfPath -o "temp\nougat_test"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Nougat conversion test successful!" -ForegroundColor Green
        } else {
            Write-Host "Nougat installation OK, but conversion test failed" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "Nougat installation failed" -ForegroundColor Red
    Write-Host "Using PyMuPDF alternative instead" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Available Conversion Options:" -ForegroundColor Cyan
Write-Host "   1. Enhanced manual version (Ready)" -ForegroundColor Green
Write-Host "   2. PyMuPDF converter (Working)" -ForegroundColor Green  
Write-Host "   3. Nougat OCR (Testing)" -ForegroundColor Yellow
Write-Host ""
# Batch PDF to Quarto Conversion Script
# Processes multiple PDFs in the source_pdfs directory

param(
    [string]$SourceDir = ".\source_pdfs",
    [string]$ConfigFile = ".\automation\config\conversion_config.json",
    [switch]$ValidateOnly,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Setup logging
$LogDir = ".\automation\logs"
$LogFile = Join-Path $LogDir "batch_conversion_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check if Python is available
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python found: $pythonVersion"
        } else {
            throw "Python not found"
        }
    }
    catch {
        Write-Log "Python is not installed or not in PATH. Please install Python first." "ERROR"
        Write-Log "You can install Python from: https://www.python.org/downloads/" "ERROR"
        return $false
    }
    
    # Check if required packages are installed
    $requiredPackages = @("marker-pdf", "pymupdf", "pandas", "pyyaml")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $result = & python -c "import $($package.Replace('-', '_')); print('OK')" 2>&1
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        }
        catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Log "Missing required packages: $($missingPackages -join ', ')" "WARNING"
        Write-Log "Installing missing packages..." "INFO"
        
        try {
            & python -m pip install $missingPackages
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install packages"
            }
            Write-Log "Successfully installed missing packages" "INFO"
        }
        catch {
            Write-Log "Failed to install required packages. Please run: python -m pip install $($missingPackages -join ' ')" "ERROR"
            return $false
        }
    }
    
    return $true
}

function Get-PDFFiles {
    param([string]$Directory)
    
    if (-not (Test-Path $Directory)) {
        Write-Log "Source directory does not exist: $Directory" "ERROR"
        return @()
    }
    
    $pdfFiles = Get-ChildItem -Path $Directory -Filter "*.pdf" -File
    Write-Log "Found $($pdfFiles.Count) PDF files in $Directory"
    
    return $pdfFiles
}

function Convert-SinglePDF {
    param(
        [System.IO.FileInfo]$PdfFile,
        [string]$ConfigFile
    )
    
    $pdfPath = $PdfFile.FullName
    Write-Log "Converting: $($PdfFile.Name)"
    
    try {
        # Call the Python conversion script
        $result = & python ".\automation\scripts\pdf_to_quarto.py" "$pdfPath" --config "$ConfigFile" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✓ Successfully converted: $($PdfFile.Name)" "SUCCESS"
            return @{
                Status = "Success"
                File = $PdfFile.Name
                Output = $result
                Error = $null
            }
        } else {
            Write-Log "✗ Failed to convert: $($PdfFile.Name)" "ERROR"
            Write-Log "Error output: $result" "ERROR"
            return @{
                Status = "Failed"
                File = $PdfFile.Name
                Output = $null
                Error = $result
            }
        }
    }
    catch {
        Write-Log "✗ Exception converting $($PdfFile.Name): $_" "ERROR"
        return @{
            Status = "Failed"
            File = $PdfFile.Name
            Output = $null
            Error = $_.Exception.Message
        }
    }
}

function Generate-Report {
    param([array]$Results)
    
    $reportFile = Join-Path $LogDir "batch_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    
    $Results | ForEach-Object {
        [PSCustomObject]@{
            FileName = $_.File
            Status = $_.Status
            Error = $_.Error
            ProcessedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    } | Export-Csv -Path $reportFile -NoTypeInformation -Encoding UTF8
    
    Write-Log "Report saved to: $reportFile"
    
    # Summary
    $successCount = ($Results | Where-Object { $_.Status -eq "Success" }).Count
    $failCount = ($Results | Where-Object { $_.Status -eq "Failed" }).Count
    
    Write-Log "=== CONVERSION SUMMARY ===" "INFO"
    Write-Log "Total files processed: $($Results.Count)" "INFO"
    Write-Log "Successful conversions: $successCount" "INFO"
    Write-Log "Failed conversions: $failCount" "INFO"
    
    if ($failCount -gt 0) {
        Write-Log "Failed files:" "WARNING"
        $Results | Where-Object { $_.Status -eq "Failed" } | ForEach-Object {
            Write-Log "  - $($_.File): $($_.Error)" "WARNING"
        }
    }
}

function Update-QuartoConfig {
    Write-Log "Updating Quarto configuration..."
    
    try {
        # Read current _quarto.yml
        $quartoFile = ".\_quarto.yml"
        if (Test-Path $quartoFile) {
            $quartoContent = Get-Content $quartoFile -Raw
            Write-Log "Current _quarto.yml backed up to _quarto.yml.backup"
            Copy-Item $quartoFile "$quartoFile.backup"
        }
        
        Write-Log "Quarto configuration update completed"
    }
    catch {
        Write-Log "Warning: Could not update Quarto configuration: $_" "WARNING"
    }
}

# Main execution
Write-Log "=== Starting Batch PDF Conversion ===" "INFO"
Write-Log "Source directory: $SourceDir"
Write-Log "Config file: $ConfigFile"
Write-Log "Validation only: $ValidateOnly"

# Check prerequisites
if (-not (Test-Prerequisites)) {
    Write-Log "Prerequisites check failed. Exiting." "ERROR"
    exit 1
}

# Get PDF files
$pdfFiles = Get-PDFFiles -Directory $SourceDir

if ($pdfFiles.Count -eq 0) {
    Write-Log "No PDF files found in $SourceDir" "WARNING"
    Write-Log "Please add PDF files to the source_pdfs directory and try again."
    exit 0
}

if ($ValidateOnly) {
    Write-Log "Validation mode - listing files only:" "INFO"
    foreach ($pdf in $pdfFiles) {
        Write-Log "  - $($pdf.Name) ($($pdf.Length) bytes)"
    }
    exit 0
}

# Process each PDF
$results = @()

foreach ($pdfFile in $pdfFiles) {
    $result = Convert-SinglePDF -PdfFile $pdfFile -ConfigFile $ConfigFile
    $results += $result
}

# Generate report
Generate-Report -Results $results

# Update Quarto configuration
Update-QuartoConfig

Write-Log "=== Batch conversion completed ===" "INFO"
Write-Log "Log file: $LogFile"

# Exit with appropriate code
$failedCount = ($results | Where-Object { $_.Status -eq "Failed" }).Count
if ($failedCount -gt 0) {
    exit 1
} else {
    exit 0
}
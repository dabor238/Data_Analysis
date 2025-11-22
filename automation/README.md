# Quick Start Guide for PDF to Quarto Automation

This guide helps you convert PDF books to Quarto format within your existing project.

## Prerequisites

1. **Python Installation**: 
   - Download from https://www.python.org/downloads/
   - Make sure Python is added to your PATH during installation

2. **Required Python Packages** (will be auto-installed):
   - marker-pdf (primary conversion tool)
   - pymupdf (fallback conversion)
   - pandas (data processing)
   - pyyaml (configuration)

## Quick Setup

1. **Add your PDF files** to the `source_pdfs/` directory
2. **Run the batch converter**:
   ```powershell
   .\automation\scripts\batch_convert.ps1
   ```

## Directory Structure

```
dataanalysis/                    # Your Quarto project root
├── source_pdfs/                 # PUT YOUR PDF FILES HERE
│   ├── optimization_book.pdf
│   └── statistics_book.pdf
├── chapters/                    # Generated Quarto files
│   ├── optimization/
│   ├── statistics/
│   └── machine_learning/
├── automation/
│   ├── scripts/
│   │   ├── batch_convert.ps1    # Main batch processor
│   │   ├── pdf_to_quarto.py     # Core conversion logic
│   │   └── validate_output.py   # Quality checker
│   ├── config/
│   │   └── conversion_config.json # Settings
│   └── logs/                    # Conversion logs
└── temp/                        # Temporary processing files
```

## Usage Examples

### Convert All PDFs
```powershell
# Process all PDFs in source_pdfs directory
.\automation\scripts\batch_convert.ps1
```

### Convert Single PDF
```powershell
# Convert one specific file
python .\automation\scripts\pdf_to_quarto.py "source_pdfs\my_book.pdf"
```

### Validate Output
```powershell
# Check quality of converted files
python .\automation\scripts\validate_output.py
```

### Preview Before Converting
```powershell
# See what files would be processed
.\automation\scripts\batch_convert.ps1 -ValidateOnly
```

## Configuration

Edit `automation/config/conversion_config.json` to customize:
- Conversion tool preferences (marker vs nougat)
- Equation processing options
- Chapter detection patterns
- Book categorization keywords

## Workflow

1. **Add PDFs**: Place PDF files in `source_pdfs/`
2. **Convert**: Run `.\automation\scripts\batch_convert.ps1`
3. **Validate**: Run `python .\automation\scripts\validate_output.py`
4. **Build Book**: Run `quarto render` to generate your book
5. **Review**: Check the generated HTML/PDF output

## Troubleshooting

### Python Not Found
- Install Python from https://www.python.org/downloads/
- Ensure "Add Python to PATH" is checked during installation
- Restart PowerShell after installation

### Missing Packages
The batch script will automatically install required packages, but if needed:
```powershell
python -m pip install marker-pdf pymupdf pandas pyyaml
```

### PDF Conversion Fails
- Check the log files in `automation/logs/`
- Try converting a single PDF first to test
- Some PDFs may require manual cleanup after conversion

### Poor Equation Recognition
- Edit `automation/config/conversion_config.json`
- Set `"tool": "nougat"` for better math recognition (slower)
- Manually review and fix complex equations in the generated .qmd files

## Output Files

After conversion, you'll have:
- **Chapters**: `.qmd` files organized by topic in `chapters/`
- **Logs**: Conversion reports in `automation/logs/`
- **Reports**: Quality validation results
- **Updated Book**: Your `_quarto.yml` supports the new structure

## Next Steps

1. Review converted chapters for accuracy
2. Adjust chapter ordering in `_quarto.yml`
3. Add cross-references between chapters
4. Customize the book's appearance and metadata
5. Render the final book: `quarto render`

## Support

- Check log files for detailed error messages
- Validation reports identify quality issues
- Configuration file controls conversion behavior
- Each tool has specific strengths for different content types
# Sample PDF file - place your real PDFs here

This directory should contain the PDF books you want to convert to Quarto format.

## Supported File Types
- PDF files (.pdf)

## Naming Conventions
For best results, use descriptive filenames:
- `optimization_methods.pdf`
- `statistical_analysis.pdf` 
- `machine_learning_basics.pdf`

## Organization
The automation system will automatically categorize books based on:
- Filename keywords
- Content analysis
- Detected topic patterns

Categories:
- `optimization/` - optimization, linear programming, convex, objective function
- `statistics/` - statistics, probability, distribution, hypothesis
- `machine_learning/` - machine learning, neural, classification, regression

## Usage
1. Copy your PDF files to this directory
2. Run: `.\automation\scripts\batch_convert.ps1`
3. Converted files appear in the `chapters/` directory

## File Size Limits
- No specific limits, but larger files take longer to process
- Files with many images may require additional processing time
- Complex mathematical content is handled best by the specialized tools
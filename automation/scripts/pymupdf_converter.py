#!/usr/bin/env python3
"""
Simple PDF to Markdown converter using PyMuPDF as alternative to Nougat
This provides a fallback solution while Nougat compatibility issues are resolved.
"""

import argparse
import fitz  # PyMuPDF
import re
import os
from pathlib import Path

def simple_pdf_to_markdown(pdf_path, output_path=None, title=None):
    """
    Convert PDF to Markdown using PyMuPDF with enhanced text processing
    """
    if not output_path:
        output_path = pdf_path.replace('.pdf', '_pymupdf.qmd')
    
    if not title:
        title = Path(pdf_path).stem.replace('_', ' ').title()
    
    print(f"🔄 Converting {pdf_path} with PyMuPDF...")
    
    # Open PDF
    doc = fitz.open(pdf_path)
    
    # Extract text from all pages
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        full_text += text + "\n"
    
    doc.close()
    
    # Clean and structure the text
    cleaned_text = clean_extracted_text(full_text)
    
    # Create Quarto header
    quarto_content = create_quarto_header(title, "PyMuPDF Enhanced Conversion")
    quarto_content += "\n\n" + cleaned_text
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(quarto_content)
    
    print(f"✅ Conversion completed: {output_path}")
    return output_path

def clean_extracted_text(text):
    """
    Clean and enhance extracted text with basic mathematical formatting
    """
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # Try to identify and format equations
    # Look for patterns like "min x" or "max x"  
    text = re.sub(r'\bmin\s+([x-z])\b', r'$$\\min_{\\1}$$', text)
    text = re.sub(r'\bmax\s+([x-z])\b', r'$$\\max_{\\1}$$', text)
    
    # Format common mathematical expressions
    text = re.sub(r'\|\|([^|]+)\|\|', r'$\\|\\1\\|$', text)  # Norms
    text = re.sub(r'∑', r'$\\sum$', text)  # Sum symbols
    text = re.sub(r'∈', r'$\\in$', text)  # Set membership
    text = re.sub(r'⟨([^⟩]+)⟩', r'$\\langle \\1 \\rangle$', text)  # Angle brackets
    
    # Identify section headers (lines with few words, title case)
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
            
        # Potential section header detection
        words = line.split()
        if (2 <= len(words) <= 8 and 
            line[0].isupper() and 
            not line.endswith('.') and
            not re.search(r'\d', line)):
            processed_lines.append(f"\n## {line} {{#sec-{line.lower().replace(' ', '-')}}}\n")
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def create_quarto_header(title, subtitle):
    """Create Quarto YAML header"""
    header = f"""---
title: "{title}"
subtitle: "{subtitle}"
author: "PDF Conversion Tool"
date: "{Path(__file__).stat().st_mtime}"
category: "converted"
format:
  html:
    toc: true
    toc-depth: 3
    number-sections: true
    theme: cosmo
  pdf:
    toc: true
    number-sections: true
    engine: lualatex
bibliography: references.bib
---

::: {{.callout-note}}
## **Conversion Information**

This document was converted from PDF using **PyMuPDF** as an alternative to Nougat OCR.

**Processing Notes:**
- Basic mathematical expression detection applied
- Section headers automatically identified  
- Manual review recommended for complex equations
- Enhanced formatting may be needed for optimal results
:::
"""
    return header

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to Quarto Markdown using PyMuPDF')
    parser.add_argument('pdf_path', help='Path to input PDF file')
    parser.add_argument('-o', '--output', help='Output path for Quarto file')
    parser.add_argument('-t', '--title', help='Document title')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        return 1
    
    try:
        output_file = simple_pdf_to_markdown(args.pdf_path, args.output, args.title)
        print(f"🎉 Success! Enhanced PDF conversion completed.")
        print(f"📄 Output file: {output_file}")
        print(f"💡 Tip: Review mathematical expressions for accuracy")
        return 0
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
Nougat-based PDF to Quarto converter for academic documents
Provides better mathematical expression handling than traditional OCR
"""

import os
import sys
from pathlib import Path
import argparse
import subprocess
import yaml
import re
from datetime import datetime

def install_nougat():
    """Install Nougat if not already installed"""
    try:
        import nougat
        print("✅ Nougat already installed")
        return True
    except ImportError:
        print("📦 Installing Nougat...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "nougat-ocr"], check=True)
            print("✅ Nougat installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Nougat")
            return False

def convert_pdf_with_nougat(pdf_path, output_dir):
    """Convert PDF to Markdown using Nougat"""
    print(f"🔄 Converting {pdf_path} with Nougat...")
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run Nougat conversion
        cmd = [
            "nougat", 
            str(pdf_path), 
            "-o", str(output_dir),
            "--no-skipping"  # Process all pages
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Nougat conversion completed")
        
        # Find the generated markdown file
        pdf_name = Path(pdf_path).stem
        md_file = output_dir / f"{pdf_name}.mmd"
        
        if md_file.exists():
            return md_file
        else:
            # Look for any .mmd file in output directory
            md_files = list(output_dir.glob("*.mmd"))
            if md_files:
                return md_files[0]
            else:
                raise FileNotFoundError("No markdown file generated")
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Nougat conversion failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def clean_nougat_output(md_content):
    """Clean and enhance Nougat-generated markdown for Quarto"""
    
    # Clean up common Nougat artifacts
    cleaned = md_content
    
    # Fix heading formatting
    cleaned = re.sub(r'^#\s*(\d+\.?\d*)\s+(.+)$', r'## \2 {#sec-\1}', cleaned, flags=re.MULTILINE)
    
    # Ensure proper equation formatting
    cleaned = re.sub(r'\\begin{equation}(.*?)\\end{equation}', r'$$\1$$ {#eq-auto}', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'\\begin{align}(.*?)\\end{align}', r'$$\\begin{aligned}\1\\end{aligned}$$ {#eq-auto}', cleaned, flags=re.DOTALL)
    
    # Fix inline math
    cleaned = re.sub(r'\\[(.*?)\\]', r'$\1$', cleaned)
    
    # Clean up excessive whitespace
    cleaned = re.sub(r'\n{3,}', r'\n\n', cleaned)
    
    # Add callouts for important sections
    cleaned = add_callouts(cleaned)
    
    return cleaned

def add_callouts(content):
    """Add Quarto callouts for better presentation"""
    
    # Add callout for definitions
    content = re.sub(
        r'(Definition \d+\.?\d*:?\s*)(.*?)(\n\n)', 
        r'::: {.callout-note icon=false}\n## **Definition**\n\n\2\n:::\n\n',
        content, flags=re.DOTALL
    )
    
    # Add callout for theorems
    content = re.sub(
        r'(Theorem \d+\.?\d*:?\s*)(.*?)(\n\n)', 
        r'::: {.callout-important icon=false}\n## **Theorem**\n\n\2\n:::\n\n',
        content, flags=re.DOTALL
    )
    
    return content

def create_quarto_header(title, author="Optimization Methods", category="optimization"):
    """Create Quarto YAML header"""
    header = f"""---
title: "{title}"
subtitle: "Fundamentals of Continuous Optimization"
author: "{author}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
category: "{category}"
format:
  html:
    toc: true
    toc-depth: 3
    code-fold: true
    number-sections: true
    theme: cosmo
    css: |
      .callout {{
        border-left: 4px solid #007acc;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
      }}
  pdf:
    toc: true
    number-sections: true
bibliography: references.bib
---

"""
    return header

def convert_to_quarto(nougat_md_path, output_path, title):
    """Convert Nougat markdown to Quarto format"""
    
    with open(nougat_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean the content
    cleaned_content = clean_nougat_output(content)
    
    # Create Quarto document
    header = create_quarto_header(title)
    quarto_content = header + cleaned_content
    
    # Save to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(quarto_content)
    
    print(f"✅ Quarto document saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Quarto using Nougat")
    parser.add_argument("pdf_path", help="Path to input PDF file")
    parser.add_argument("-o", "--output", help="Output Quarto file path")
    parser.add_argument("-t", "--title", help="Document title")
    parser.add_argument("--temp-dir", default="temp/nougat_output", help="Temporary directory for Nougat output")
    
    args = parser.parse_args()
    
    # Install Nougat if needed
    if not install_nougat():
        sys.exit(1)
    
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Set up paths
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"chapters/optimization/{pdf_path.stem}_nougat.qmd")
    
    title = args.title or f"Chapter: {pdf_path.stem.replace('_', ' ').title()}"
    temp_dir = Path(args.temp_dir)
    
    try:
        # Convert with Nougat
        nougat_md = convert_pdf_with_nougat(pdf_path, temp_dir)
        if not nougat_md:
            sys.exit(1)
        
        # Convert to Quarto format
        convert_to_quarto(nougat_md, output_path, title)
        
        print(f"""
🎉 Conversion completed successfully!

📁 Original PDF: {pdf_path}
📝 Quarto file: {output_path}
🔬 Nougat output: {nougat_md}

Next steps:
1. Review the generated Quarto file
2. Run: quarto render --to html
3. Compare with original PDF for accuracy
        """)
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
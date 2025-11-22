#!/usr/bin/env python3
"""
PDF to Quarto Converter
Converts PDF files to Quarto-compatible markdown with proper front matter and equation handling.
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

class PDFToQuartoConverter:
    def __init__(self, config_path="./automation/config/conversion_config.json"):
        """Initialize converter with configuration"""
        self.config = self.load_config(config_path)
        self.setup_directories()
        
    def load_config(self, config_path):
        """Load conversion configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Default configuration if file is missing"""
        return {
            "conversion": {"tool": "marker"},
            "processing": {
                "equation_cleanup": True,
                "figure_processing": True,
                "table_processing": True,
                "chapter_detection": True
            },
            "output": {
                "chapters_dir": "./chapters",
                "temp_dir": "./temp/processed_markdown",
                "add_frontmatter": True
            }
        }
    
    def setup_directories(self):
        """Ensure required directories exist"""
        dirs = [
            self.config["output"]["chapters_dir"],
            self.config["output"]["temp_dir"],
            "./automation/logs"
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def convert_pdf_with_marker(self, pdf_path):
        """Convert PDF using Marker library"""
        try:
            from marker.convert import convert_single_pdf
            print(f"Converting {pdf_path} with Marker...")
            markdown_content = convert_single_pdf(pdf_path)
            return markdown_content
        except ImportError:
            print("Marker library not installed. Install with: pip install marker-pdf")
            return None
        except Exception as e:
            print(f"Error converting with Marker: {e}")
            return None
    
    def convert_pdf_with_pymupdf(self, pdf_path):
        """Fallback conversion using PyMuPDF"""
        try:
            import fitz
            print(f"Converting {pdf_path} with PyMuPDF (fallback)...")
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            print("PyMuPDF library not installed. Install with: pip install pymupdf")
            return None
        except Exception as e:
            print(f"Error converting with PyMuPDF: {e}")
            return None
    
    def convert_pdf(self, pdf_path):
        """Convert PDF using available tools"""
        # Try primary tool first
        if self.config["conversion"]["tool"] == "marker":
            content = self.convert_pdf_with_marker(pdf_path)
            if content:
                return content
        
        # Fallback to PyMuPDF
        print("Falling back to PyMuPDF...")
        return self.convert_pdf_with_pymupdf(pdf_path)
    
    def clean_equations(self, content):
        """Clean and standardize LaTeX equations"""
        if not self.config["processing"]["equation_cleanup"]:
            return content
        
        # Fix common equation formatting issues
        content = re.sub(r'\$\$\n\s*\n', '$$\n', content)  # Remove empty lines in equations
        content = re.sub(r'\n\s*\n\$\$', '\n$$', content)
        content = re.sub(r'\\\[', '$$', content)  # Convert LaTeX display math
        content = re.sub(r'\\\]', '$$', content)
        
        # Fix inline math
        content = re.sub(r'\\\(', '$', content)
        content = re.sub(r'\\\)', '$', content)
        
        return content
    
    def detect_book_category(self, content, pdf_name):
        """Detect which category this book belongs to"""
        content_lower = content.lower()
        pdf_name_lower = pdf_name.lower()
        
        category_scores = {}
        for category, keywords in self.config["book_categories"].items():
            score = 0
            for keyword in keywords:
                score += content_lower.count(keyword.lower())
                score += pdf_name_lower.count(keyword.lower()) * 2  # Weight filename higher
            category_scores[category] = score
        
        # Return category with highest score, default to 'optimization'
        if not category_scores or max(category_scores.values()) == 0:
            return "optimization"
        
        return max(category_scores, key=category_scores.get)
    
    def format_chapters(self, content):
        """Standardize chapter headings"""
        if not self.config["processing"]["chapter_detection"]:
            return content
        
        for pattern in self.config.get("chapter_patterns", []):
            content = re.sub(
                pattern, 
                lambda m: f"# {m.group().split()[-1]}", 
                content, 
                flags=re.MULTILINE
            )
        
        return content
    
    def process_figures(self, content):
        """Process figure references for Quarto"""
        if not self.config["processing"]["figure_processing"]:
            return content
        
        # Convert figure references to Quarto format
        content = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            r'![\1](\2){#fig-\1}',
            content
        )
        
        return content
    
    def generate_front_matter(self, pdf_name, category):
        """Generate YAML front matter for Quarto"""
        if not self.config["output"]["add_frontmatter"]:
            return ""
        
        clean_title = pdf_name.replace('_', ' ').replace('-', ' ').title()
        
        front_matter = f"""---
title: "{clean_title}"
author: "Extracted from PDF"
date: "{datetime.now().strftime('%Y-%m-%d')}"
category: "{category}"
format:
  html:
    toc: true
    toc-depth: 3
    code-fold: true
  pdf:
    toc: true
bibliography: references.bib
---

"""
        return front_matter
    
    def process_content(self, content, pdf_name):
        """Process markdown content for Quarto compatibility"""
        # Clean equations
        content = self.clean_equations(content)
        
        # Format chapters
        content = self.format_chapters(content)
        
        # Process figures
        content = self.process_figures(content)
        
        # Detect category
        category = self.detect_book_category(content, pdf_name)
        
        # Add front matter
        front_matter = self.generate_front_matter(pdf_name, category)
        
        return front_matter + content, category
    
    def save_processed_file(self, content, pdf_name, category):
        """Save processed content to appropriate location"""
        # Create category-specific filename
        clean_name = re.sub(r'[^\w\s-]', '', pdf_name).strip()
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        
        # Ensure filename is not empty
        if not clean_name:
            clean_name = "unnamed_chapter"
        
        # Save to category subdirectory
        category_dir = Path(self.config["output"]["chapters_dir"]) / category
        category_dir.mkdir(exist_ok=True)
        
        output_file = category_dir / f"{clean_name}.qmd"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def convert_single_pdf(self, pdf_path):
        """Convert a single PDF file"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            print(f"PDF file not found: {pdf_path}")
            return None
        
        print(f"Processing: {pdf_path.name}")
        
        # Convert PDF to markdown
        raw_content = self.convert_pdf(pdf_path)
        if not raw_content:
            print(f"Failed to convert {pdf_path}")
            return None
        
        # Process content
        processed_content, category = self.process_content(raw_content, pdf_path.stem)
        
        # Save processed file
        output_file = self.save_processed_file(processed_content, pdf_path.stem, category)
        
        print(f"✓ Converted: {pdf_path.name} → {output_file}")
        print(f"  Category: {category}")
        print(f"  Output: {output_file}")
        
        return output_file
    
    def log_conversion(self, pdf_path, output_file, success, error=None):
        """Log conversion results"""
        log_file = Path("./automation/logs") / f"conversions_{datetime.now().strftime('%Y%m%d')}.log"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = f"[{timestamp}] {status}: {pdf_path}"
        if success:
            log_entry += f" → {output_file}"
        else:
            log_entry += f" (Error: {error})"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\\n")

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Convert PDF to Quarto markdown')
    parser.add_argument('pdf_path', help='Path to PDF file to convert')
    parser.add_argument('--config', default='./automation/config/conversion_config.json',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    converter = PDFToQuartoConverter(args.config)
    result = converter.convert_single_pdf(args.pdf_path)
    
    if result:
        print(f"\\nConversion completed successfully!")
        print(f"Output file: {result}")
    else:
        print(f"\\nConversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
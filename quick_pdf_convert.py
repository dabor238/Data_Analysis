"""
Simple PDF to Markdown converter using PyMuPDF
This is faster than Nougat and works well for text extraction
"""
import fitz  # PyMuPDF
from pathlib import Path
import re

def clean_text(text):
    """Clean up extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove page numbers and headers/footers (simple heuristic)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that are just numbers (likely page numbers)
        if line.strip().isdigit():
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def pdf_to_markdown(pdf_path, output_path):
    """Convert PDF to markdown using PyMuPDF"""
    
    print(f"Converting {pdf_path} to markdown...")
    
    # Open PDF
    doc = fitz.open(pdf_path)
    markdown_content = []
    
    markdown_content.append("# Introduction to Optimization\n")
    markdown_content.append(f"*Converted from PDF - {doc.page_count} pages*\n\n")
    markdown_content.append("---\n\n")
    
    # Process each page
    for page_num in range(len(doc)):
        print(f"Processing page {page_num + 1}/{len(doc)}...")
        
        page = doc[page_num]
        
        # Extract text with formatting
        text = page.get_text("text")
        
        if text.strip():
            # Clean the text
            text = clean_text(text)
            
            # Add page marker
            markdown_content.append(f"## Page {page_num + 1}\n\n")
            markdown_content.append(text)
            markdown_content.append("\n\n---\n\n")
    
    # Combine all content
    full_markdown = "".join(markdown_content)
    
    # Save to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
    
    print(f"\n✅ Conversion complete!")
    print(f"📄 Output saved to: {output_path}")
    print(f"📊 Total pages: {len(doc)}")
    
    # Also create a plain text version
    txt_path = output_path.with_suffix('.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
    
    print(f"📄 Plain text also saved to: {txt_path}")
    
    return output_path

if __name__ == "__main__":
    pdf_file = "source_pdfs/01_intro.pdf"
    output_file = "temp/nougat_output/01_intro_pymupdf.md"
    
    try:
        result = pdf_to_markdown(pdf_file, output_file)
        
        print(f"\n📖 To view the markdown file:")
        print(f"   code {result}")
        print(f"\n📖 To view the plain text file:")
        print(f"   type {result.replace('.md', '.txt')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

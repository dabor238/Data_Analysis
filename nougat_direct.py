"""
Direct Nougat conversion using Python API
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'  # Fix OpenMP issue on Windows

from pathlib import Path
from PIL import Image
import torch
from nougat import NougatModel
from nougat.utils.checkpoint import get_checkpoint
from nougat.postprocessing import markdown_compatible
import fitz  # PyMuPDF

def convert_pdf_to_markdown(pdf_path, output_path):
    """Convert PDF to markdown using Nougat"""
    
    print(f"Loading Nougat model...")
    
    # Initialize model
    model = NougatModel.from_pretrained("facebook/nougat-base")
    model.eval()
    
    if torch.cuda.is_available():
        model = model.to("cuda")
        print("Using GPU")
    else:
        print("Using CPU (this will be slower)")
    
    # Open PDF
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    all_text = []
    
    # Process each page
    for page_num in range(len(doc)):
        print(f"Processing page {page_num + 1}/{len(doc)}...")
        
        page = doc[page_num]
        
        # Render page to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert with Nougat
        with torch.no_grad():
            outputs = model.inference(image=img)
            text = outputs["predictions"][0]
            
        # Post-process
        text = markdown_compatible(text)
        all_text.append(text)
    
    # Combine all pages
    full_markdown = "\n\n".join(all_text)
    
    # Save to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
    
    print(f"\n✅ Conversion complete!")
    print(f"Output saved to: {output_path}")
    print(f"Total pages processed: {len(doc)}")
    
    return output_path

if __name__ == "__main__":
    pdf_file = "source_pdfs/01_intro.pdf"
    output_file = "temp/nougat_output/01_intro_nougat.md"
    
    try:
        result = convert_pdf_to_markdown(pdf_file, output_file)
        print(f"\n📄 To view the file, run:")
        print(f"  type {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

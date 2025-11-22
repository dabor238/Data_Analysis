"""
Simple Nougat PDF converter - avoids problematic imports
"""
import subprocess
import sys
from pathlib import Path

def convert_with_nougat_cli(pdf_path, output_dir):
    """Use Nougat CLI tool directly"""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {pdf_path.name} with Nougat...")
    print(f"Output directory: {output_dir}")
    
    # Use the nougat executable directly
    nougat_exe = Path(sys.executable).parent / "nougat.exe"
    
    if not nougat_exe.exists():
        print(f"Error: Nougat executable not found at {nougat_exe}")
        return None
    
    cmd = [
        str(nougat_exe),
        str(pdf_path),
        "-o", str(output_dir),
        "--no-skipping",
        "--markdown"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Conversion successful!")
            print(result.stdout)
            
            # Find output file
            output_files = list(output_dir.glob("*.mmd"))
            if output_files:
                print(f"\n📄 Output file: {output_files[0]}")
                return output_files[0]
            else:
                print("Warning: No .mmd file found in output directory")
                return None
        else:
            print(f"❌ Conversion failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Conversion timed out after 10 minutes")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    pdf_file = "source_pdfs/01_intro.pdf"
    output_directory = "temp/nougat_output"
    
    result = convert_with_nougat_cli(pdf_file, output_directory)
    
    if result:
        print(f"\n✅ SUCCESS! Markdown file created at: {result}")
        print(f"\nTo view the content, run:")
        print(f"  type {result}")
    else:
        print("\n❌ Conversion failed")

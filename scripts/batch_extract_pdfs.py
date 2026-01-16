#!/usr/bin/env python3
"""
Batch process all PDFs in ./pdfs directory and extract text to ./texts directory.
"""

import pdfplumber
from pathlib import Path
import sys
import argparse


def extract_full_text(pdf_path):
    """
    Extract all text from a PDF file including footnotes.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Complete text content as a string
    """
    full_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                full_text.append(f"\n{'='*80}\n")
                full_text.append(f"PAGE {i}\n")
                full_text.append(f"{'='*80}\n\n")
                full_text.append(text)
                full_text.append("\n")
    
    return ''.join(full_text)


def batch_process_pdfs(pdf_dir="./pdfs", output_dir="./texts"):
    """
    Process all PDFs in pdf_dir and save extracted text to output_dir.
    
    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory to save extracted text files
    """
    pdf_path = Path(pdf_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    
    # Get all PDF files
    pdf_files = sorted(pdf_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    print(f"Output directory: {output_path.absolute()}")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            # Extract text
            text = extract_full_text(pdf_file)
            
            # Create output filename
            output_file = output_path / f"{pdf_file.stem}.txt"
            
            # Save to file
            output_file.write_text(text, encoding='utf-8')
            
            # Calculate stats
            char_count = len(text)
            line_count = text.count('\n')
            
            print(f"  ✓ Success: {char_count:,} characters, {line_count:,} lines")
            print(f"  → Saved to: {output_file.name}")
            successful += 1
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Processing complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(pdf_files)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch extract text from PDF files including footnotes."
    )
    parser.add_argument(
        "-i", "--input",
        default="./pdfs",
        help="Input directory containing PDF files (default: ./pdfs)"
    )
    parser.add_argument(
        "-o", "--output",
        default="./texts",
        help="Output directory for extracted text files (default: ./texts)"
    )
    
    args = parser.parse_args()
    batch_process_pdfs(pdf_dir=args.input, output_dir=args.output)

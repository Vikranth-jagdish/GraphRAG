"""
PDF splitter utility for handling large PDF files that may cause memory issues.
"""

import os
import sys
from pathlib import Path
from typing import List
import argparse

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2 is required for PDF splitting. Install with: pip install PyPDF2")
    sys.exit(1)


def split_pdf(input_path: Path, pages_per_split: int = 20, output_dir: Path = None) -> List[Path]:
    """
    Split a large PDF into smaller chunks.

    Args:
        input_path: Path to the input PDF file
        pages_per_split: Number of pages per split file
        output_dir: Directory to save split files (defaults to same as input)

    Returns:
        List of paths to created split files
    """
    if output_dir is None:
        output_dir = input_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)

        print(f"Splitting {input_path.name} ({total_pages} pages) into chunks of {pages_per_split} pages...")

        split_files = []
        base_name = input_path.stem

        for start_page in range(0, total_pages, pages_per_split):
            end_page = min(start_page + pages_per_split, total_pages)

            # Create writer for this chunk
            writer = PdfWriter()

            # Add pages to writer
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            # Create output filename
            part_num = (start_page // pages_per_split) + 1
            output_filename = f"{base_name}_part{part_num:02d}.pdf"
            output_path = output_dir / output_filename

            # Write the split file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            split_files.append(output_path)
            print(f"  Created: {output_filename} (pages {start_page + 1}-{end_page})")

        print(f"Successfully split into {len(split_files)} files")
        return split_files

    except Exception as e:
        print(f"Error splitting PDF {input_path}: {e}")
        return []


def main():
    """Command line interface for PDF splitting."""
    parser = argparse.ArgumentParser(description="Split large PDF files into smaller chunks")
    parser.add_argument("input", help="Path to PDF file to split")
    parser.add_argument("--pages", "-p", type=int, default=20, help="Pages per split (default: 20)")
    parser.add_argument("--output", "-o", help="Output directory (defaults to same as input)")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File {input_path} does not exist")
        sys.exit(1)

    if not input_path.suffix.lower() == '.pdf':
        print(f"Error: {input_path} is not a PDF file")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else None

    split_files = split_pdf(input_path, args.pages, output_dir)

    if split_files:
        print(f"\nSplit files created in: {split_files[0].parent}")
        print("You can now convert these smaller files individually.")


if __name__ == "__main__":
    main()
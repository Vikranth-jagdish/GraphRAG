import os
import argparse
import sys
from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter


def write_markdown(md_text: str, out_path: Path, title: str | None = None, add_frontmatter: bool = False):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if add_frontmatter:
        header = [
            "---",
            f"title: {title or out_path.stem}",
            "source: pdf",
            "ingestion_notes: Converted from PDF via Docling",
            "tags: [pdf, converted]",
            f"converted_at: {datetime.now().isoformat()}",
            "---",
            "",
        ]
        content = "\n".join(header) + md_text
    else:
        content = md_text
    out_path.write_text(content, encoding="utf-8")


def convert_pdf(pdf_path: Path, output_dir: Path, add_frontmatter: bool = False) -> Path:
    # Check file size and warn if large
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 5:
        print(f"Warning: {pdf_path.name} is {file_size_mb:.1f}MB - consider splitting first with:")
        print(f"python -m pdf_extraction.splitter \"{pdf_path}\" --pages 15")

    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    md = result.document.export_to_markdown()

    # Sanitize name and write
    safe_name = pdf_path.stem.replace("/", "-").replace("\\", "-") + ".md"
    out_path = output_dir / safe_name
    write_markdown(md, out_path, title=pdf_path.stem, add_frontmatter=add_frontmatter)
    return out_path


def batch_convert(input_path: Path, output_dir: Path, recursive: bool, add_frontmatter: bool) -> list[Path]:
    pdfs = []
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        pdfs = [input_path]
    else:
        glob = "**/*.pdf" if recursive else "*.pdf"
        pdfs = list(input_path.glob(glob))

    outputs: list[Path] = []
    for pdf in pdfs:
        try:
            out = convert_pdf(pdf, output_dir, add_frontmatter=add_frontmatter)
            print(f"✓ Converted: {pdf} -> {out}")
            outputs.append(out)
        except Exception as e:
            print(f"✗ Failed: {pdf}: {e}")
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Convert PDFs to Markdown using Docling")
    parser.add_argument("--input", "-i", default=str(Path(__file__).parent / "imports"), help="PDF file or directory containing PDFs (default: pdf_extraction/imports)")
    parser.add_argument("--output", "-o", default="documents", help="Output directory for Markdown files")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories for PDFs")
    parser.add_argument("--frontmatter", action="store_true", help="Add YAML frontmatter to Markdown")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    # Ensure default imports directory exists to simplify UX
    if not input_path.exists():
        try:
            input_path.mkdir(parents=True, exist_ok=True)
            print(f"Created imports directory: {input_path}")
        except Exception as e:
            print(f"Failed to create imports directory {input_path}: {e}")
            sys.exit(1)

    outputs = batch_convert(input_path, output_dir, args.recursive, args.frontmatter)
    print(f"\nConverted {len(outputs)} file(s) to {output_dir}")


if __name__ == "__main__":
    main()



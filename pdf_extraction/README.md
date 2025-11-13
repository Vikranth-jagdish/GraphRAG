# PDF Extraction with Docling

Convert PDF files to Markdown and place them into `documents/` for ingestion.

## Install

```bash
pip install docling
```

## Usage

```bash
# Default (drop PDFs into pdf_extraction/imports/ and run)
python -m pdf_extraction.convert --frontmatter

# Single PDF
python -m pdf_extraction.convert --input path/to/file.pdf --output documents --frontmatter

# Directory (recursive)
python -m pdf_extraction.convert -i path/to/pdfs -o documents -r --frontmatter
```

The `--frontmatter` flag adds YAML metadata suitable for the ingestion pipeline.

## Notes

- Clean up headings in the generated Markdown if needed for better chunking.
- Consider adding `patient_id` to frontmatter for per-patient scoping.

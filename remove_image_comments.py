"""
Script to remove <!-- image --> comments from markdown files.
"""
import os
from pathlib import Path


def remove_image_comments(file_path: str) -> bool:
    """
    Remove <!-- image --> comments from a markdown file.

    Args:
        file_path (str): Path to the markdown file.

    Returns:
        bool: True if file was modified, False otherwise.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remove <!-- image --> comments (including variations with spaces)
    content = content.replace('<!-- image -->', '')

    # Check if content was modified
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


def main():
    """Process all markdown files in the documents directory."""
    documents_dir = Path('documents')

    if not documents_dir.exists():
        print(f"Directory {documents_dir} does not exist")
        return

    modified_count = 0

    for md_file in documents_dir.glob('*.md'):
        if remove_image_comments(str(md_file)):
            print(f"Modified: {md_file.name}")
            modified_count += 1

    print(f"\nTotal files modified: {modified_count}")


if __name__ == "__main__":
    main()

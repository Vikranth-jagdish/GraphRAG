#!/usr/bin/env python3
"""
Full test of medical entity extraction on your converted medical documents.
"""

from pathlib import Path

def extract_entities_from_text(text, terms_dict):
    """Extract entities from text using simple matching."""
    found_entities = {}
    text_lower = text.lower()

    for category, terms in terms_dict.items():
        found_entities[category] = []
        for term in terms:
            if len(term.split()) > 1:
                # Multi-word terms
                if term.lower() in text_lower:
                    found_entities[category].append(term)
            else:
                # Single words - check with word boundaries
                import re
                pattern = r'\b' + re.escape(term.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_entities[category].append(term)

    return found_entities

def main():
    """Test medical extraction on your documents."""
    print("Medical Entity Extraction - Full Document Test")
    print("=" * 50)

    try:
        from ingestion.medical_entities import MEDICAL_ENTITIES, extract_medical_values

        documents_dir = Path("documents")
        if not documents_dir.exists():
            print("Documents directory not found!")
            return

        md_files = list(documents_dir.glob("*.md"))
        print(f"Found {len(md_files)} documents to test")

        # Test on each document
        for doc_path in md_files:
            print(f"\n--- Testing: {doc_path.name} ---")

            try:
                content = doc_path.read_text(encoding='utf-8')
                # Use first 3000 characters for meaningful extraction
                sample_content = content[:3000]

                print(f"Document length: {len(content)} chars (testing first {len(sample_content)})")

                # Extract entities
                entities = extract_entities_from_text(sample_content, MEDICAL_ENTITIES)

                # Count total entities
                total_entities = sum(len(items) for items in entities.values())
                print(f"Total entities found: {total_entities}")

                # Show entities by category
                for category, items in entities.items():
                    if items:
                        # Remove duplicates and limit output
                        unique_items = list(set(items))[:8]  # Max 8 per category
                        print(f"  {category.title()}: {unique_items}")

                # Extract medical values
                values = extract_medical_values(sample_content)
                if values:
                    unique_values = list(set(values))[:5]  # Max 5 values
                    print(f"  Medical Values: {unique_values}")

                print("")

            except Exception as e:
                print(f"  ERROR processing {doc_path.name}: {e}")

        print("Test completed successfully!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
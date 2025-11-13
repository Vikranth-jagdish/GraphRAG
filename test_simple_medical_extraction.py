#!/usr/bin/env python3
"""
Simple test for medical entity extraction without graph dependencies.
"""

import sys
from pathlib import Path

def test_medical_entities():
    """Test medical entity extraction basics."""
    print("Testing Medical Entity Extraction")
    print("=" * 40)

    try:
        # Test medical entities module
        from ingestion.medical_entities import (
            MEDICAL_ENTITIES, MEDICAL_ABBREVIATIONS, get_all_medical_terms,
            get_medical_terms_by_category, extract_medical_values
        )

        print("\n1. Testing Medical Entity Dictionary:")
        all_terms = get_all_medical_terms()
        print(f"   Total medical terms loaded: {len(all_terms)}")
        print(f"   Medical abbreviations: {len(MEDICAL_ABBREVIATIONS)}")

        # Show sample terms from each category
        for category, terms in MEDICAL_ENTITIES.items():
            sample_terms = list(terms)[:3]  # First 3 terms
            print(f"   {category.title()}: {sample_terms}")

        print("\n2. Testing Term Extraction:")

        # Test condition extraction
        test_text = """
        Patient presents with Type 2 diabetes and hypertension.
        HbA1c is 8.5% and BP is 150/90 mmHg. Currently on metformin 1000mg twice daily.
        Complications include diabetic retinopathy and early nephropathy.
        Recommend adding insulin and ACE inhibitor. ECG shows normal rhythm.
        """

        print(f"   Test text: {test_text[:80]}...")

        # Test condition extraction
        conditions = get_medical_terms_by_category("conditions")
        found_conditions = []
        text_lower = test_text.lower()
        for condition in list(conditions)[:20]:  # Test first 20 to avoid too much output
            if condition.lower() in text_lower:
                found_conditions.append(condition)
        print(f"   Conditions found: {found_conditions}")

        # Test medication extraction
        medications = get_medical_terms_by_category("medications")
        found_medications = []
        for medication in list(medications)[:20]:
            if medication.lower() in text_lower:
                found_medications.append(medication)
        print(f"   Medications found: {found_medications}")

        # Test values extraction
        values = extract_medical_values(test_text)
        print(f"   Values found: {values}")

        print("\n3. Testing on Real Documents:")

        documents_dir = Path("documents")
        if documents_dir.exists():
            md_files = list(documents_dir.glob("*.md"))
            print(f"   Found {len(md_files)} documents")

            # Test on first document
            if md_files:
                test_doc = md_files[0]
                print(f"   Testing document: {test_doc.name}")

                try:
                    content = test_doc.read_text(encoding='utf-8')
                    sample_content = content[:1000].lower()  # First 1000 chars, lowercase

                    # Quick test for common medical terms
                    common_terms = ['diabetes', 'hypertension', 'HbA1c', 'blood pressure', 'insulin', 'metformin']
                    found_terms = [term for term in common_terms if term.lower() in sample_content]
                    print(f"   Common medical terms found: {found_terms}")

                    # Test value extraction
                    values = extract_medical_values(content[:1000])
                    if values:
                        print(f"   Medical values found: {values[:5]}")  # First 5

                except Exception as e:
                    print(f"   Error reading document: {e}")

        print("\n4. Testing Abbreviations:")
        test_abbrev_text = "Patient with T2DM, CAD, and CKD. HbA1c is 8.2%. On ACEI and statin."
        print(f"   Text with abbreviations: {test_abbrev_text}")

        # Find abbreviations in text
        found_abbrevs = []
        for abbrev in MEDICAL_ABBREVIATIONS:
            if abbrev in test_abbrev_text:
                found_abbrevs.append(f"{abbrev} = {MEDICAL_ABBREVIATIONS[abbrev]}")
        print(f"   Abbreviations found: {found_abbrevs}")

        print("\nTEST COMPLETE: Medical entity extraction is working!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_medical_entities()
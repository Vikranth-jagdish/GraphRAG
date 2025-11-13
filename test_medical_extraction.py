#!/usr/bin/env python3
"""
Test script for medical entity extraction from converted documents.
"""

import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_medical_extraction():
    """Test medical entity extraction on converted documents."""
    try:
        from ingestion.chunker import ChunkingConfig, create_chunker
        from ingestion.graph_builder import create_graph_builder, SimpleMedicalEntityExtractor
        from ingestion.medical_entities import get_all_medical_terms, MEDICAL_ABBREVIATIONS

        print("🧪 Testing Medical Entity Extraction")
        print("=" * 50)

        # Test 1: Check medical entities loaded
        print("\n1️⃣ Testing Medical Entity Dictionary:")
        all_terms = get_all_medical_terms()
        print(f"   📊 Total medical terms loaded: {len(all_terms)}")
        print(f"   🔤 Medical abbreviations: {len(MEDICAL_ABBREVIATIONS)}")

        # Sample terms from each category
        from ingestion.medical_entities import MEDICAL_ENTITIES
        for category, terms in MEDICAL_ENTITIES.items():
            sample_terms = list(terms)[:5]  # First 5 terms
            print(f"   {category.title()}: {sample_terms}")

        # Test 2: Simple pattern extraction
        print("\n2️⃣ Testing Simple Pattern Extraction:")
        extractor = SimpleMedicalEntityExtractor()

        test_text = """
        Patient has Type 2 diabetes with HbA1c 8.5%. Currently on metformin 1000mg.
        Blood pressure is 150/90 mmHg. Recommend adding ACE inhibitor and insulin.
        Annual fundoscopy shows early diabetic retinopathy. Creatinine is elevated at 2.1 mg/dl.
        """

        entities = extractor.extract_entities(test_text)
        print(f"   📝 Test text: {test_text[:100]}...")
        for category, items in entities.items():
            if items:
                print(f"   ✅ {category}: {items}")

        # Test 3: Test on actual converted documents
        print("\n3️⃣ Testing on Converted Documents:")

        documents_dir = Path("documents")
        if not documents_dir.exists():
            print("   ❌ Documents directory not found")
            return

        # Find some converted documents
        md_files = list(documents_dir.glob("*.md"))
        if not md_files:
            print("   ❌ No markdown documents found")
            return

        print(f"   📁 Found {len(md_files)} documents")

        # Test on first few documents
        for i, doc_path in enumerate(md_files[:3]):
            print(f"\n   📄 Testing document: {doc_path.name}")

            try:
                content = doc_path.read_text(encoding='utf-8')
                # Take first 1000 chars for testing
                sample_content = content[:1000]

                entities = extractor.extract_entities(sample_content)
                total_entities = sum(len(items) for items in entities.values())
                print(f"      📊 Total entities found: {total_entities}")

                for category, items in entities.items():
                    if items:
                        print(f"      {category}: {items[:5]}")  # Show first 5

            except Exception as e:
                print(f"      ❌ Error processing {doc_path.name}: {e}")

        # Test 4: Test chunking + entity extraction pipeline
        print("\n4️⃣ Testing Full Pipeline (Chunking + Entity Extraction):")

        config = ChunkingConfig(chunk_size=500, use_semantic_splitting=False)
        chunker = create_chunker(config)
        graph_builder = create_graph_builder()

        # Use diabetes document if available
        diabetes_docs = [f for f in md_files if "diabetes" in f.name.lower()]
        if diabetes_docs:
            test_doc = diabetes_docs[0]
            print(f"   📖 Testing with: {test_doc.name}")

            try:
                content = test_doc.read_text(encoding='utf-8')[:2000]  # Limit for testing

                # Chunk the document
                chunks = chunker.chunk_document(
                    content=content,
                    title=test_doc.stem,
                    source=test_doc.name
                )

                print(f"   ✂️  Created {len(chunks)} chunks")

                # Extract entities from chunks
                enriched_chunks = await graph_builder.extract_entities_from_chunks(
                    chunks,
                    use_llm_extraction=False  # Use rule-based for now
                )

                print(f"   🔍 Entity extraction complete")

                # Show results from first chunk
                if enriched_chunks:
                    first_chunk = enriched_chunks[0]
                    entities = first_chunk.metadata.get('entities', {})
                    total_entities = sum(len(items) for items in entities.values())
                    print(f"   📈 First chunk entities: {total_entities} total")

                    for category, items in entities.items():
                        if items:
                            print(f"      {category}: {items}")

            except Exception as e:
                print(f"   ❌ Pipeline test failed: {e}")
                import traceback
                traceback.print_exc()

        print("\n🎉 Medical Entity Extraction Test Complete!")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_medical_extraction())
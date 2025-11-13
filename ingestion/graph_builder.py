"""
Knowledge graph builder for extracting entities and relationships.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timezone
import asyncio
import re

from graphiti_core import Graphiti
from dotenv import load_dotenv

from .chunker import DocumentChunk
from .medical_entities import (
    MEDICAL_ENTITIES, MEDICAL_ABBREVIATIONS, get_all_medical_terms,
    get_medical_terms_by_category, expand_abbreviations, extract_medical_values
)

# Import graph utilities
try:
    from ..agent.graph_utils import GraphitiClient
except ImportError:
    # For direct execution or testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent.graph_utils import GraphitiClient

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds knowledge graph from document chunks."""
    
    def __init__(self):
        """Initialize graph builder."""
        self.graph_client = GraphitiClient()
        self._initialized = False
    
    async def initialize(self):
        """Initialize graph client."""
        if not self._initialized:
            await self.graph_client.initialize()
            self._initialized = True
    
    async def close(self):
        """Close graph client."""
        if self._initialized:
            await self.graph_client.close()
            self._initialized = False
    
    async def add_document_to_graph(
        self,
        chunks: List[DocumentChunk],
        document_title: str,
        document_source: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        batch_size: int = 3  # Reduced batch size for Graphiti
    ) -> Dict[str, Any]:
        """
        Add document chunks to the knowledge graph.
        
        Args:
            chunks: List of document chunks
            document_title: Title of the document
            document_source: Source of the document
            document_metadata: Additional metadata
            batch_size: Number of chunks to process in each batch
        
        Returns:
            Processing results
        """
        if not self._initialized:
            await self.initialize()
        
        if not chunks:
            return {"episodes_created": 0, "errors": []}
        
        logger.info(f"Adding {len(chunks)} chunks to knowledge graph for document: {document_title}")
        logger.info("⚠️ Large chunks will be truncated to avoid Graphiti token limits.")
        
        # Check for oversized chunks and warn
        oversized_chunks = [i for i, chunk in enumerate(chunks) if len(chunk.content) > 6000]
        if oversized_chunks:
            logger.warning(f"Found {len(oversized_chunks)} chunks over 6000 chars that will be truncated: {oversized_chunks}")
        
        episodes_created = 0
        errors = []
        
        # Process chunks one by one to avoid overwhelming Graphiti
        for i, chunk in enumerate(chunks):
            try:
                # Create episode ID
                episode_id = f"{document_source}_{chunk.index}_{datetime.now().timestamp()}"
                
                # Prepare episode content with size limits
                episode_content = self._prepare_episode_content(
                    chunk,
                    document_title,
                    document_metadata
                )
                
                # Create source description (shorter)
                source_description = f"Document: {document_title} (Chunk: {chunk.index})"
                
                # Add episode to graph
                await self.graph_client.add_episode(
                    episode_id=episode_id,
                    content=episode_content,
                    source=source_description,
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "document_title": document_title,
                        "document_source": document_source,
                        "chunk_index": chunk.index,
                        "original_length": len(chunk.content),
                        "processed_length": len(episode_content)
                    }
                )
                
                episodes_created += 1
                logger.info(f"✓ Added episode {episode_id} to knowledge graph ({episodes_created}/{len(chunks)})")
                
                # Small delay between each episode to reduce API pressure
                if i < len(chunks) - 1:
                    await asyncio.sleep(1.2)
                    
            except Exception as e:
                error_msg = f"Failed to add chunk {chunk.index} to graph: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                
                # Continue processing other chunks even if one fails
                continue
        
        result = {
            "episodes_created": episodes_created,
            "total_chunks": len(chunks),
            "errors": errors
        }
        
        logger.info(f"Graph building complete: {episodes_created} episodes created, {len(errors)} errors")
        return result
    
    def _prepare_episode_content(
        self,
        chunk: DocumentChunk,
        document_title: str,
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Prepare episode content with minimal context to avoid token limits.
        
        Args:
            chunk: Document chunk
            document_title: Title of the document
            document_metadata: Additional metadata
        
        Returns:
            Formatted episode content (optimized for Graphiti)
        """
        # Limit chunk content to avoid Graphiti's 8192 token limit
        # Estimate ~4 chars per token, keep content under 6000 chars to leave room for processing
        max_content_length = 6000
        
        content = chunk.content
        if len(content) > max_content_length:
            # Truncate content but try to end at a sentence boundary
            truncated = content[:max_content_length]
            last_sentence_end = max(
                truncated.rfind('. '),
                truncated.rfind('! '),
                truncated.rfind('? ')
            )
            
            if last_sentence_end > max_content_length * 0.7:  # If we can keep 70% and end cleanly
                content = truncated[:last_sentence_end + 1] + " [TRUNCATED]"
            else:
                content = truncated + "... [TRUNCATED]"
            
            logger.warning(f"Truncated chunk {chunk.index} from {len(chunk.content)} to {len(content)} chars for Graphiti")
        
        # Add minimal context (just document title for now)
        if document_title and len(content) < max_content_length - 100:
            episode_content = f"[Doc: {document_title[:50]}]\n\n{content}"
        else:
            episode_content = content
        
        return episode_content
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count (4 chars per token)."""
        return len(text) // 4
    
    def _is_content_too_large(self, content: str, max_tokens: int = 7000) -> bool:
        """Check if content is too large for Graphiti processing."""
        return self._estimate_tokens(content) > max_tokens
    
    async def extract_entities_from_chunks(
        self,
        chunks: List[DocumentChunk],
        extract_conditions: bool = True,
        extract_medications: bool = True,
        extract_tests: bool = True,
        extract_organizations: bool = True,
        use_llm_extraction: bool = False
    ) -> List[DocumentChunk]:
        """
        Extract medical entities from chunks and add to metadata.

        Args:
            chunks: List of document chunks
            extract_conditions: Whether to extract medical conditions
            extract_medications: Whether to extract medications
            extract_tests: Whether to extract medical tests
            extract_organizations: Whether to extract medical organizations
            use_llm_extraction: Whether to use LLM for enhanced extraction

        Returns:
            Chunks with medical entity metadata added
        """
        logger.info(f"Extracting entities from {len(chunks)} chunks")
        
        enriched_chunks = []
        
        for chunk in chunks:
            entities = {
                "conditions": [],
                "medications": [],
                "tests": [],
                "organizations": [],
                "values": [],
                "symptoms": [],
                "procedures": []
            }

            content = chunk.content

            if use_llm_extraction:
                # Use LLM-based extraction for more sophisticated entity recognition
                entities = await self._extract_entities_with_llm(content)
            else:
                # Use rule-based extraction
                if extract_conditions:
                    entities["conditions"] = self._extract_medical_conditions(content)

                if extract_medications:
                    entities["medications"] = self._extract_medications(content)

                if extract_tests:
                    entities["tests"] = self._extract_medical_tests(content)

                if extract_organizations:
                    entities["organizations"] = self._extract_medical_organizations(content)

                # Always extract medical values and symptoms (important for medical context)
                entities["values"] = self._extract_medical_values(content)
                entities["symptoms"] = self._extract_symptoms(content)
                entities["procedures"] = self._extract_procedures(content)
            
            # Create enriched chunk
            enriched_chunk = DocumentChunk(
                content=chunk.content,
                index=chunk.index,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                metadata={
                    **chunk.metadata,
                    "entities": entities,
                    "entity_extraction_date": datetime.now().isoformat()
                },
                token_count=chunk.token_count
            )
            
            # Preserve embedding if it exists
            if hasattr(chunk, 'embedding'):
                enriched_chunk.embedding = chunk.embedding
            
            enriched_chunks.append(enriched_chunk)
        
        logger.info("Entity extraction complete")
        return enriched_chunks
    
    def _extract_medical_conditions(self, text: str) -> List[str]:
        """Extract medical conditions from text."""
        conditions = get_medical_terms_by_category("conditions")
        found_conditions = set()
        text_lower = text.lower()

        for condition in conditions:
            # Case-insensitive search with word boundaries for multi-word terms
            if len(condition.split()) > 1:
                # For multi-word terms, use exact phrase matching
                if condition.lower() in text_lower:
                    found_conditions.add(condition)
            else:
                # For single words, use word boundaries
                pattern = r'\b' + re.escape(condition.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_conditions.add(condition)

        return list(found_conditions)

    def _extract_medications(self, text: str) -> List[str]:
        """Extract medications from text."""
        medications = get_medical_terms_by_category("medications")
        found_medications = set()
        text_lower = text.lower()

        for medication in medications:
            if len(medication.split()) > 1:
                if medication.lower() in text_lower:
                    found_medications.add(medication)
            else:
                pattern = r'\b' + re.escape(medication.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_medications.add(medication)

        return list(found_medications)

    def _extract_medical_tests(self, text: str) -> List[str]:
        """Extract medical tests from text."""
        tests = get_medical_terms_by_category("tests")
        found_tests = set()
        text_lower = text.lower()

        for test in tests:
            if len(test.split()) > 1:
                if test.lower() in text_lower:
                    found_tests.add(test)
            else:
                pattern = r'\b' + re.escape(test.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_tests.add(test)

        return list(found_tests)

    def _extract_medical_organizations(self, text: str) -> List[str]:
        """Extract medical organizations from text."""
        organizations = get_medical_terms_by_category("organizations")
        found_orgs = set()

        for org in organizations:
            if org in text:
                found_orgs.add(org)

        return list(found_orgs)

    def _extract_medical_values(self, text: str) -> List[str]:
        """Extract medical values and ranges from text."""
        return extract_medical_values(text)

    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text."""
        symptoms = get_medical_terms_by_category("symptoms")
        found_symptoms = set()
        text_lower = text.lower()

        for symptom in symptoms:
            if len(symptom.split()) > 1:
                if symptom.lower() in text_lower:
                    found_symptoms.add(symptom)
            else:
                pattern = r'\b' + re.escape(symptom.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_symptoms.add(symptom)

        return list(found_symptoms)

    def _extract_procedures(self, text: str) -> List[str]:
        """Extract medical procedures from text."""
        procedures = get_medical_terms_by_category("procedures")
        found_procedures = set()
        text_lower = text.lower()

        for procedure in procedures:
            if len(procedure.split()) > 1:
                if procedure.lower() in text_lower:
                    found_procedures.add(procedure)
            else:
                pattern = r'\b' + re.escape(procedure.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_procedures.add(procedure)

        return list(found_procedures)

    async def _extract_entities_with_llm(self, content: str) -> Dict[str, List[str]]:
        """
        Extract medical entities using LLM for more sophisticated recognition.

        Args:
            content: Text content to analyze

        Returns:
            Dictionary with extracted medical entities
        """
        # Import providers for LLM access
        try:
            from ..agent.providers import get_llm_model, get_gemini_client
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from agent.providers import get_llm_model, get_gemini_client

        # Medical entity extraction prompt
        extraction_prompt = f"""
        You are a medical information extraction system. Extract medical entities from the following text and categorize them.

        Text: "{content[:2000]}"  # Limit content to avoid token limits

        Extract and categorize the following types of medical entities:

        1. **Medical Conditions**: Diseases, disorders, syndromes (e.g., diabetes, hypertension, CAD)
        2. **Medications**: Drugs, medications, drug classes (e.g., metformin, ACE inhibitor)
        3. **Medical Tests**: Laboratory tests, diagnostic procedures (e.g., HbA1c, ECG, fundoscopy)
        4. **Medical Organizations**: Healthcare institutions, guidelines (e.g., ICMR, WHO, ADA)
        5. **Medical Values**: Test results, target ranges (e.g., HbA1c <7%, BP <140/90)
        6. **Symptoms**: Signs and symptoms (e.g., polyuria, chest pain, dyspnea)
        7. **Procedures**: Medical procedures, interventions (e.g., insulin injection, angioplasty)

        Return the results in JSON format:
        {{
            "conditions": ["list of medical conditions"],
            "medications": ["list of medications"],
            "tests": ["list of medical tests"],
            "organizations": ["list of organizations"],
            "values": ["list of medical values"],
            "symptoms": ["list of symptoms"],
            "procedures": ["list of procedures"]
        }}

        Only extract entities that are clearly present in the text. Do not infer or add entities not mentioned.
        """

        try:
            # Try to get OpenAI model first, then fall back to Gemini
            try:
                model = get_llm_model()
                # This would need to be implemented based on your LLM provider setup
                # For now, return empty entities to avoid errors
                logger.info("LLM-based extraction requested but not fully implemented yet")
                return {
                    "conditions": [],
                    "medications": [],
                    "tests": [],
                    "organizations": [],
                    "values": [],
                    "symptoms": [],
                    "procedures": []
                }
            except Exception as e:
                logger.warning(f"Failed to use primary LLM model: {e}")
                # Fall back to rule-based extraction
                return {
                    "conditions": self._extract_medical_conditions(content),
                    "medications": self._extract_medications(content),
                    "tests": self._extract_medical_tests(content),
                    "organizations": self._extract_medical_organizations(content),
                    "values": self._extract_medical_values(content),
                    "symptoms": self._extract_symptoms(content),
                    "procedures": self._extract_procedures(content)
                }

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            # Fall back to rule-based extraction
            return {
                "conditions": self._extract_medical_conditions(content),
                "medications": self._extract_medications(content),
                "tests": self._extract_medical_tests(content),
                "organizations": self._extract_medical_organizations(content),
                "values": self._extract_medical_values(content),
                "symptoms": self._extract_symptoms(content),
                "procedures": self._extract_procedures(content)
            }

    async def clear_graph(self):
        """Clear all data from the knowledge graph."""
        if not self._initialized:
            await self.initialize()
        
        logger.warning("Clearing knowledge graph...")
        await self.graph_client.clear_graph()
        logger.info("Knowledge graph cleared")


class SimpleMedicalEntityExtractor:
    """Simple rule-based medical entity extractor as fallback."""

    def __init__(self):
        """Initialize medical extractor with patterns."""
        self.condition_patterns = [
            r'\b(?:diabetes|hypertension|CAD|CKD|obesity|dyslipidemia)\b',
            r'\b(?:Type [12] diabetes|T[12]DM|GDM)\b',
            r'\b(?:diabetic retinopathy|diabetic nephropathy|diabetic neuropathy)\b',
            r'\b(?:myocardial infarction|MI|stroke|heart failure)\b'
        ]

        self.medication_patterns = [
            r'\b(?:metformin|insulin|glipizide|gliclazide|pioglitazone)\b',
            r'\b(?:lisinopril|enalapril|losartan|amlodipine|atenolol)\b',
            r'\b(?:atorvastatin|simvastatin|rosuvastatin)\b',
            r'\b(?:ACE inhibitor|ARB|beta blocker|diuretic|statin)\b'
        ]

        self.test_patterns = [
            r'\b(?:HbA1c|fasting glucose|FPG|OGTT|BMI|blood pressure|BP)\b',
            r'\b(?:ECG|echocardiogram|fundoscopy|creatinine|LDL|HDL)\b',
            r'\b(?:lipid profile|liver function|LFT|ACR)\b'
        ]

        self.value_patterns = [
            r'HbA1c\s*[<>=≤≥]\s*\d+\.?\d*%?',
            r'BP\s*[<>=≤≥]\s*\d+/\d+',
            r'BMI\s*[<>=≤≥]\s*\d+\.?\d*',
            r'\d+\s*mg/dl',
            r'\d+\s*mmHg'
        ]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities using patterns."""
        entities = {
            "conditions": [],
            "medications": [],
            "tests": [],
            "values": []
        }

        # Extract conditions
        for pattern in self.condition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["conditions"].extend(matches)

        # Extract medications
        for pattern in self.medication_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["medications"].extend(matches)

        # Extract tests
        for pattern in self.test_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["tests"].extend(matches)

        # Extract values
        for pattern in self.value_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["values"].extend(matches)

        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities


# Factory function
def create_graph_builder() -> GraphBuilder:
    """Create graph builder instance."""
    return GraphBuilder()


# Example usage
async def main():
    """Example usage of the graph builder."""
    from .chunker import ChunkingConfig, create_chunker
    
    # Create chunker and graph builder
    config = ChunkingConfig(chunk_size=300, use_semantic_splitting=False)
    chunker = create_chunker(config)
    graph_builder = create_graph_builder()
    
    sample_text = """
    ICMR Guidelines for Management of Type 2 Diabetes recommend maintaining
    HbA1c ≤7% for optimal glycemic control. Patients with diabetes should be
    screened for diabetic retinopathy through dilated fundoscopy annually.

    First-line treatment for Type 2 diabetes includes metformin along with
    lifestyle modifications. If HbA1c targets are not achieved, combination
    therapy with insulin or DPP4 inhibitors may be necessary.

    Hypertension management requires maintaining BP <140/90 mmHg. ACE inhibitors
    or ARBs are preferred for patients with diabetes and kidney disease.
    """
    
    # Chunk the document
    chunks = chunker.chunk_document(
        content=sample_text,
        title="Medical Treatment Guidelines",
        source="medical_guidelines.md"
    )
    
    print(f"Created {len(chunks)} chunks")
    
    # Extract entities
    enriched_chunks = await graph_builder.extract_entities_from_chunks(chunks)
    
    for i, chunk in enumerate(enriched_chunks):
        print(f"Chunk {i}: {chunk.metadata.get('entities', {})}")
    
    # Add to knowledge graph
    try:
        result = await graph_builder.add_document_to_graph(
            chunks=enriched_chunks,
            document_title="ICMR Diabetes Management Guidelines",
            document_source="example.md",
            document_metadata={"topic": "Diabetes", "date": "2024"}
        )
        
        print(f"Graph building result: {result}")
        
    except Exception as e:
        print(f"Graph building failed: {e}")
    
    finally:
        await graph_builder.close()


if __name__ == "__main__":
    asyncio.run(main())
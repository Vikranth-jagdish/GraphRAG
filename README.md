# Medical Knowledge Graph RAG - Clinical Decision Support System

An advanced AI-powered clinical decision support system that combines traditional RAG (Retrieval-Augmented Generation) with knowledge graph capabilities to provide evidence-based differential diagnosis and treatment planning. The system processes ICMR (Indian Council of Medical Research) medical guidelines and builds a comprehensive knowledge graph of medical entities, relationships, and clinical protocols. It uses PostgreSQL with pgvector for semantic search and Neo4j with Graphiti for temporal knowledge graphs to enable intelligent clinical reasoning.

Built with:

- Pydantic AI for the AI Agent Framework
- Graphiti for the Knowledge Graph
- Postgres with PGVector for the Vector Database
- Neo4j for the Knowledge Graph Engine (Graphiti connects to this)
- FastAPI for the Agent API

## Overview

This system is designed for healthcare professionals and clinical decision support, providing three main capabilities:

1. **Document Ingestion Pipeline**: Processes medical guidelines and clinical documents using semantic chunking, extracts medical entities (conditions, medications, tests, procedures, symptoms), and builds both vector embeddings and knowledge graph relationships
2. **AI Clinical Agent Interface**: A conversational agent powered by Pydantic AI that can search across both vector database and knowledge graph to provide evidence-based clinical recommendations
3. **Streaming API**: FastAPI backend with real-time streaming responses for differential diagnosis, treatment planning, and clinical queries

### Medical Capabilities

The system provides comprehensive clinical decision support:

- **Differential Diagnosis Generation**: Analyzes patient presentations and generates evidence-based differential diagnoses ranked by likelihood, with citations from ICMR guidelines
- **Treatment Plan Recommendations**: Provides structured treatment plans including:
  - Assessment plans (laboratory tests, imaging, screening, monitoring)
  - Pharmacologic interventions (medications with dosages and protocols)
  - Non-pharmacologic interventions (lifestyle modifications, procedures)
  - Patient education and counseling recommendations
  - Follow-up and monitoring schedules
- **Medical Entity Extraction**: Automatically identifies and extracts:
  - Medical conditions (diabetes, hypertension, cancers, complications)
  - Medications (insulin, antihypertensives, chemotherapy agents, etc.)
  - Medical tests (HbA1c, PSA, imaging studies, biopsies, etc.)
  - Procedures (surgeries, radiotherapy, chemotherapy regimens)
  - Symptoms and signs
  - Medical values and targets (HbA1c <7%, BP <140/90, etc.)
  - Anatomical structures and systems
- **Knowledge Graph Relationships**: Builds temporal and relational connections between:
  - Conditions and their complications
  - Medications and their indications/contraindications
  - Tests and their diagnostic purposes
  - Treatment protocols and their evidence base
  - Comorbidities and their interactions

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (such as Neon) with pgvector extension
- Neo4j database (for knowledge graph)
- LLM Provider API key (OpenAI, Ollama, Gemini, etc.)

## Installation

### 1. Set up a virtual environment

```bash
# Create and activate virtual environment
python -m venv venv       # python3 on Linux
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up required tables in Postgres

Execute the SQL in `sql/schema.sql` to create all necessary tables, indexes, and functions.

Be sure to change the embedding dimensions on lines 31, 67, and 100 based on your embedding model. OpenAI's text-embedding-3-small is 1536 and nomic-embed-text from Ollama is 768 dimensions, for reference.

Note that this script will drop all tables before creating/recreating!

### 4. Set up Neo4j

You have a couple easy options for setting up Neo4j:

#### Option A: Using Local-AI-Packaged (Simplified setup - Recommended)

1. Clone the repository: `git clone https://github.com/coleam00/local-ai-packaged`
2. Follow the installation instructions to set up Neo4j through the package
3. Note the username and password you set in .env and the URI will be bolt://localhost:7687

#### Option B: Using Neo4j Desktop

1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new project and add a local DBMS
3. Start the DBMS and set a password
4. Note the connection details (URI, username, password)

### 5. Configure environment variables

Create a `.env` file in the project root:

```bash
# Database Configuration (example Neon connection string)
DATABASE_URL=postgresql://username:password@ep-example-12345.us-east-2.aws.neon.tech/neondb

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# LLM Provider Configuration (choose one)
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-api-key
LLM_CHOICE=gpt-4.1-mini

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-your-api-key
EMBEDDING_MODEL=text-embedding-3-small

# Ingestion Configuration
INGESTION_LLM_CHOICE=gpt-4.1-nano  # Faster model for processing

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
APP_PORT=8058
```

For other LLM providers:

```bash
# Ollama (Local)
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_CHOICE=qwen2.5:14b-instruct

# OpenRouter
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your-openrouter-key
LLM_CHOICE=anthropic/claude-3-5-sonnet

# Gemini
LLM_PROVIDER=gemini
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_API_KEY=your-gemini-key
LLM_CHOICE=gemini-2.5-flash
```

## Quick Start

### 1. Prepare Your Medical Documents

Add your medical guideline documents (markdown format) to the `documents/` folder:

```bash
mkdir -p documents
# Add your medical guideline files
# Example: documents/ICMR_Guidelines_for_Management_of_Type_2_Diabetes.md
#          documents/ICMR_STANDARD_TREATMENT_GUIDELINES_OF_HYPERTENSION.md
```

**Current Medical Documents Included**:

The system comes pre-configured with ICMR (Indian Council of Medical Research) guidelines:

- **Diabetes Management**:
  - Type 1 Diabetes Mellitus guidelines (11 parts)
  - Type 2 Diabetes Mellitus guidelines
  - Gestational Diabetes Mellitus guidelines
  - Standard Treatment Workflow for Diabetes

- **Hypertension**:
  - ICMR Standard Treatment Guidelines of Hypertension 2016
  - RSSDI guidelines for management of hypertension in patients with diabetes mellitus

- **Oncology**:
  - Breast Cancer Consensus documents
  - Prostate Cancer Consensus documents (3 parts)
  - Colorectal Cancer Consensus documents

**Note**: Processing all medical documents into the knowledge graph will take significant time (potentially 30+ minutes to several hours) due to the computational complexity of medical entity extraction and relationship building. The system extracts thousands of medical entities and builds complex relationships between conditions, medications, tests, and procedures.

### 2. Run Document Ingestion

**Important**: You must run ingestion first to populate the databases before the agent can provide meaningful clinical responses.

```bash
# Basic ingestion with semantic chunking and medical entity extraction
python -m ingestion.ingest

# Clean existing data and re-ingest everything
python -m ingestion.ingest --clean

# Custom settings for faster processing (no knowledge graph)
python -m ingestion.ingest --chunk-size 800 --no-semantic --verbose
```

The ingestion process will:

- Parse and semantically chunk medical documents
- Extract medical entities (conditions, medications, tests, procedures, symptoms, values)
- Generate embeddings for vector search
- Build knowledge graph relationships between medical entities
- Store everything in PostgreSQL and Neo4j

**Medical Entity Extraction**: The system uses comprehensive medical dictionaries to extract:
- **Conditions**: Diabetes (Type 1, Type 2, Gestational), Hypertension, Cancers (Breast, Prostate, Colorectal), Complications, etc.
- **Medications**: Insulin formulations, antihypertensives, chemotherapy agents, hormone therapy, etc.
- **Tests**: Laboratory tests (HbA1c, PSA, lipid profiles), imaging (CT, MRI, PET-CT), biopsies, etc.
- **Procedures**: Surgeries, radiotherapy, chemotherapy regimens, lifestyle interventions, etc.
- **Values**: Clinical targets (HbA1c <7%, BP <140/90, PSA ranges, etc.)

NOTE that this can take a while because knowledge graphs are very computationally expensive, especially with comprehensive medical entity extraction!

### 2b. (Optional) Convert PDFs to Markdown

You can convert medical PDF documents into Markdown for ingestion using Docling:

```bash
pip install docling

# Single PDF
python -m pdf_extraction.convert --input path/to/medical_guideline.pdf --output documents --frontmatter

# Directory (recursive)
python -m pdf_extraction.convert -i path/to/medical_pdfs -o documents -r --frontmatter
```

The `--frontmatter` flag adds YAML metadata to help with ingestion and optional per-patient scoping.

### 3. Configure Agent Behavior (Optional)

Before running the API server, you can customize the clinical agent's behavior by modifying the system prompt in `agent/prompts.py`. The system prompt controls:

- When to use vector search vs knowledge graph search for clinical queries
- How to combine results from different sources
- The agent's clinical reasoning strategy for tool selection
- Format and structure of clinical responses

Medical-specific prompts for differential diagnosis and treatment planning are defined in `agent/medical_prompts.py`.

### 4. Start the API Server (Terminal 1)

```bash
# Start the FastAPI server
python -m agent.api

# Server will be available at http://localhost:8058
```

### 5. Use the Command Line Interface (Terminal 2)

The CLI provides an interactive way to query the clinical agent and see which tools it uses for each clinical query.

```bash
# Start the CLI in a separate terminal from the API (connects to default API at http://localhost:8058)
python cli.py

# Connect to a different URL
python cli.py --url http://localhost:8058

# Connect to a specific port
python cli.py --port 8080
```

#### CLI Features

- **Real-time streaming responses** - See the agent's clinical response as it's generated
- **Tool usage visibility** - Understand which tools the agent used:
  - `vector_search` - Semantic similarity search across medical literature
  - `graph_search` - Knowledge graph queries for medical relationships
  - `hybrid_search` - Combined search approach for comprehensive clinical reasoning
- **Session management** - Maintains conversation context for patient cases
- **Color-coded output** - Easy to read clinical responses and tool information

#### Example CLI Session

```
🤖 Medical Knowledge Graph RAG CLI
============================================================
Connected to: http://localhost:8058

You: A 45-year-old male presents with polyuria, polydipsia, and weight loss. Random blood glucose is 280 mg/dL. What are the differential diagnoses?

🤖 Assistant:
Based on the clinical presentation, I'll search for relevant guidelines on diabetes and related conditions...

**Provisional Diagnosis**: Type 2 Diabetes Mellitus

**Differential Diagnoses**:
1. Type 2 Diabetes Mellitus - Most likely given age, symptoms, and glucose level
2. Type 1 Diabetes Mellitus - Consider if rapid onset or ketosis present
3. Secondary Diabetes - Rule out if other causes present
...

**Recommended Investigations**:
- HbA1c to confirm diagnosis and assess glycemic control
- Fasting plasma glucose
- C-peptide levels to assess insulin production
...

**Treatment Plan**:
- Lifestyle modification and medical nutrition therapy
- Metformin as first-line pharmacologic therapy
- Patient education on self-monitoring blood glucose
...

**Citations**:
- ICMR Guidelines for Management of Type 2 Diabetes 2018
- ICMR Standard Treatment Workflow for Diabetes Mellitus

🛠 Tools Used:
  1. vector_search (query='diabetes symptoms polyuria polydipsia', limit=10)
  2. graph_search (query='diabetes diagnosis criteria')
  3. hybrid_search (query='Type 2 diabetes treatment guidelines', limit=10)

────────────────────────────────────────────────────────────

You: What are the treatment options for locally advanced breast cancer?

🤖 Assistant:
Based on ICMR consensus guidelines, locally advanced breast cancer (LABC) requires a multidisciplinary approach...

**Treatment Recommendations**:
- Neoadjuvant chemotherapy followed by surgery
- Modified radical mastectomy or breast-conserving surgery based on response
- Adjuvant radiotherapy
- Hormone therapy for hormone receptor-positive disease
...

🛠 Tools Used:
  1. hybrid_search (query='locally advanced breast cancer treatment', limit=10)
  2. get_entity_relationships (entity='breast cancer')
```

#### CLI Commands

- `help` - Show available commands
- `health` - Check API connection status
- `clear` - Clear current session
- `exit` or `quit` - Exit the CLI

### 6. Test the System

#### Health Check

```bash
curl http://localhost:8058/health
```

#### Chat with the Clinical Agent (Non-streaming)

```bash
curl -X POST "http://localhost:8058/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the diagnostic criteria for Type 2 diabetes according to ICMR guidelines?"
  }'
```

#### Streaming Chat

```bash
curl -X POST "http://localhost:8058/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "A patient with Type 2 diabetes and hypertension. What is the recommended blood pressure target and first-line antihypertensive medication?"
  }'
```

## How It Works

### The Power of Hybrid RAG + Knowledge Graph for Clinical Decision Support

This system combines the best of both worlds for medical knowledge retrieval:

**Vector Database (PostgreSQL + pgvector)**:

- Semantic similarity search across medical document chunks
- Fast retrieval of contextually relevant clinical information
- Excellent for finding similar cases, treatment protocols, and guideline sections
- Enables natural language queries about medical conditions, symptoms, and treatments

**Knowledge Graph (Neo4j + Graphiti)**:

- Temporal and relational connections between medical entities
- Graph traversal for discovering relationships between:
  - Conditions and their complications (e.g., diabetes → diabetic nephropathy)
  - Medications and their indications (e.g., metformin → Type 2 diabetes)
  - Tests and their diagnostic purposes (e.g., HbA1c → diabetes monitoring)
  - Treatment protocols and their evidence base
  - Comorbidities and their interactions (e.g., diabetes + hypertension)
- Perfect for understanding disease progression, treatment pathways, and clinical relationships
- Temporal tracking of how medical knowledge evolves over time

**Intelligent Clinical Agent**:

- Automatically chooses the best search strategy based on query type
- Combines results from both databases for comprehensive clinical reasoning
- Provides evidence-based responses with source citations from ICMR guidelines
- Generates structured differential diagnoses and treatment plans
- Considers patient context (gender, age) for appropriate recommendations

### Medical Entity Extraction and Knowledge Graph Building

The system performs comprehensive medical entity extraction during ingestion:

1. **Rule-Based Extraction**: Uses extensive medical dictionaries covering:
   - 200+ medical conditions (diabetes types, cancers, cardiovascular diseases, etc.)
   - 150+ medications (insulin, antihypertensives, chemotherapy agents, etc.)
   - 250+ medical tests (laboratory tests, imaging studies, biopsies, etc.)
   - 200+ procedures (surgeries, radiotherapy, lifestyle interventions, etc.)
   - Symptoms, signs, anatomical terms, and medical values

2. **LLM-Enhanced Extraction** (optional): Uses language models for more sophisticated entity recognition and relationship extraction

3. **Knowledge Graph Construction**: Builds relationships such as:
   - Condition → treated_by → Medication
   - Condition → diagnosed_by → Test
   - Condition → managed_by → Procedure
   - Medication → contraindicated_in → Condition
   - Test → indicates → Condition

### Example Clinical Queries

The system excels at various types of clinical queries:

- **Symptom-Based Diagnosis**: "Patient presents with polyuria, polydipsia, and weight loss. What are the differential diagnoses?"
  - Uses vector search to find similar clinical presentations
  - Uses knowledge graph to explore relationships between symptoms and conditions

- **Treatment Protocol Queries**: "What is the first-line treatment for Type 2 diabetes according to ICMR guidelines?"
  - Uses vector search to find relevant treatment guidelines
  - Uses knowledge graph to understand medication relationships and contraindications

- **Comorbidity Questions**: "How should hypertension be managed in a patient with Type 2 diabetes?"
  - Combines vector search for comorbid condition guidelines
  - Uses knowledge graph to understand interactions between conditions and medications

- **Complex Clinical Reasoning**: "What are the treatment options for locally advanced breast cancer in a postmenopausal woman?"
  - Combines vector search for treatment protocols
  - Uses knowledge graph to understand staging, receptor status, and treatment pathways
  - Considers patient-specific factors (age, menopausal status)

- **Temporal Questions**: "What is the recommended follow-up schedule after prostate cancer treatment?"
  - Leverages Graphiti's temporal capabilities to track treatment protocols over time

### Why This Architecture Works So Well for Medical Applications

1. **Complementary Strengths**: Vector search finds semantically similar clinical content while knowledge graphs reveal hidden relationships between medical entities

2. **Evidence-Based**: All recommendations are grounded in ICMR guidelines with proper citations

3. **Comprehensive Medical Entity Recognition**: Extensive medical dictionaries ensure accurate extraction of conditions, medications, tests, and procedures

4. **Temporal Intelligence**: Graphiti tracks how medical knowledge and treatment protocols evolve over time

5. **Clinical Reasoning**: The hybrid approach enables sophisticated clinical reasoning that combines semantic understanding with relationship analysis

6. **Flexible LLM Support**: Switch between OpenAI, Ollama, OpenRouter, or Gemini based on your needs and cost considerations

7. **Production Ready**: Comprehensive testing, error handling, and monitoring for clinical applications

## API Documentation

Visit http://localhost:8058/docs for interactive API documentation once the server is running.

The API provides endpoints for:
- General clinical chat queries
- Streaming chat responses
- Differential diagnosis generation
- Treatment plan recommendations
- Document search and retrieval
- Health status checks

## Key Features

- **Hybrid Search**: Seamlessly combines vector similarity and graph traversal for comprehensive clinical reasoning
- **Medical Entity Extraction**: Comprehensive extraction of conditions, medications, tests, procedures, and clinical values
- **Knowledge Graph Relationships**: Builds temporal and relational connections between medical entities
- **Evidence-Based Recommendations**: All clinical recommendations cite specific ICMR guidelines and medical literature
- **Differential Diagnosis**: Generates ranked differential diagnoses with clinical rationale and citations
- **Treatment Planning**: Provides structured treatment plans including assessment, pharmacologic, and non-pharmacologic interventions
- **Streaming Responses**: Real-time AI responses with Server-Sent Events
- **Flexible Providers**: Support for multiple LLM and embedding providers
- **Semantic Chunking**: Intelligent document splitting using LLM analysis for medical documents
- **Gender-Specific Safety**: Ensures recommendations are appropriate for patient gender
- **Production Ready**: Comprehensive testing, logging, and error handling

## Project Structure

```
agentic-rag-knowledge-graph/
├── agent/                      # AI agent and API
│   ├── agent.py               # Main Pydantic AI agent
│   ├── api.py                 # FastAPI application
│   ├── providers.py           # LLM provider abstraction
│   ├── models.py              # Data models (including medical models)
│   ├── prompts.py             # System prompts for clinical agent
│   ├── medical_prompts.py     # Medical-specific prompts (differential diagnosis, treatment planning)
│   ├── tools.py               # Search and retrieval tools
│   ├── db_utils.py            # Database utilities
│   └── graph_utils.py         # Knowledge graph utilities
├── ingestion/                 # Document processing
│   ├── ingest.py             # Main ingestion pipeline
│   ├── chunker.py            # Semantic chunking
│   ├── embedder.py           # Embedding generation
│   ├── graph_builder.py      # Knowledge graph construction
│   └── medical_entities.py   # Medical entity dictionaries and extraction
├── pdf_extraction/           # PDF to Markdown conversion
│   ├── convert.py            # PDF conversion utilities
│   └── splitter.py           # Document splitting
├── sql/                       # Database schema
│   └── schema.sql            # PostgreSQL schema with pgvector
├── documents/                # Medical guideline documents (ICMR)
├── parsed/                   # Processed/parsed documents
└── tests/                    # Comprehensive test suite
    ├── agent/                # Agent tests
    └── ingestion/            # Ingestion tests
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent --cov=ingestion --cov-report=html

# Run specific test categories
pytest tests/agent/
pytest tests/ingestion/
```

## Medical Guidelines Coverage

The system currently includes ICMR (Indian Council of Medical Research) guidelines for:

### Diabetes Management
- Type 1 Diabetes Mellitus - Comprehensive guidelines covering diagnosis, treatment, complications, and management
- Type 2 Diabetes Mellitus - Evidence-based treatment protocols, medication selection, and monitoring
- Gestational Diabetes Mellitus - Screening, diagnosis, and management during pregnancy
- Standard Treatment Workflows - Step-by-step clinical decision pathways

### Hypertension
- Standard Treatment Guidelines of Hypertension (2016) - Diagnosis, risk stratification, and treatment
- Hypertension in Diabetes - Specialized guidelines for comorbid management (RSSDI)

### Oncology
- Breast Cancer - Consensus documents covering staging, treatment protocols, and management
- Prostate Cancer - Comprehensive guidelines for diagnosis, staging, and treatment
- Colorectal Cancer - Evidence-based treatment protocols and surgical management

## Troubleshooting

### Common Issues

**Database Connection**: Ensure your DATABASE_URL is correct and the database is accessible

```bash
# Test your connection
psql -d "$DATABASE_URL" -c "SELECT 1;"
```

**Neo4j Connection**: Verify your Neo4j instance is running and credentials are correct

```bash
# Check if Neo4j is accessible (adjust URL as needed)
curl -u neo4j:password http://localhost:7474/db/data/
```

**No Results from Agent**: Make sure you've run the ingestion pipeline first

```bash
python -m ingestion.ingest --verbose
```

**LLM API Issues**: Check your API key and provider configuration in `.env`

**Medical Entity Extraction Issues**: Ensure medical dictionaries in `ingestion/medical_entities.py` are comprehensive for your use case

**Slow Ingestion**: Medical entity extraction and knowledge graph building are computationally expensive. Consider:
- Using a faster LLM model for ingestion (`INGESTION_LLM_CHOICE`)
- Processing documents in batches
- Using `--no-semantic` flag for faster chunking (less optimal but faster)

## Medical Disclaimer

**IMPORTANT**: This system is designed as a clinical decision support tool to assist healthcare professionals. It should NOT be used as a substitute for professional medical judgment, diagnosis, or treatment. All clinical recommendations should be:

- Reviewed and validated by qualified healthcare professionals
- Considered in the context of individual patient circumstances
- Used in conjunction with clinical expertise and patient preferences
- Subject to appropriate clinical oversight and quality assurance

The system provides evidence-based recommendations from ICMR guidelines but does not replace the need for:
- Professional medical evaluation
- Clinical judgment
- Patient-specific considerations
- Regulatory compliance
- Medical liability considerations

## Contributing

When adding new medical guidelines or entities:

1. Add medical documents to the `documents/` folder
2. Update medical entity dictionaries in `ingestion/medical_entities.py` if needed
3. Run ingestion to process new documents
4. Test with relevant clinical queries
5. Update documentation as needed

## License

[Add your license information here]

---

Built with ❤️ for healthcare professionals using Pydantic AI, FastAPI, PostgreSQL, Neo4j, and ICMR guidelines.

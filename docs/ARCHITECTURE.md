
# ResearchMind AI — System Architecture

## 1. Architecture Principles

- Modular components with clear responsibilities.
- Separation of API, business logic, and data access.
- Replaceable LLM and embedding providers.
- Traceability from generated answers to source evidence.
- Automated testing at component and integration levels.
- Reproducible experiments and evaluation.

## 2. High-Level Architecture

The application consists of five major subsystems.

### Document Processing

Responsible for:

- PDF validation
- Text extraction
- Text cleaning
- Chunking
- Metadata preservation

### Retrieval Engine

Responsible for:

- Embedding generation
- Vector indexing
- Keyword retrieval
- Hybrid retrieval
- Reranking

### LLM Generation

Responsible for:

- Prompt construction
- Context assembly
- LLM inference
- Structured answer generation

### Evidence Verification

Responsible for:

- Claim extraction
- Citation validation
- Evidence-to-claim mapping
- Unsupported claim detection

### Application Layer

Responsible for:

- FastAPI endpoints
- Request validation
- Application orchestration
- Error handling
- Frontend integration

## 3. Data Flow

PDF Upload
    ↓
Document Validation
    ↓
Text Extraction
    ↓
Text Cleaning
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Index

User Question
    ↓
Query Processing
    ↓
Hybrid Retrieval
    ↓
Reranking
    ↓
Context Assembly
    ↓
LLM Generation
    ↓
Citation Validation
    ↓
Answer with Evidence

## 4. Initial Technology Stack

Language: Python

API Framework: FastAPI

LLM Framework: Hugging Face Transformers

Embedding Framework: Sentence Transformers

Vector Search: FAISS

Model Runtime: Ollama or Transformers

Testing: Pytest

Frontend: React and TypeScript

Deployment: Docker

## 5. Initial Backend Modules

backend/app/

    api/
        HTTP endpoints

    core/
        Configuration and application settings

    schemas/
        Request and response models

    services/
        Document processing and business logic

    main.py
        FastAPI application entry point

backend/tests/

    Unit and integration tests

## 6. Initial Implementation Boundary

The first implementation will contain only:

- PDF ingestion
- Document metadata
- Text extraction
- Input validation
- Automated tests

Vector indexing and LLM generation will be implemented
after ingestion is reliable.

# ResearchMind AI

**An AI-assisted research assistant for semantic search across PDF documents.**

ResearchMind AI is an ongoing learning project focused on exploring how AI can help users find relevant information from documents. It uses text embeddings and semantic similarity to retrieve relevant content from uploaded PDFs.

The project is being developed with AI-assisted guidance while I strengthen my understanding of document processing, embeddings, and information retrieval.

## Project Status

🚧 **In Progress**

The core document retrieval workflow is being developed. Additional features and improvements are planned.

## Features

- PDF document upload and text extraction
- Page-aware document chunking
- Text embeddings using `all-MiniLM-L6-v2`
- Semantic similarity search
- Document filtering and management
- SQLite-based data persistence
- REST API endpoints using FastAPI

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| FastAPI | API development |
| PyMuPDF | PDF text extraction |
| Sentence Transformers | Text embedding generation |
| all-MiniLM-L6-v2 | Semantic embedding model |
| SQLite | Data persistence |

## How It Works

1. A user uploads a PDF document.
2. Text is extracted from the PDF.
3. The extracted text is divided into smaller chunks.
4. The embedding model converts each chunk into a numerical vector.
5. A user submits a search query.
6. The query is converted into an embedding.
7. The system compares the query embedding with stored document embeddings.
8. Relevant document chunks are returned based on similarity.

## Project Structure

```text
ResearchMind-AI/
├── backend/
│   ├── api/
│   │   └── documents.py
│   ├── document_store.py
│   ├── vector_store.py
│   └── researchmind.db
├── tests/
├── README.md
└── requirements.txt
```

*The structure may change as development continues.*

## Getting Started

### Prerequisites

- Python 3.12+
- Git

### Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd ResearchMind-AI
```

Create and activate a virtual environment:

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

### Run the Application

The API entry point may vary depending on the project configuration. If the FastAPI application is exposed as `app` in `backend/main.py`, run:

```powershell
$env:PYTHONPATH="backend"
uvicorn main:app --app-dir backend --reload
```

Then open the API documentation:

```text
http://127.0.0.1:8000/docs
```

*Update the run command if your actual application entry point is different.*

## Learning Objectives

Through this project, I am exploring:

- How text embeddings represent document content
- How semantic search differs from keyword search
- How document chunking supports information retrieval
- How APIs connect document processing and retrieval components
- How to build and improve AI/ML applications through hands-on development

## Future Improvements

- LLM-based answer generation using retrieved document passages
- Source references and page-level citations in generated answers
- Improved retrieval and ranking
- Additional document formats
- A user-friendly interface

## Disclaimer

This is an educational project under active development. AI tools are used as development assistance to explore concepts, troubleshoot issues, and improve the implementation. The project is also part of my ongoing learning in AI/ML and document retrieval.

## Author

**Tanishq R V**

B.Tech Computer Science and Engineering — AI & Machine Learning

SRM Institute of Science and Technology

# Multilingual-Community-RAG
A multilingual Retrieval-Augmented Generation (RAG) system designed to transform community archives, Patrika publications, notices, events, and historical records into an intelligent conversational assistant.

---

## Project Vision

Community information is often distributed across PDFs, scanned documents, notices, advertisements, event announcements, and historical archives.

This project aims to create an AI-powered knowledge assistant capable of:

- Understanding Gujarati, Hindi, and English content
- Searching across Patrika archives
- Answering community-specific questions
- Retrieving notices, events, marriages, and announcements
- Providing conversational responses grounded in source documents

---

## Key Features

### Document Intelligence

- PDF Processing
- OCR Processing
- Multilingual Text Extraction
- Automated Metadata Generation

### Knowledge Retrieval

- Vector Search
- Semantic Retrieval
- Hybrid Search
- Metadata Filtering

### Conversational AI

- Community-specific Question Answering
- Context-aware Responses
- Source Attribution
- Guardrails Against Hallucinations

---

## Architecture

```text
PDFs / Images
        │
        ▼
Document Ingestion Agent
        │
        ▼
Extraction Layer
(PyMuPDF + PaddleOCR)
        │
        ▼
Cleaning Agent
        │
        ▼
Chunking Agent
        │
        ▼
Metadata Agent
        │
        ▼
Embedding Agent (BGE-M3)
        │
        ▼
ChromaDB Vector Store
        │
        ▼
Retriever
        │
        ▼
LLM (Gemini / Groq / Ollama)
        │
        ▼
Community Knowledge Assistant
```

---

## Technology Stack

| Layer | Technology |
|---------|------------|
| Language | Python |
| OCR | PaddleOCR |
| PDF Extraction | PyMuPDF |
| Embeddings | BGE-M3 |
| Vector Database | ChromaDB |
| LLM | Gemini / Groq / Ollama |
| Frontend | Streamlit |
| Backend | FastAPI |

---

## Project Roadmap

### Phase 1

- PDF Extraction
- OCR Pipeline
- Text Cleaning

### Phase 2

- Chunking
- Embeddings
- Vector Storage

### Phase 3

- Retrieval Pipeline
- Question Answering

### Phase 4

- Agentic Workflow
- Automated Ingestion

### Phase 5

- Production Deployment
- Community Integration
---

## Future Enhancements

- Voice Queries
- Image Search
- Community Analytics
- Event Recommendation Engine

---

## Contributors

- Kavya Gada
- Team Members

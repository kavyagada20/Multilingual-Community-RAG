# Multilingual-Community-RAG
Multilingual RAG-based Community Knowledge Assistant for Patrika archives, community notices, events, and historical records.

# Community Knowledge Assistant

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

community-knowledge-assistant/

│
├── data/
│   ├── raw_pdfs/
│   ├── raw_images/
│   ├── extracted_text/
│   ├── processed_chunks/
│   └── metadata/
│
├── chroma_db/
│
├── src/
│
│   ├── agents/
│   │   ├── ingestion_agent.py
│   │   ├── extraction_agent.py
│   │   ├── cleaning_agent.py
│   │   ├── chunking_agent.py
│   │   ├── metadata_agent.py
│   │   ├── embedding_agent.py
│   │   └── retrieval_agent.py
│
│   ├── database/
│   │   └── chroma_manager.py
│
│   ├── ingestion/
│   │   ├── pdf_extractor.py
│   │   ├── ocr_processor.py
│   │   └── text_cleaner.py
│
│   ├── retrieval/
│   │   └── retriever.py
│
│   ├── llm/
│   │   └── gemini_client.py
│
│   ├── prompts/
│   │   ├── qa_prompt.txt
│   │   └── guardrail_prompt.txt
│
│   └── app/
│       └── streamlit_app.py
│
├── tests/
│
├── docs/
│
├── requirements.txt
│
├── .env.example
│
├── .gitignore
│
└── README.md

## Future Enhancements

- Voice Queries
- Image Search
- Community Analytics
- Event Recommendation Engine

---

## Contributors

- Kavya Gada
- Team Members

# Project README

## 1. Introduction

### 1.1. About INCA Solutions

INCA Solutions is a leading technology company providing digital transformation services across Latin America. As part of its innovation strategy, INCA Solutions adopted IBM Watsonx.ai, an enterprise-grade studio for developing AI services and applications.

### 1.2. Business Challenge

With continuous onboarding of new employees and the technical depth of Watsonx.ai, INCA Solutions needed a more efficient training and support mechanism. The goal was to build an intelligent conversational assistant capable of answering questions about Watsonx.ai by leveraging the official documentation.

## 2. Solution Overview

This project implements a proof-of-concept MVP following the Retrieval-Augmented Generation (RAG) architecture. It uses Watsonx.ai for embeddings and inference, and ChromaDB as the vector store. All answers are retrieved strictly from the provided document: **Unleashing the Power of AI with IBM watsonx.ai**.

### 2.1. Architecture

```text
User Question --> FastAPI Endpoint --> Watsonx.ai (Embeddings)
                                      |
                                      v
                           ChromaDB (Vector Retrieval)
                                      |
                                      v (top-k chunks)
                             Watsonx.ai (LLM Inference)
                                      |
                                      v
                              Response to User
```

Components:

* **FastAPI** backend exposing `/ask`
* **pdfplumber** to extract and chunk PDF text
* **Watsonx.ai** for embedding generation and language model inference
* **ChromaDB** containerized vector database (Docker)
* **Streamlit** frontend for interactive UI
* **Docker Compose** to orchestrate backend, frontend, and ChromaDB

## 3. Repository Structure

```
.
├── assets/               # PDF documentation (watsonx.ai guide)
├── docker-compose.yml    # Orchestrates backend + ChromaDB + frontend containers
├──images/
├── source/
│   ├── back-end/         # Backend service (FastAPI)
│   │   ├── app.py               # Endpoints
│   │   ├── index_docs.py        # Indexation of de document
|   |   ├──.example.env          # Environment variable template
│   │   ├── test_ask.py          # Manual test
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── front-end/        # Streamlit frontend application
│       ├── app.py
│       ├── requirements.txt
│       └── Dockerfile
└── README.md             # This document
```

## 4. Installation & Setup

### 4.1. Prerequisites

* Docker & Docker Compose
* Local environment capable of running containers.
* Python 3.11+ (for local index and tests)
* IBM Watsonx.ai credentials (URL, Project ID, API key)

### 4.2. Configure Environment

1. Copy `.env.example` to `.env` in the project root.
2. Fill in your Watsonx.ai credentials:

   ```ini
   WATSONX_URL=
   WATSONX_PROJECT_ID=
   WATSONX_APIKEY=
   ```

### 4.3. Single Command Launch (Docker Compose)

From the project root, build and start all services (backend, frontend, ChromaDB) in detached mode:
(Make sure you have docker running)

```bash
docker-compose up --build
```

This command will launch:

* **chroma** container on port 8000
* **backend** container on port 8080
* **frontend** (Streamlit) container on port 8501

## 5. Usage

### 5.1. Healthcheck (ChromaDB)

```bash
curl -i http://localhost:8000/api/v2/healthcheck
```

### 5.2. Verify Indexed Chunks

```bash
python -c "import chromadb; c=chromadb.HttpClient(host='http://localhost:8000'); col=c.get_collection('watsonx_docs'); print('Chunks:', col.count())"
```

### 5.4. Frontend UI

Open your browser to:

```
http://localhost:8501
```

Interactively type questions and view answers with source citations.

## 6. Technical Decisions & Best Practices

* **Chunk Size**: \~100 words to respect embedding model limits
* **Vector Store**: ChromaDB for lightweight, local Docker deployment
* **Models**: `ibm/granite-embedding-107m-multilingual` for embeddings; IBM Granite instruct for inference
* **Security**: All credentials loaded via environment variables; no secrets in code
* **Containerization**: Docker Compose for multi-service orchestration
* **Standards**: Secure coding per OWASP Quick Reference

## 7. Areas for Improvement

While the current MVP meets the core requirements, there are several areas that can be enhanced in future iterations:

Multi-Document Support: Enable indexing and retrieval across multiple PDFs or document formats (Word, Markdown, etc.) for broader coverage.

Incremental Indexing: Allow dynamic updates to the vector store so new documents or revisions can be ingested without re-indexing the entire corpus.

Caching & Performance: Add a caching layer for frequent queries to reduce API calls to Watsonx.ai and speed up response times.

User Interface Polish: Enhance the Streamlit frontend with richer UI components.


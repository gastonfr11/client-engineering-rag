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
* **Docker Compose** to orchestrate backend + ChromaDB

## 3. Repository Structure

```
.
├── assets/               # PDF documentation (watsonx.ai guide)
├── docker-compose.yml    # Orchestrates backend + ChromaDB containers
├── .env.example          # Environment variable template
├── source/
│   ├── back-end/         # Backend service (FastAPI)
│   │   ├── app.py
│   │   ├── index_docs.py
│   │   ├── test_ask.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── front-end/        # (Optional) Frontend application
└── README.md             # This document
```

## 4. Installation & Setup

### 4.1. Prerequisites

* Docker & Docker Compose
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

### 4.3. Local Python Setup (indexing & testing)

```bash
cd source/back-end
python -m venv venv
# PowerShell:
.
venv\Scripts\Activate.ps1
# CMD:
# venv\Scripts\activate.bat
pip install -r requirements.txt
python index_docs.py   # Extracts, chunks, embeds, and indexes the PDF
```

### 4.4. Docker Setup (runtime)

From the project root:

```bash
docker-compose up --build -d
```

This launches:

* **chroma** container on port 8000
* **backend** container on port 8080

## 5. Usage

### 5.1. Healthcheck (ChromaDB)

```bash
# Using curl.exe
curl.exe -i http://localhost:8000/api/v2/healthcheck
# Or PowerShell:
Invoke-RestMethod http://localhost:8000/api/v2/healthcheck
```

### 5.2. Verify Indexed Chunks

```bash
python -c "import chromadb; c=chromadb.HttpClient(host='http://localhost:8000'); col=c.get_collection('watsonx_docs'); print('Chunks:', col.count())"
```

### 5.3. Ask a Question

```bash
# Using PowerShell here-string + Invoke-RestMethod
echo @'
{'"question"':'"What is Watsonx.ai?"','"k"':3}
'@ > body.json
Invoke-RestMethod -Uri http://localhost:8080/ask -Method POST -Body (Get-Content body.json -Raw) -ContentType 'application/json'
```

Or run the Python test script:

```bash
python test_ask.py
```

## 6. Technical Decisions & Best Practices

* **Chunk Size**: \~100 words to respect embedding model limits
* **Vector Store**: ChromaDB for lightweight, local Docker deployment
* **Models**: `ibm/granite-embedding-107m-multilingual` for embeddings; an IBM Granite instruct model for inference
* **Security**: All credentials loaded via environment variables; no secrets in code
* **Containerization**: Docker Compose for multi-service orchestration
* **Standards**: Secure coding per OWASP Quick Reference

## 7. (Optional) Frontend

A minimal UI can be built using Streamlit or React in `source/front-end/`. Questions must be in English, and the UI will display the answer and source chunks.

## 8. Delivery

* Submit project `.zip` (without `venv/` or `.env`) via email.
* Include **README.md** and all source under `source/`.
* Provide a \~10-minute demo video in MP4, showcasing:

  1. Architecture overview
  2. Indexing flow (`index_docs.py`)
  3. Running services (`docker-compose up`)
  4. Live queries and responses

*Prepared for INCA Solutions – RAG Conversational Assistant Challenge*

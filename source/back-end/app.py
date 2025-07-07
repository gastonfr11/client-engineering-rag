import os
import chromadb

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from pathlib import Path

#carga variables de entorno
load_dotenv()
WATSONX_URL     = os.getenv("WATSONX_URL")
WATSONX_APIKEY  = os.getenv("WATSONX_APIKEY")
WATSONX_PROJECT = os.getenv("WATSONX_PROJECT_ID")

#conexión a ChromaDB
CHROMA_HOST = os.getenv("CHROMA_HOST", "http://localhost:8000")
client     = chromadb.HttpClient(host=CHROMA_HOST)

try:
    collection = client.get_collection(name="watsonx_docs")
except chromadb.errors.NotFoundError:
    collection = client.create_collection(name="watsonx_docs")

#cliente de embeddings
embedder = WatsonxEmbeddings(
    url=WATSONX_URL,
    apikey=WATSONX_APIKEY,
    project_id=WATSONX_PROJECT,
    model_id="ibm/granite-embedding-107m-multilingual"
)

#cliente de LLM para generación de texto
llm = WatsonxLLM(
    url=WATSONX_URL,
    apikey=WATSONX_APIKEY,
    project_id=WATSONX_PROJECT,
    model_id="ibm/granite-3-2b-instruct"       
)

app = FastAPI()

class Query(BaseModel):
    question: str
    k: int = 3   

@app.post("/ask")
def ask(q: Query):
    # Embedding de la pregunta
    q_emb = embedder.embed_query(q.question)

    # Búsqueda semántica (solo traigo metadatos)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=q.k,
        include=["documents", "metadatas"]
    )
    print(">>> RAW METADATAS:", results["metadatas"])
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    if not docs:
        raise HTTPException(404, "No documents found.")

    # Construyo un prompt
    context = "\n\n---\n\n".join(docs)
    prompt = f"""
You are an AI assistant. Using ONLY the context below, write a detailed, well-structured answer in 2–3 paragraphs.
Then list your sources in a numbered list, giving only page numbers and section titles.

--- CONTEXT BEGIN ---
{context}
--- CONTEXT END ---

QUESTION: {q.question}
"""

    # Generación
    response = llm.generate([prompt])
    answer = response.generations[0][0].text.strip()

    # Formateo de fuentes
    sources = []
    for m in metas:
        page = m.get("page", "unknown")
        section = m.get("section")
        if section:
            sources.append(f"Page {page}, Section “{section}”")
        else:
            sources.append(f"Page {page}")
    
    return {"answer": answer, "sources": sources}

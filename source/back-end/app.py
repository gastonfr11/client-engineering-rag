import os
import chromadb
import numpy as np

from fastapi import FastAPI, HTTPException
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames
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

app = FastAPI()

@app.on_event("startup")
def startup_event():
    import index_docs  

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


parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 512,    
    GenTextParamsMetaNames.MIN_NEW_TOKENS: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.2,       
}


llm = WatsonxLLM(
    url=WATSONX_URL,
    apikey=WATSONX_APIKEY,
    project_id=WATSONX_PROJECT,
    model_id="ibm/granite-3-2b-instruct",
    params=parameters,  
)



class Query(BaseModel):
    question: str
    k: int = 3   

def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

@app.post("/ask")
def ask(q: Query):
    # Embedding de la pregunta
    q_emb = embedder.embed_query(q.question)

    # Búsqueda semántica (solo traigo metadatos)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=max(q.k, 10),
        include=["documents", "metadatas"]
    )
    print(">>> RAW METADATAS:", results["metadatas"])
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    if not docs:
        raise HTTPException(404, "No documents found.")
    
     # Re-embedea cada documento
    doc_embs = embedder.embed_documents(docs)

    # Calcula similitudes
    scores = [cos_sim(q_emb, d_emb) for d_emb in doc_embs]

    # Reordena por score descendente
    ranked = sorted(zip(scores, docs, metas), key=lambda x: x[0], reverse=True)

    # Toma los top k
    top_k = ranked[: q.k ]
    _, docs, metas = zip(*top_k)

    for i, (score, doc, meta) in enumerate(ranked, 1):
        print(f"[Rerank] #{i} score={score:.3f}, page={meta.get('page')}")

    # Construyo un prompt
    context = "\n\n---\n\n".join(docs)
    prompt = f"""
You are an AI assistant. Using ONLY the context below, write a detailed, well-structured answer in 2–3 paragraphs.

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

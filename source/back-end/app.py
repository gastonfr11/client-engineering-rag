from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import chromadb
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from pathlib import Path

#carga variables de entorno
load_dotenv()
WATSONX_URL     = os.getenv("WATSONX_URL")
WATSONX_APIKEY  = os.getenv("WATSONX_APIKEY")
WATSONX_PROJECT = os.getenv("WATSONX_PROJECT_ID")

#conexión a ChromaDB
client = chromadb.HttpClient(host="http://chroma:8000")
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
    q_emb = embedder.embed_query(q.question)


    results = collection.query(
        query_embeddings=[q_emb],
        n_results=q.k,
        include=["documents", "metadatas"]
    )
    docs = results["documents"][0]        
    metas = results["metadatas"][0]       

    if not docs:
        raise HTTPException(status_code=404, detail="No se encontraron documentos.")


    context = "\n\n---\n\n".join(docs)
    prompt  = f"Con la siguiente información de contexto:\n\n{context}\n\nResponde la pregunta: {q.question}"

    response = llm.generate([prompt])  
    answer = response.generations[0][0].text.strip()

    return {"answer": answer, "sources": docs}

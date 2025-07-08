import os                                       #os se usa para leer variables de entorno
import pdfplumber                               #librería usada para abrir y extraer texto de pdf
import chromadb                                 #usado para comunicarse con ChromaDB

from dotenv import load_dotenv                  #se encarga de cargar las variables del .env al entorno
from pathlib import Path                        #para manejar rutas
from langchain_ibm import WatsonxEmbeddings     #usado para pedir embeddings a Watsonx.ai 

#load se encarga de buscar un archivo .env en la carpeta actual, cargando así las claves
load_dotenv()

#obtenemos las credenciales del .env
WATSONX_URL     = os.getenv("WATSONX_URL")
WATSONX_APIKEY  = os.getenv("WATSONX_APIKEY")
WATSONX_PROJECT = os.getenv("WATSONX_PROJECT_ID")

#el objeto embedder se encarga de mandar texto a Watsonx.ai
embedder = WatsonxEmbeddings(
    url=WATSONX_URL,
    apikey=WATSONX_APIKEY,        
    project_id=WATSONX_PROJECT,  
    model_id="ibm/granite-embedding-107m-multilingual"
)

#client se concecta a chromaDB
CHROMA_HOST = os.getenv("CHROMA_HOST", "http://localhost:8000")
client = chromadb.HttpClient(host=CHROMA_HOST)

#queremos obtener la colección watsonx_docs. Si existe la obtenemos, sino la creamos.
try:
    collection = client.get_collection(name="watsonx_docs")
    print("Colection 'watsonx_docs' recovered.")
except Exception:
    collection = client.create_collection(name="watsonx_docs")
    print("Colection 'watsonx_docs' created.")

#LOCALIZAR PDF (para poder acceder de forma dinámica)

#sube dos carpetas para ir a la raíz
BASE_DIR   = Path(__file__).parent

#assets_dir es la carpeta assets que está en la raíz. La idea es listar todos los PDF, idealmente tiene que haber uno solo.
assets_dir = BASE_DIR.parent / "assets"
pdf_files = list(assets_dir.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No encontré ningún PDF en {assets_dir}")
if len(pdf_files) > 1:
    print("There is more than 1 PDF in assets, using the first one found")
pdf_file = pdf_files[0]
print(f"Using PDF: {pdf_file.name}")

# Parámetro de tamaño
max_words = 100

# 1) Generar lista de tuplas (page_num, texto_chunk)
chunks_with_pages = []
with pdfplumber.open(pdf_file) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        words = text.split()
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i : i + max_words])
            chunks_with_pages.append((page_num, chunk))

print(f"Generated {len(chunks_with_pages)} chunks of ~{max_words} words.")

# 2) Pedir embeddings solo del texto
texts = [chunk for _, chunk in chunks_with_pages]
embeddings = embedder.embed_documents(texts)

# 3) Subir cada chunk junto con su página al metadata
for idx, ((page_num, chunk), emb) in enumerate(zip(chunks_with_pages, embeddings)):
    collection.add(
        ids=[f"chunk_{idx}"],
        embeddings=[emb],
        documents=[chunk],
        metadatas=[{"page": page_num, "length": len(chunk.split())}],
    )

print("Indexaction Completed.")



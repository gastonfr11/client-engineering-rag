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
client = chromadb.HttpClient(host="http://localhost:8000")

#queremos obtener la colección watsonx_docs. Si existe la obtenemos, sino la creamos.
try:
    collection = client.get_collection(name="watsonx_docs")
    print("Colection 'watsonx_docs' recovered.")
except Exception:
    collection = client.create_collection(name="watsonx_docs")
    print("Colection 'watsonx_docs' created.")

#LOCALIZAR PDF (para poder acceder de forma dinámica)

#sube dos carpetas para ir a la raíz
REPO_ROOT = Path(__file__).parents[2]

#assets_dir es la carpeta assets que está en la raíz. La idea es listar todos los PDF, idealmente tiene que haber uno solo.
assets_dir = REPO_ROOT / "assets"
pdf_files = list(assets_dir.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No encontré ningún PDF en {assets_dir}")
if len(pdf_files) > 1:
    print("There is more than 1 PDF in assets, using the first one found")
pdf_file = pdf_files[0]
print(f"Using PDF: {pdf_file.name}")

#abrimos el pdf encontrado y extraemos el texto, teniendo en full text un único string con todo el texto
with pdfplumber.open(pdf_file) as pdf:
    full_text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)

#CHUNKING

#separamos en una lista de palabras, con un máximo de 100 para no pasarnos
words = full_text.split()
max_words = 100
chunks = [
    " ".join(words[i : i + max_words])
    for i in range(0, len(words), max_words)
]
print(f"Generated {len(chunks)} chunks of ~{max_words} words.")

#enviamos a batch todos los fragmentos y recibimos una lista de vectores, uno por chunk.
embeddings = embedder.embed_documents(chunks)
for idx, (text, emb) in enumerate(zip(chunks, embeddings)):
    collection.add(
        ids=[f"chunk_{idx}"],
        embeddings=[emb],
        documents=[text],
        metadatas=[{"length": len(text.split())}],
    )
print(f"Generated {len(chunks)} chunks of ~{max_words} words.")



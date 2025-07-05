## Proyecto RAG con IBM watsonx.ai

Este repositorio contiene un prototipo de asistente conversacional RAG (Retrieval-Augmented Generation) basado en la documentación oficial de IBM watsonx.ai.

### Estructura del repositorio

```
client-engineering-rag/
├── assets/                      # Documentación fuente (PDF, diagramas)
├── chroma_db/                   # Volumen para ChromaDB (no versionado)
├── source/
│   └── back-end/
│       ├── app.py               # FastAPI: endpoint /ask
│       ├── index_docs.py        # Script de indexación con embeddings
│       ├── Dockerfile           # Imagen del backend
│       ├── requirements.txt     # Dependencias Python
│       └── .env.example         # Variables de entorno de ejemplo
├── docker-compose.yml           # Orquestación: ChromaDB + Backend
└── README.md
```

### Requisitos previos

* Docker & Docker Compose
* Credenciales de IBM watsonx.ai:

  * `WATSONX_URL`
  * `WATSONX_PROJECT_ID`
  * `WATSONX_APIKEY`

### Configuración

1. **Crea tu `.env`** en `source/back-end/` o en la raíz:

   ```shell
   cp source/back-end/.env.example .env
   # Edita .env con tus credenciales
   ```
2. **Modifica** `Docker Compose` para apuntar al `.env`:

   ```yaml
   environment:
     - WATSONX_URL=${WATSONX_URL}
     - WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID}
     - WATSONX_APIKEY=${WATSONX_APIKEY}
   ```

### Levantar con Docker

```bash
cd client-engineering-rag
docker-compose up --build -d
```

* ChromaDB estará en `http://localhost:8000`
* Backend RAG en `http://localhost:8080`

### Uso

Para hacer preguntas al asistente:

```bash
curl -X POST http://localhost:8080/ask \
     -H "Content-Type: application/json" \
     -d '{"question":"¿Qué es Watsonx.ai?","k":3}'
```

### Flujo de trabajo

1. **Indexación**: `index_docs.py` extrae el PDF, chunkea, genera embeddings y los guarda en ChromaDB.
2. **Consulta**: el endpoint `/ask` genera el embedding de la pregunta, recupera los chunks más similares, y llama al LLM para generar la respuesta.
3. **Containerización**: todo el servicio está orquestado con Docker Compose.

### Entrega

* Comprimir el repositorio (excluyendo `chroma_db`).
* Incluir instrucciones de uso (este README).
* Grabar video demo explicando la arquitectura y demo de uso en Docker.

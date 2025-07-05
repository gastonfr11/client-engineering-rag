# 1. Imagen base con Python
FROM python:3.10-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código fuente
COPY . .

# 5. Exponer el puerto de FastAPI
EXPOSE 8080

# 6. Comando por defecto para arrancar Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

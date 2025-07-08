#Imagen base con Python
FROM python:3.10-slim

#Directorio de trabajo
WORKDIR /app

#Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copiar el código fuente
COPY . .

#Exponer el puerto de FastAPI
EXPOSE 8080

#Comando por defecto para arrancar Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

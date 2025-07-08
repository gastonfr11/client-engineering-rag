# front-end/Dockerfile
FROM python:3.10-slim
WORKDIR /app

# Copia las dependencias y las instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia la app de Streamlit
COPY app.py .

# Expone el puerto por defecto de Streamlit
EXPOSE 8501

# Comando para arrancar
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

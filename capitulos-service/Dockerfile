# Usa una imagen base ligera de Python
FROM python:3.10-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia los requirements y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Exponemos el puerto 8000 para FastAPI
EXPOSE 8000

# Comando para arrancar la app con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# tests/Dockerfile
FROM python:3.10-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos de testing
COPY requirements_test.txt .

# Instala las dependencias de testing
RUN pip install --no-cache-dir -r requirements_test.txt

# Copia la carpeta de pruebas al contenedor
COPY . .

# Comando para ejecutar pytest. Este comando se ejecutará cuando levantes el contenedor.
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"]

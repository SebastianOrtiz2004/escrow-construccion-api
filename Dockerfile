# Usa una imagen base oficial de Python ligera
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para compilar paquetes (como psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de dependencias
COPY requirements.txt .

# Instala las dependencias de Python de forma limpia, sin caché
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto al directorio de trabajo
COPY . .

# Expone el puerto en el que correrá FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación usando uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

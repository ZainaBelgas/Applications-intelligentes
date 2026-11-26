# Image de MaintAI : le code et ses bibliothèques, sans les données ni le modèle.
# Construire : docker build -t maintai:0.4.0 .

# 1. L'image de départ
FROM python:3.11-slim

# 2. Le dossier de travail
WORKDIR /app

# 3. Les bibliothèques AVANT le code (cette couche reste en cache)
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# 4. Le code
COPY maintai ./maintai
COPY ui ./ui

# 5. Les chemins du modèle et des données
ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

# 6. Le port et la commande de démarrage
EXPOSE 8000
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
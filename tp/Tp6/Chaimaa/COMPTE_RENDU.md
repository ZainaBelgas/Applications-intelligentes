Compte rendu · TP6 — Conteneuriser MaintAI avec Docker et Docker Compose
Membres : CHAIMAA EZZERAG Date : 26/11/2026 Heure : 11:30

1. Mise en place
Vérification de Docker :

Hello from Docker!
Docker Client : 29.1.2
Docker Server Engine : 29.1.2
Résultat de python -m pytest avant les modifications :

5 failed, 33 passed, 4 warnings in 63.68s (0:01:03)
2. Image et conteneur
Quelle différence entre une image et un conteneur ?
Une image contient le système de base, les bibliothèques et le code de l’application. Un conteneur est une instance créée à partir de cette image. Plusieurs conteneurs peuvent utiliser la même image.

Pourquoi copier requirements-docker.txt avant le code ?
Docker peut réutiliser la couche d’installation des bibliothèques lorsque seul le code change. Cela accélère le build suivant.

Pourquoi utiliser scikit-learn==1.8.0 ?
Cette version correspond à celle utilisée pour entraîner et sauvegarder le modèle. La fixer permet de reproduire l’environnement et réduit le risque d’incompatibilité au chargement.

Pourquoi exclure mlflow, dvc et pytest ?
MLflow sert au suivi des entraînements, DVC au versionnement des données et pytest aux tests. L’image de service embarque les dépendances nécessaires à l’API et à l’interface.

3. Sprint 1 — Le Dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
Build	Durée	Taille affichée par docker images
Premier build	261,28 s (4 min 21 s)	À compléter si la taille a été relevée
Après modification de maintai/predict.py	4,92 s	1,13 GB d’espace disque et 259 MB de contenu
CACHED signifie que Docker réutilise le résultat d’une étape précédente. L’étape RUN pip install est restée en cache, car le fichier requirements-docker.txt était identique. Les étapes de copie du code ont été réexécutées.

4. Sprint 1 — Lancer un conteneur
Commande exécutée dans PowerShell :

docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "${PWD}\models:/app/models:ro" maintai:0.4.0
Essai	Réponse observée
GET /health avec le modèle monté	status: ok, model_loaded: True
POST /v1/predict sans clé	401 Unauthorized
POST /v1/predict avec la clé	200 OK, failure_probability: 0.9553, alert: true, threshold: 0.3
Piège 1 — Sans le montage du modèle

/health répond avec status: ok et model_loaded: False. Avec une clé valide, /v1/predict renvoie 503 Service Unavailable avec le message « Modèle non chargé ». L’API peut démarrer, mais elle a besoin des fichiers du modèle pour prédire.

Piège 2 — Écoute sur 127.0.0.1 dans le conteneur

docker logs maintai-local-test affiche Uvicorn running on http://127.0.0.1:8000. Depuis Windows, l’appel à http://localhost:8002/health échoue avec The connection was closed unexpectedly. Uvicorn écoute uniquement sur la boucle locale du conteneur. L’écoute sur 0.0.0.0 permet à Docker de lui transmettre les requêtes du port publié.

5. Sprint 2 — Docker Compose
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command:
      - python
      - -m
      - streamlit
      - run
      - ui/app.py
      - --server.address=0.0.0.0
      - --server.port=8501
      - --server.headless=true
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
Résumé de la sortie de docker compose ps :

Conteneur	Service	État	Port publié
tp6-api-1	api	Up	8000:8000
tp6-ui-1	ui	Up	8501:8501
La barre latérale de Streamlit affiche http://api:8000. Cette URL vient de la variable MAINTAI_API_URL, définie dans compose.yaml et lue par ui/app.py.

Pour un relevé de 72 °C, 6 mm/s de vibration, 85 % de charge et 15 000 heures de fonctionnement, l’interface a affiché 95 % de probabilité de panne et une alerte, car la valeur dépasse le seuil de 30 %.

Résultats des appels à /health depuis le conteneur ui :

http://api:8000/health → {"status":"ok","model_loaded":true}
http://localhost:8000/health → httpx.ConnectError: [Errno 111] Connection refused
Dans le conteneur ui, localhost désigne le conteneur Streamlit lui-même. api est le nom du service FastAPI sur le réseau Compose. Depuis le PC, localhost:8000 fonctionne parce que Docker publie le port de l’API.

Résultat final de python -m pytest :

38 passed, 4 warnings in 78.54s (0:01:18)
6. Décision — ADR 005
Voir docs/adr/005-image-docker.md.

Le modèle est monté en lecture seule au démarrage du conteneur. Il peut ainsi être mis à jour sans reconstruire l’image Docker.

7. Questions de compréhension
Qu’est-ce qui entre dans l’image et qu’est-ce qui arrive au lancement ?
L’image contient Python, les bibliothèques installées avec pip et le code copié par le Dockerfile. Au démarrage, le modèle et les données sont fournis par des montages en lecture seule. La clé arrive via --env-file .env ou env_file: .env dans Compose.

Pourquoi la clé API est-elle exclue de l’image ?
Une image peut être partagée. Y inclure la clé exposerait le secret aux personnes qui y ont accès. Charger la clé au démarrage permet aussi de la changer sans reconstruire l’image.

Qu’est-ce que Docker ajoute à la livraison du modèle ?
Docker fournit l’environnement d’exécution de l’application, avec le système de base, Python et les bibliothèques. Compose décrit aussi comment lancer et connecter l’API et l’interface.

8. Rendu Git
Lien de la pull request : à compléter après ouverture.
Tag tp6 sur GitHub : à vérifier après la fusion et la publication du tag.
.env, models/ ou data/*.csv visibles dans git status avant le commit : à vérifier avant le commit.
9. Ce qui reste flou
À compléter avec une question personnelle, ou écrire « Aucun point bloquant » si c’est le cas.
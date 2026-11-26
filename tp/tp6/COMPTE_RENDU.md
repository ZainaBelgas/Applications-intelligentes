# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** …  ·  **Membres :** Amira Zahr, …  ·  **Date :** 26/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Hello from Docker!

Client:
 Version:           29.9.3
 API version:       1.56
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.99.0 (245822)
 Engine:
  Version:          29.9.3
  API version:      1.56 (minimum version 1.40)
  OS/Arch:          linux/amd64
```

Dernière ligne de `python -m pytest` après la mise en place :

```
5 failed, 33 passed, 6 warnings in 32.36s
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   Une image est le résultat figé et nommé du Dockerfile (système, Python, bibliothèques, code). Un conteneur est une exécution isolée de cette image, avec ses fichiers et son réseau. Une image peut lancer plusieurs conteneurs.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Docker réutilise les couches en cache jusqu'à la première qui change. Les bibliothèques changent rarement et sont longues à installer ; le code change souvent. Une modification du code ne relance donc pas pip install.
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Le modèle a été écrit avec scikit-learn 1.8.0. Un fichier joblib chargé avec une autre version peut échouer ou se comporter différemment. La version figée rend aussi l'image reproductible.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   L'image sert à utiliser le modèle (API et interface), pas à l'entraîner ni à le tester. Elle reste plus légère, plus rapide à construire et contient moins de composants à maintenir.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
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
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | … | 1.13GB |
| après une modification de `maintai/predict.py` | … | 1.13GB |

Que signifie `CACHED` dans le journal du second build ?

Docker n'a pas réexécuté l'instruction : elle et les précédentes n'ont pas changé, il réutilise la couche déjà construite.

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "%cd%\models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | 200, `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | 401, « Clé API absente ou invalide » |
| `POST /v1/predict` avec la clé | 200, `failure_probability: 0.9475`, `alert: true`, `threshold: 0.3` |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

`/health` répond 200 avec `model_loaded: false`. `/v1/predict` avec la clé répond 503 « Modèle non chargé » (401 sans clé). Le modèle n'est pas dans l'image : sans volume, `/app/models` ne le contient pas.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

`docker logs test` montre qu'Uvicorn tourne sur http://127.0.0.1:8000, mais http://localhost:8002/health ne répond pas (`ERR_EMPTY_RESPONSE`). Dans un conteneur, 127.0.0.1 désigne ce conteneur seulement : le trafic publié par -p n'arrive pas à l'API. Il faut --host 0.0.0.0.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

```yaml
# MaintAI en deux conteneurs : l'API et l'interface Streamlit.
# Lancer : docker compose up --build      Arrêter : docker compose down

services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env                     # MAINTAI_API_KEY, comme au TP2
    ports:
      - "8000:8000"                    # PC:conteneur
    volumes:
      - ./models:/app/models:ro        # le modèle du PC, en lecture seule

  ui:
    image: maintai:0.4.0               # la même image que l'API
    command: ["python", "-m", "streamlit", "run", "ui/app.py",
              "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
    environment:
      MAINTAI_API_URL: http://api:8000  # le nom du service, pas localhost
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro            # les données pour l'onglet « Données »
    depends_on:
      - api
```

Sortie de `docker compose ps` :

```
NAME        IMAGE           COMMAND                  SERVICE   CREATED         STATUS         PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       3 minutes ago   Up 3 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        3 minutes ago   Up 3 minutes   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

http://api:8000. Elle vient de la variable MAINTAI_API_URL définie dans compose.yaml et lue par os.getenv dans ui/app.py.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
Avec api :
{"status":"ok","model_loaded":true}

Avec localhost :
httpx.ConnectError: [Errno 111] Connection refused
```

Avec api, on obtient la réponse de /health. Avec localhost, la connexion échoue : depuis le conteneur ui, localhost désigne ui lui-même, où rien n'écoute sur le port 8000. Dans le navigateur, localhost désigne le PC, et le port 8000 y est publié vers le conteneur api.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
38 passed, 6 warnings in 49.37s
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

Le modèle arrive par un volume en lecture seule, pour en changer sans reconstruire l'image ; en contrepartie, il faut le fournir au lancement. Les données et la clé restent aussi hors de l'image.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   Dans l'image : Linux slim, Python 3.11, les bibliothèques figées, maintai/ et ui/. Au lancement : le modèle (volume ./models), les données (volume ./data), la clé (--env-file .env ou env_file) et l'URL de l'API pour l'interface (environment: MAINTAI_API_URL).
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   L'image peut être partagée et toute personne qui l'obtient pourrait lire la clé dans ses couches ou sa configuration. De plus, la clé doit pouvoir changer sans reconstruire.
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   Au code, au modèle et aux versions des bibliothèques, Docker ajoute l'environnement d'exécution : le système, la version de Python, les bibliothèques installées et la commande de démarrage, réunis dans une image.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp6` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? oui / non

## 9. Ce qui reste flou

…

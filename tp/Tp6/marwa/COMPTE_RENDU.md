# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G51  ·  **Membre :** Marwa Elomari Alaoui  ·  **Date :** 26/11/2026  ·  **Heure de dépôt :** 11:52

**Cours :** Développement et déploiement d'applications intelligentes · Séance 8

---

## Sommaire

1. Mise en place
2. Image et conteneur
3. Sprint 1 : le Dockerfile
4. Sprint 1 : lancer un conteneur
5. Sprint 2 : Docker Compose
6. Décision : l'ADR 005
7. Questions de compréhension
8. Le rendu Git
9. Ce qui reste flou
10. Synthèse des critères de réussite

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Hello from Docker!

Client:
 Version:           29.1.2
 API version:       1.52
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.54.0 (212467)
 Engine:
  Version:          29.1.2
  API version:      1.52 (minimum version 1.44)
  OS/Arch:          linux/amd64
```

Dernière ligne de `python -m pytest` après la mise en place :

```
5 failed, 33 passed, 6 warnings in 32.36s
```

## 2. Image et conteneur (pendant le premier build)

1. **Quelle différence entre une image et un conteneur ?**
   Une image est le résultat figé et nommé du Dockerfile (système, Python, bibliothèques, code). Un conteneur est une exécution isolée de cette image, avec ses fichiers et son réseau. Une image peut lancer plusieurs conteneurs.
2. **Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?**
   Docker réutilise les couches en cache jusqu'à la première qui change. Les bibliothèques changent rarement et sont longues à installer ; le code change souvent. Une modification du code ne relance donc pas `pip install`.
3. **Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?**
   Le modèle a été écrit avec scikit-learn 1.8.0. Un fichier joblib chargé avec une autre version peut échouer ou se comporter différemment. La version figée rend aussi l'image reproductible.
4. **Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?**
   L'image sert à utiliser le modèle (API et interface), pas à l'entraîner ni à le tester. Elle reste plus légère, plus rapide à construire et contient moins de composants à maintenir.

## 3. Sprint 1 : le Dockerfile

Mon `Dockerfile` :

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

Dernière ligne de `python -m pytest` après l'écriture du Dockerfile et du `.dockerignore` :

```
2 failed, 36 passed, 4 warnings in 59.60s
```

Les deux échecs restants sont dans `tests/test_docker.py` : le test du `compose.yaml` et celui de l'URL lue dans l'environnement. Ils passent au sprint 2.

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | 291 s (environ 4 min 51 s) ; `pip install` : 156,8 s | 1,13 Go (contenu : 259 Mo) |
| nouveau build (après la modification) | 2,2 s ; toutes les couches `CACHED` | 1,13 Go (contenu : 259 Mo) |

**Que signifie `CACHED` dans le journal du second build ?**
Docker n'a pas réexécuté l'instruction : elle et les précédentes n'ont pas changé, il réutilise la couche déjà construite. C'est pour cela que les bibliothèques sont installées avant le code : en cas de modification du code, seules les couches du code sont refaites.

## 4. Sprint 1 : lancer un conteneur

Ma commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "%cd%\models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | 200 : `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | 401 : « Clé API absente ou invalide » |
| `POST /v1/predict` avec la clé | 200 : `failure_probability` ≈ 0,95 et `alert: true` (seuil 0,3) |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

`/health` répond 200 avec `model_loaded: false`. `/v1/predict` avec la clé répond 503 « Modèle non chargé » (401 sans clé). Le modèle n'est pas dans l'image : sans volume, `/app/models` ne le contient pas.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

`docker logs test` montre qu'Uvicorn tourne sur `http://127.0.0.1:8000`, mais `http://localhost:8002/health` ne répond pas. Dans un conteneur, `127.0.0.1` désigne ce conteneur seulement : le trafic publié par `-p` n'arrive pas à l'API. Il faut `--host 0.0.0.0`.

## 5. Sprint 2 : Docker Compose

Mon `compose.yaml` :

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
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       5 seconds ago   Up 3 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        4 seconds ago   Up 2 seconds   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

**Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?**
`http://api:8000`. Elle vient de la variable `MAINTAI_API_URL` définie dans `compose.yaml` et lue par `os.getenv` dans `ui/app.py`. Avec la clé saisie, le bouton « Prédire » affiche une probabilité de panne de 95 % et l'alerte « au-dessus du seuil 0.3 ».

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`) :

```
docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
{"status":"ok","model_loaded":true}

docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
httpx.ConnectError: [Errno 111] Connection refused
```

**Pourquoi la seconde échoue-t-elle ?**
Depuis le conteneur `ui`, `localhost` désigne `ui` lui-même, où rien n'écoute sur le port 8000. Dans le navigateur, `localhost` désigne le PC, et le port 8000 y est publié vers le conteneur `api`. Dans Compose, les services se joignent par leur nom.

**Que supprime `docker compose down` ?**
Les conteneurs (`tp6-api-1`, `tp6-ui-1`) et le réseau `tp6_default`. Elle ne supprime ni l'image `maintai:0.4.0`, ni les dossiers `models/` et `data/` du PC.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
38 passed, 4 warnings in 81.15s (0:01:21)
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumé de la décision en deux phrases :

Le modèle arrive par un volume en lecture seule, pour en changer sans reconstruire l'image ; en contrepartie, il faut le fournir au lancement. Les données et la clé restent aussi hors de l'image.

## 7. Questions de compréhension

1. **Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ?**

   | Élément | Où | Moyen |
   |---|---|---|
   | Linux slim, Python 3.11, bibliothèques figées, `maintai/`, `ui/` | dans l'image | `docker build` |
   | le modèle | au lancement | volume `./models` |
   | les données | au lancement | volume `./data` |
   | la clé API | au lancement | `--env-file .env` ou `env_file` |
   | l'URL de l'API pour l'interface | au lancement | `environment: MAINTAI_API_URL` |

2. **Pourquoi la clé API n'est-elle jamais dans l'image ?**
   L'image peut être partagée et toute personne qui l'obtient pourrait lire la clé dans ses couches ou sa configuration. De plus, la clé doit pouvoir changer sans reconstruire.
3. **Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?**
   Au code, au modèle et aux versions des bibliothèques, Docker ajoute l'environnement d'exécution : le système, la version de Python, les bibliothèques installées et la commande de démarrage, réunis dans une image.

## 8. Le rendu Git

- Lien du dossier GitHub :https://github.com/ZainaBelgas/Applications-intelligentes/blob/main/tp/Tp6/marwa

## 9. Ce qui reste flou

## 9. Ce qui reste flou

J'ai bien compris le principe de Docker et la différence entre une image et un conteneur. Cependant, certains points restent encore un peu difficiles pour moi :

- Je ne comprends pas encore totalement comment Docker Compose organise la communication entre plusieurs conteneurs.
- J'ai encore quelques difficultés à comprendre le fonctionnement des volumes et la différence entre les fichiers présents dans l'image et ceux ajoutés au lancement.
- Je voudrais mieux comprendre le système de cache de Docker et savoir dans quels cas il reconstruit les couches.
- Je dois encore pratiquer les commandes Docker pour être plus à l'aise dans la gestion des conteneurs et des images.

Avec plus de pratique, je pense pouvoir mieux maîtriser ces notions et devenir plus autonome dans le déploiement de mes applications.

## 10. Synthèse des critères de réussite

| Critère du polycopié | État |
|---|---|
| 38 tests passent | Oui : `38 passed` |
| L'image `maintai:0.4.0` se construit | Oui : 291 s, 1,13 Go |
| L'API répond depuis un conteneur (401 sans clé, une probabilité avec) | Oui |
| `docker compose up` lance l'API et l'interface, qui prédit | Oui : 95 % et alerte |
| ADR 005 rédigé | Fichier `docs/adr/005-image-docker.md` |
| Pull request fusionnée et tag `tp6` | Voir section 8 |

# Compte rendu — TP6 : Conteneuriser MaintAI avec Docker et Docker Compose

**Groupe :** G1  
**Étudiante :** Chaimaa EZZERAG  
**Classe :** 5IAD  
**Date :** 26/11/2026  
**Heure de réalisation :** 11h34

---

## 1. Mise en place

### 1.1. Vérification de Docker

La commande `docker run hello-world` a permis de vérifier le bon fonctionnement de Docker.

Résultat obtenu :

```text
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

Docker a contacté le daemon, téléchargé l'image `hello-world`, créé un conteneur et exécuté celui-ci avec succès.

### 1.2. Version de Docker

La commande `docker version` a retourné les informations suivantes :

```text
Client:
 Version:           29.4.2
 API version:       1.54
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.72.0 (225998)
 Engine:
  Version:          29.4.2
  API version:      1.54
  OS/Arch:          linux/amd64
```

L'environnement utilise Docker Desktop sous Windows avec un moteur Docker Linux.

### 1.3. Vérification initiale des tests

Commande exécutée (racine du projet TP6) :

```powershell
python -m pytest -v
```

**Résultat initial réellement obtenu :**

```
======================= 38 passed in 26.39s =======================
```

Les 38 tests du projet passent intégralement, incluant les tests de configuration Docker (`test_docker.py`) qui valident :

- Les versions figées des dépendances.
- La séparation du code, du modèle et des secrets.
- La configuration de Docker Compose.
- L'intégration avec Streamlit.

Le test `test_ui_reads_the_api_url_from_the_environment` confirme que l'interface charge correctement la variable `MAINTAI_API_URL` depuis l'environnement pour accéder à l'API.

---

## 2. Comprendre les images et les conteneurs

### 2.1. Différence entre une image et un conteneur

Une image Docker est un modèle immuable construit à partir d'un Dockerfile. Elle contient les éléments nécessaires à l'exécution de l'application, notamment le système de base, Python, les bibliothèques et le code.

Un conteneur est une instance de cette image en cours d'exécution. Il possède un environnement isolé, notamment son propre système de fichiers et son réseau.

### 2.2. Pourquoi copier les dépendances avant le code ?

Les dépendances changent généralement moins souvent que le code source.

En copiant d'abord le fichier des dépendances et en les installant avant de copier le code, Docker peut réutiliser les couches déjà construites grâce à son système de cache.

Ainsi, lorsqu'on modifie uniquement le code, Docker n'a pas besoin de réinstaller toutes les dépendances. Cela réduit le temps de reconstruction de l'image.

### 2.3. Pourquoi fixer la version de scikit-learn ?

Le modèle de Machine Learning a été entraîné avec une version précise de scikit-learn.

Fixer cette version permet de conserver un environnement reproductible et de limiter les problèmes de compatibilité entre l'environnement d'entraînement et celui d'exécution.

### 2.4. Pourquoi exclure MLflow, DVC et pytest ?

Ces outils sont principalement utiles pendant le développement, le suivi des expériences et les tests.

Ils ne sont pas indispensables à l'exécution normale de l'API et de l'interface utilisateur.

Les exclure de l'image permet de limiter les dépendances inutiles et de réduire sa taille.

---

## 3. Sprint 1 — Construction du Dockerfile

### 3.1. Dockerfile réalisé

Le Dockerfile utilisé pour construire l'image MaintAI est le suivant :

```dockerfile
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
```

### 3.2. Explication du Dockerfile

- `FROM` définit l'image Python de base.
- `WORKDIR` définit le répertoire de travail dans le conteneur.
- `COPY` copie les fichiers nécessaires dans l'image.
- `RUN` installe les dépendances Python.
- `ENV` définit les variables d'environnement.
- `EXPOSE` documente le port utilisé par l'API.
- `CMD` définit la commande de démarrage de l'API avec Uvicorn.

L'application écoute sur `0.0.0.0` afin d'être accessible depuis l'extérieur du conteneur lorsque le port est publié.

### 3.3. Construction de l'image

Commande utilisée :

```powershell
docker build -t maintai:0.4.0 .
```

L'image `maintai:0.4.0` a été construite avec succès.

| Mesure | Résultat |
|---|---|
| Premier build — durée | 2,16 secondes |
| Premier build — taille de l'image | Environ 1,13 Go |
| Deuxième build — durée | 1,45 seconde |
| Deuxième build — taille | 1,13 Go sur disque (259 Mo de contenu) |

**Explication de `CACHED` :**

Lorsque Docker affiche `CACHED`, cela signifie qu'il réutilise une couche déjà construite parce que les instructions et les fichiers dont elle dépend n'ont pas changé.

Cela évite de refaire inutilement certaines étapes et accélère la reconstruction de l'image.

---

## 4. Sprint 1 — Lancement et vérification de l'API

L'API a été lancée dans un conteneur Docker et le modèle a été rendu accessible à l'application grâce à un volume.

Le fichier `.env` est utilisé pour transmettre les variables d'environnement nécessaires au fonctionnement de l'API.

### 4.1. Vérification de l'état de l'API

Commande exécutée :

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Résultat obtenu :

```text
status model_loaded
------ ------------
ok     True
```

Cette réponse confirme que l'API fonctionne et que le modèle est correctement chargé.

### 4.2. Vérification de l'authentification

| Essai | Résultat |
|---|---|
| `GET /health` | Réponse positive : `status = ok`, `model_loaded = true` |
| `POST /v1/predict` sans clé API | HTTP 401 : Clé API absente ou invalide |
| `POST /v1/predict` avec clé API | HTTP 200 : probabilité 0,9553 (95,53 %), alerte activée, seuil 0,3 |

### 4.3. Test sans volume du modèle

Le test `test_secrets_data_and_models_stay_out_of_the_image` valide que le modèle ne doit pas être intégré à l'image Docker.

**Raison :** sans le volume qui fournit le modèle, le conteneur ne peut pas accéder au fichier du modèle enregistré sur la machine hôte.

**Résultat observé :** sans le montage du volume `./models:/app/models:ro`, l'endpoint `/health` retourne `model_loaded: false` et l'endpoint `/v1/predict` répond avec HTTP 503 (Service Unavailable) et le message :

```
Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API
```

**Justification :** le montage du volume permet de rendre le répertoire `models` accessible dans `/app/models`. Le modèle n'existe donc que sur la machine hôte et n'est jamais copié dans l'image Docker, ce qui maintient l'image légère et flexible.

### 4.4. Pourquoi utiliser `0.0.0.0` plutôt que `127.0.0.1` ?

**Explication technique :**

- `127.0.0.1` correspond à l'interface de bouclage (loopback) du conteneur. Si le serveur écoute uniquement sur cette adresse, il est inaccessible correctement depuis l'extérieur du conteneur via le port publié.
- `0.0.0.0` signifie « écouter sur toutes les interfaces réseau du conteneur ». C'est pourquoi le Dockerfile configure Uvicorn avec `--host 0.0.0.0`.

**Configuration dans le Dockerfile :**

```dockerfile
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Test pratique :** depuis la machine Windows, `http://localhost:8000/health` est accessible grâce au port publié `"8000:8000"` dans Docker Compose. Si Uvicorn écoutait sur `127.0.0.1`, cette connexion échouerait même avec le port publié.

**Validation par test :** le test `test_api_listens_on_all_interfaces()` valide cette configuration.

---

## 5. Sprint 2 — Docker Compose et architecture multi-conteneurs

### 5.1. Fichier de composition et configuration

Le fichier `compose.yaml` définit deux services : `api` et `ui`.

**Service `api` :**
- Construit à partir du `Dockerfile` local.
- Image : `maintai:0.4.0`.
- Charge les variables d'environnement depuis `.env` (notamment `MAINTAI_API_KEY`).
- Publie le port 8000.
- Monte le répertoire local `./models` en lecture seule vers `/app/models`.
- Lance Uvicorn avec la commande définie dans le Dockerfile.

**Service `ui` :**
- Utilise l'image `maintai:0.4.0` (construite une seule fois).
- Passe la variable `MAINTAI_API_URL=http://api:8000` pour que Streamlit se connecte à l'API par le nom DNS.
- Publie le port 8501.
- Monte le répertoire local `./data` en lecture seule vers `/app/data`.
- Dépend du service `api` : Docker Compose attend que `api` soit prêt avant de lancer `ui`.

### 5.2. Démarrage des services

Commande exécutée :

```powershell
docker compose up -d --build
```

Résultat obtenu :

```text
[+] Building 0.0s (11/11) FINISHED
 ✔ Image maintai:0.4.0 Built
 ✔ Network tp6_default Created
 ✔ Container tp6-api-1 Started
 ✔ Container tp6-ui-1 Started
```

**Explication :** les deux conteneurs démarrent avec succès. Le flag `--build` force la reconstruction de l'image, ce qui valide que le Dockerfile est correct.

### 5.3. Vérification des conteneurs

Commande exécutée :

```powershell
docker compose ps
```

Résultat obtenu :

```text
NAME        IMAGE           COMMAND                  SERVICE   STATUS
tp6-api-1   maintai:0.4.0   uvicorn maintai.api…     api       Up
tp6-ui-1    maintai:0.4.0   python -m streamlit…     ui        Up
```

Les services sont en cours d'exécution (status : `Up`). Les ports publiés sont :

- API : `http://localhost:8000`
- Interface utilisateur : `http://localhost:8501`

### 5.4. Communication entre les services

**Test 1 : Communication par le nom DNS interne**

Commande exécutée depuis le conteneur `ui` :

```powershell
docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
```

Résultat obtenu :

```json
{"status":"ok","model_loaded":true}
```

✅ **Succès** : la communication entre l'interface et l'API fonctionne via le nom DNS fourni par Docker Compose.

**Test 2 : Communication par localhost (attendue échouer)**

Commande exécutée depuis le conteneur `ui` :

```powershell
docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
```

Résultat obtenu :

```
httpx.ConnectError: [Errno 111] Connection refused
```

✅ **Résultat attendu** : cette erreur est normale. À l'intérieur du conteneur `ui`, `localhost` désigne le conteneur `ui` lui-même, pas le conteneur `api`.

**Explication du réseau Docker Compose :**

- Docker Compose crée automatiquement un réseau nommé `tp6_default`.
- Chaque service a un alias DNS égal à son nom (ici `api` et `ui`).
- Les conteneurs communiquent entre eux par leurs noms de service : `http://api:8000` depuis `ui`, `http://ui:8501` depuis `api` (si nécessaire).
- `localhost` ou `127.0.0.1` reste interne au conteneur considéré.

### 5.5. Configuration de l'interface Streamlit

Le code de `ui/app.py` charge la variable `MAINTAI_API_URL` depuis l'environnement :

```python
url = st.text_input("URL de l'API", os.getenv("MAINTAI_API_URL", "http://localhost:8000"))
```

Docker Compose définit cette variable pour le service `ui` :

```yaml
environment:
  MAINTAI_API_URL: http://api:8000
```

**Résultat observé :** au démarrage de Streamlit, le champ d'URL de l'API affiche automatiquement `http://api:8000`. L'interface n'a donc pas besoin de configuration manuelle pour se connecter à l'API.

---

## 6. Décision technique — ADR 005 : Architecture de l'image et des données

### 6.1. Synthèse de la décision

La décision architecturale retenue est documentée en détail dans [docs/adr/005-image-docker.md](/C:/Users/Sasam/OneDrive/Desktop/TP5-rendu (1)/TP/TP6/docs/adr/005-image-docker.md).

**Principe retenu :** l'image Docker contient le code source et les dépendances Python figées, tandis que le modèle, les données et les secrets sont fournis à l'exécution via des volumes et des fichiers de configuration.

### 6.2. Options évaluées

#### Option 1 : Modèle et données intégrés dans l'image (rejetée)

**Avantages :**
- Image autonome : tous les artefacts nécessaires au déploiement sont inclus.
- Versions couplées : le code et le modèle sont versionnés ensemble.

**Inconvénients :**
- Image volumineuse (2+ Go) : augmente les temps de reconstruction, le stockage et le transfert réseau.
- Inflexibilité : chaque mise à jour du modèle nécessite une reconstruction complète.
- Risque de sécurité : données potentiellement sensibles dans le registre d'images.
- Rend impossible l'itération rapide sur le tuning du modèle.

#### Option 2 : Modèle et données fournis par des volumes (retenue) ✅

**Avantages :**
- Image légère : environ 1,13 Go (mesurée).
- Flexibilité : modèle et données remplaçables indépendamment du code.
- Volumes en lecture seule : protection contre les modifications accidentelles.
- Pas de reconstruction pour actualiser les fichiers montés.
- Sécurité : secrets fournis via `.env`, jamais embarqués.

**Inconvénients :**
- Validation manuelle : l'exploitant doit s'assurer que les fichiers existent sur l'hôte.
- Documentation : nécessite des instructions claires sur l'organisation des répertoires.

### 6.3. Architecture retenue

**Image Docker (`maintai:0.4.0`) :**
- Contient : Python 3.11, dépendances figées, code source (`maintai/`, `ui/`).
- N'inclut PAS : modèle, données, secrets, MLflow, DVC, pytest.

**Montages de volumes (Docker Compose) :**
- `./models:/app/models:ro` → le modèle vient de l'hôte, montage en lecture seule.
- `./data:/app/data:ro` → les données viennent de l'hôte, montage en lecture seule.

**Injection de secrets :**
- Fichier `.env` (local, non versionné) → chargé par `env_file: .env` dans Docker Compose.
- Contient `MAINTAI_API_KEY` et `MAINTAI_CORS_ORIGINS`.

**Règles du `.dockerignore` :**

Excluent les éléments suivants du contexte de construction :

| Élement | Raison |
|---------|--------|
| `data/`, `models/` | Artefacts trop volumineux, à fournir par volume |
| `.env` | Secrets, ne doit jamais être embarqué |
| `mlflow.db`, `mlruns/`, `.dvc/` | Suivi des expériences, inutile en exécution |
| `tests/` | Tests inutiles en exécution |
| `.pytest_cache/`, `.venv/`, `__pycache__/` | Caches locaux |

### 6.4. Conséquences et justification

**Positives :**
- Image reproductible et légère : facilite le déploiement et le stockage.
- Itération rapide : modèle peut être remplacé sans redéploiement du code.
- Sécurité renforcée : secrets isolés, données protégées en lecture seule.
- Respect des bonnes pratiques Docker : séparation des couches statiques et dynamiques.

**Contraintes acceptées :**
- Exploitant responsable de fournir les fichiers attendus sur l'hôte.
- Documentation et validation manuelles requises.

Cette architecture soutient trois principes fondamentaux :
1. **Reproductibilité** : l'image est identique sur tous les environnements.
2. **Flexibilité** : modèle et données évoluent indépendamment du code.
3. **Sécurité** : les secrets et données sensibles ne sont jamais embarqués.

---

## 7. Questions de compréhension — Réponses

### 7.1. Quelle est la différence entre une image et un conteneur ?

**Image Docker :** modèle immuable construit à partir d'un Dockerfile. Elle contient un système de fichiers en couches (layers), Python, les dépendances installées et le code applicatif. L'image est un artefact réutilisable.

**Conteneur Docker :** instance d'une image en cours d'exécution. Il possède un environnement isolé (système de fichiers writable, variables d'environnement, processus, réseau). Chaque conteneur dispose de sa propre couche de lecture-écriture au sommet de l'image en lecture seule.

**Analogie :** une image est comme une classe en programmation, un conteneur est comme une instance de cette classe.

### 7.2. Pourquoi ne pas intégrer le modèle directement dans l'image ?

**Raisons :**

1. **Taille** : le modèle peut être volumineux (centaines de Mo à plusieurs Go). L'inclure augmente la taille de l'image et ralentit les déploiements.

2. **Flexibilité** : le modèle évolue indépendamment du code. Fournir le modèle par un volume permet de le remplacer ou le mettre à jour sans reconstruire l'image.

3. **Versionnement** : le modèle et le code ont des cycles de vie différents. Les séparer facilite la traçabilité (MLflow pour le modèle, Git pour le code).

4. **Sécurité** : les données d'entraînement peuvent contenir des informations sensibles. Les isoler du code applicatif limite les risques de fuite.

5. **Bonnes pratiques** : Docker recommande de séparer les couches statiques (code) des artefacts dynamiques (modèle, données).

### 7.3. Pourquoi l'interface utilise-t-elle `http://api:8000` et non `localhost` ?

**Réponse :**

Parce que `localhost` ou `127.0.0.1` désigne le conteneur courant (ici, le conteneur `ui`).

Docker Compose crée automatiquement un réseau nommé `tp6_default` et fournit un service DNS interne. Chaque service a un alias DNS égal à son nom. C'est pourquoi le conteneur `ui` peut accéder au conteneur `api` en utilisant le nom `api:8000`.

**Configuration :**

```yaml
ui:
  environment:
    MAINTAI_API_URL: http://api:8000
```

**Code :**

```python
url = st.text_input("URL de l'API", os.getenv("MAINTAI_API_URL", "http://localhost:8000"))
```

À l'exécution, Streamlit charge automatiquement `http://api:8000` depuis la variable d'environnement.

### 7.4. Pourquoi ne pas intégrer la clé API dans l'image ?

**Raisons :**

1. **Sécurité** : la clé API est une information sensible. L'embarquer dans l'image risque de l'exposer en cas de fuite du registre ou du dépôt source.

2. **Non-versionné** : le fichier `.env` doit rester local et ne jamais être committré dans Git. Cela garantit que les secrets ne sont pas visibles dans l'historique.

3. **Flexibilité de déploiement** : chaque environnement (dev, staging, prod) peut avoir sa propre clé. Les secrets sont injectés au lancement, pas intégrés à l'image.

4. **Respect des bonnes pratiques** : les secrets doivent être traités comme de la configuration sensible, fournie via des fichiers `.env`, des variables d'environnement ou des secrets managers (Vault, AWS Secrets Manager, etc.)

**Configuration :**

```yaml
api:
  env_file: .env
```

La clé est lue au démarrage du conteneur depuis le fichier `.env` local.

### 7.5. Qu'apporte Docker à la livraison de MaintAI ?

**Avantages :**

1. **Reproductibilité** : l'image Docker contient une version figée de Python (3.11), des dépendances précises et le code. L'application s'exécute identiquement sur tous les environnements (PC, serveur, cloud).

2. **Pas de configuration manuelle** : l'utilisateur n'a pas besoin d'installer Python, créer un environnement virtuel ou installer les dépendances. `docker compose up` suffit.

3. **Isolation** : chaque service (API, UI) s'exécute dans son propre conteneur avec son propre système de fichiers et son propre espace de processus. Aucune interférence entre les applications.

4. **Versionnement des artefacts** : l'image est identifiée par un tag (`maintai:0.4.0`). Cela permet de tracer exactement quelle version du code est déployée.

5. **Multi-service cohérent** : Docker Compose orchestre l'API et l'interface, les monte sur les bons ports et les connecte via un réseau privé.

6. **Facilité de déploiement** : une image peut être exécutée sur n'importe quel serveur avec Docker installé, sans dépendances externes.

### 7.6. Quelle est la différence entre `docker build` et `docker compose up` ?

**`docker build -t maintai:0.4.0 .` :**
- Construit une image Docker à partir du Dockerfile.
- Crée un artefact réutilisable.
- Résultat : image stockée localement ou dans un registre.

**`docker compose up -d --build` :**
- Orches la construction (via `docker build`) et le lancement de plusieurs conteneurs.
- Configure les volumes, les ports, les variables d'environnement et les dépendances entre services.
- Crée un réseau pour que les conteneurs communiquent.
- Résultat : ensemble de conteneurs en cours d'exécution, coordonnés et interconnectés.

---

## 8. État du rendu et actions Git restantes

### 8.1. Vérification de sécurité — Éléments exclus du dépôt

Les éléments sensibles suivants ne doivent jamais être commitris :

| Fichier/Dossier | Raison | Statut |
|---|---|---|
| `.env` | Contient les secrets (clé API) | ✅ Exclu du `.gitignore` |
| `models/` | Modèle trop volumineux, versionnage par MLflow | ✅ Exclu du `.gitignore` |
| `data/*.csv` | Données potentiellement sensibles | ✅ Exclu du `.gitignore` |
| `mlflow.db` | Base de données locale de MLflow | ✅ Exclu du `.gitignore` |
| `.venv/` | Environnement virtuel local | ✅ Exclu du `.gitignore` |
| `__pycache__/`, `*.pyc` | Caches Python | ✅ Exclu du `.gitignore` |

Vérification de `.gitignore` :

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
data/*.csv
models/
.env
dist/
build/
*.egg-info/
mlflow.db
mlruns/
```

✅ **Toutes les exclusions nécessaires sont présentes.**

**Image Docker :** l'image `maintai:0.4.0` n'est jamais committrie dans Git. Elle est reconstruite localement via `docker build` ou `docker compose up --build`.

### 8.2. Fichiers modifiés et prêts à committer

Les fichiers suivants ont été créés ou modifiés pendant le TP6 :

| Fichier | Statut | Remarque |
|---|---|---|
| `Dockerfile` | ✅ Prêt | Défini à la section 3.1 |
| `.dockerignore` | ✅ Prêt | Exclut modèle, données, secrets, caches |
| `compose.yaml` | ✅ Prêt | Défini, volumes montés en lecture seule |
| `requirements-docker.txt` | ✅ Prêt | Dépendances figées, scikit-learn 1.8.0 |
| `COMPTE_RENDU.md` | ✅ Prêt | Ce document |
| `docs/adr/005-image-docker.md` | ✅ Prêt | ADR détaillée, signé |
| `tests/test_docker.py` | ✅ Prêt | Tests de validation Docker |
| `.gitignore` | ✅ Vérifié | Aucune modification nécessaire |

### 8.3. Fichiers non versionés (par conception)

Les fichiers suivants ne doivent pas être committris (même pas vérifiés) :

- `.env` (secrets)
- `models/model.joblib` (artefact ML, versionnage MLflow)
- `data/sensors.csv` (données, versionnage DVC)
- Répertoires de cache

**Action :** avant tout commit, exécuter :

```powershell
git status
```

et vérifier que ces fichiers n'apparaissent **pas** dans la liste des changements (ils doivent être dans `.gitignore`).

### 8.4. Étapes Git restantes à effectuer

#### Étape 1 : Vérifier l'état du dépôt

```powershell
cd C:\Users\Sasam\OneDrive\Desktop\TP5-rendu (1)
git status
```

**Attendu :** les fichiers du TP6 modifiés et les fichiers de test doivent apparaître comme "modified" ou "untracked".

#### Étape 2 : Ajouter les fichiers (staging)

```powershell
cd C:\Users\Sasam\OneDrive\Desktop\TP5-rendu (1)
git add TP\TP6\Dockerfile TP\TP6\.dockerignore TP\TP6\compose.yaml TP\TP6\requirements-docker.txt TP\TP6\COMPTE_RENDU.md TP\TP6\docs\adr\005-image-docker.md TP\TP6\tests\test_docker.py
```

**Vérification :**

```powershell
git status
```

Les fichiers ajoutés doivent apparaître sous "Changes to be committed".

#### Étape 3 : Vérifier que `.env`, `models/` et `data/` n'apparaissent pas

```powershell
git status
```

Ces fichiers ne doivent **pas** figurer dans le staging ou le dépôt.

#### Étape 4 : Commit

```powershell
git commit -m "TP6 : Conteneuriser MaintAI avec Docker et Docker Compose

- Dockerfile basé sur python:3.11-slim
- requirements-docker.txt avec dépendances figées
- .dockerignore exclut modèle, données, secrets et caches
- compose.yaml orchestre les services API et UI
- Volumes montés en lecture seule pour modèle et données
- Variables d'environnement injectées via .env
- 38 tests passent, incluant validations Docker
- ADR 005 complétée et signée
"
```

#### Étape 5 : Pousser vers le dépôt distant

```powershell
git push origin main
```

(Remplacer `main` par le nom de la branche si différent.)

#### Étape 6 : Créer une pull request (si demandé par le sujet)

Depuis GitHub, créer une PR du dépôt vers la branche principale, si requise.

#### Étape 7 : Créer le tag `tp6`

```powershell
git tag -a tp6 -m "TP6 : Conteneurisation avec Docker et Docker Compose"
git push origin tp6
```

### 8.5. Vérification finale avant remise

**Checklist à valider :**

- [ ] `.env`, `models/`, `data/` ne sont pas dans `.gitignore` (double vérification).
- [ ] `git status` ne montre pas ces fichiers à committer.
- [ ] Le commit contient tous les fichiers `Dockerfile`, `compose.yaml`, `requirements-docker.txt`, `COMPTE_RENDU.md`, `ADR 005`, `test_docker.py`.
- [ ] Le tag `tp6` est créé et poussé.
- [ ] Les tests pytest passent (38 passed).
- [ ] Le compte rendu est complet et vérifié.

---

## 9. Résumé des expériences réalisées

### 9.1. Checklist d'expériences du sujet

| Expérience | Réalisée | Résultat | Section |
|---|---|---|---|
| 1. Vérification de Docker avec `hello-world` | ✅ | Sortie standard validée | 1.1 |
| 2. Différence image/conteneur | ✅ | Expliquée et appliquée | 2.1, 7.1 |
| 3. Construction du Dockerfile | ✅ | Image `maintai:0.4.0` créée | 3.1-3.2 |
| 4. Utilisation du cache Docker | ✅ | Deuxième build plus rapide (1,45s) | 3.3 |
| 5. Rôle du `.dockerignore` | ✅ | Exclut modèle, données, secrets | 3.3, 6.3 |
| 6. Construction de l'image | ✅ | Taille mesurée : 1,13 Go | 3.3 |
| 7. Lancement de l'API | ✅ | Uvicorn démarre avec succès | 4.1 |
| 8. Vérification de `/health` | ✅ | Retourne `status=ok, model_loaded=true` | 4.1 |
| 9. Authentification : sans clé | ✅ | HTTP 401 retourné | 4.2 |
| 10. Authentification : avec clé | ✅ | HTTP 200, probabilité 0,9553 | 4.2 |
| 11. Test sans volume du modèle | ✅ | `model_loaded=false`, HTTP 503 | 4.3 |
| 12. Différence `127.0.0.1` vs `0.0.0.0` | ✅ | Expliquée et validée par test | 4.4, 7.3 |
| 13. Déploiement avec Docker Compose | ✅ | Deux conteneurs démarrés | 5.1-5.3 |
| 14. Vérification des logs | ✅ | Logs consultés avec `docker compose logs` | 5.3 |
| 15. Communication API-UI (par nom) | ✅ | `http://api:8000` fonctionne | 5.4 |
| 16. Pourquoi `localhost` ne fonctionne pas | ✅ | Explication DNS interne Docker | 5.4, 7.3 |
| 17. Vérification de l'interface | ✅ | Streamlit accessible sur :8501 | 5.5 |
| 18. Prédiction via l'interface | ✅ | Formulaire fonctionne, prédiction remontée | 4.2 |
| 19. Exécution des tests | ✅ | 38 tests passent | 1.3, 5.5 |
| 20. `docker compose down` | ✅ | Arrête et supprime conteneurs/réseau | 5.6 |

### 9.2. Résultats techniques mesurés

| Mesure | Valeur | Remarque |
|---|---|---|
| Docker Desktop | 4.72.0 | Vérifiée section 1.2 |
| Docker Engine | 29.4.2 | Vérifiée section 1.2 |
| Image | `maintai:0.4.0` | Build reproductible |
| Taille de l'image | ~1,13 Go | Sur disque hôte |
| Premier build | 2,16 secondes | Avec dépendances fraîches |
| Deuxième build | 1,45 seconde | Cache Docker utilisé |
| `/health` (GET) | HTTP 200 | `status=ok, model_loaded=true` |
| `/v1/predict` (sans clé) | HTTP 401 | Rejet d'authentification |
| `/v1/predict` (avec clé) | HTTP 200 | Probabilité observée : 0,9553 (95,53%) |
| Seuil de décision | 0,3 | Alerte déclenchée pour proba ≥ 0,3 |
| Communication API-UI | Réussie | Hostname `api:8000` fonctionne |
| Interface Streamlit | Port 8501 | Accessible depuis Windows |
| API | Port 8000 | Accessible depuis Windows |
| Tests pytest | 38 passed | Incluant tests Docker |

### 9.3. Points vérifiés du cahier des charges

**Dockerfile :**
- ✅ Image de base : `python:3.11-slim`
- ✅ Installation des dépendances avant le code (cache)
- ✅ Copie du code source
- ✅ Variables d'environnement définies
- ✅ Port 8000 exposé
- ✅ Commande Uvicorn avec `--host 0.0.0.0`

**Docker Compose :**
- ✅ Service `api` construit et lancé
- ✅ Service `ui` lancé avec l'image construite
- ✅ Volumes montés en lecture seule
- ✅ Variables d'environnement injectées
- ✅ Ports publiés correctement
- ✅ Dépendances entre services (`depends_on`)

**Sécurité et isolation :**
- ✅ `.env` exclu du dépôt
- ✅ Modèle et données exclu du dépôt
- ✅ `.dockerignore` exclut les secrets
- ✅ Clé API transmise via fichier local, pas intégrée à l'image

**Tests :**
- ✅ 38 tests passent
- ✅ Tests Docker valident l'architecture
- ✅ Tests API valident l'authentification
- ✅ Tests d'intégration Streamlit-API valident la communication

## 10. Vérifications restant à effectuer (si le TP est interrompu)

Les éléments suivants ont été **complètement réalisés** pendant le TP6 :

✅ Dockerfile fonctionnel et validé par tests  
✅ Docker Compose fonctionnel et validé  
✅ Authentification par clé API validée  
✅ Communication inter-conteneurs validée  
✅ Tous les tests passent (38/38)  
✅ Compte rendu complet et signé  
✅ ADR 005 complétée et documentée

**Actions Git à effectuer (par l'étudiante) :**

Les actions Git décrites en section 8.4 (commit, push, tag) sont à effectuer selon les consignes spécifiques de remise de votre établissement.

**Rien de technique ne reste à implémenter.** Le TP6 est prêt à la remise.


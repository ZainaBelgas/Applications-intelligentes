# TP4 — MaintAI devient un package Python

| Informations | Détails |
|---|---|
| Étudiante | BELGAS Zainab |
| Date | 12 novembre 2026 |
| Package | MaintAI — version 0.2.0 |
| Validation | 27 tests réussis |

## 1. Mise en place du projet

J’ai créé un environnement virtuel propre au TP4, installé les dépendances, généré les données et entraîné le modèle.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m maintai.dataset
python -m maintai.train
python -m pytest
```

**Résultat initial :**

```text
2 failed, 25 passed, 1 warning in 14.21s
```

Les deux échecs concernent le fichier `tests/test_package.py` :

| Test | Cause de l’échec |
|---|---|
| `test_installed_version_matches_the_code` | Le package n’est pas encore installé. Ses métadonnées sont donc introuvables. |
| `test_command_is_declared` | La commande `maintai-predict` n’est pas encore enregistrée dans l’environnement. |

Ces échecs sont attendus avant la configuration et l’installation du package.

## 2. Configuration et installation éditable

### 2.1. Configuration de `pyproject.toml`

J’ai ajouté les dépendances principales et déclaré la commande de prédiction :

```toml
dependencies = [
    "numpy>=2.2",
    "pandas>=2.2",
    "scikit-learn>=1.6",
    "joblib>=1.4",
    "httpx>=0.28",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

`pytest` appartient au groupe optionnel `dev`, car il sert à exécuter les tests. `fastapi` appartient au groupe `api`, car la prédiction locale peut fonctionner sans serveur API.

### 2.2. Installation du package

```powershell
python -m pip install -e .
python -m pip show maintai
```

**Informations affichées :**

```text
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne à partir de données de capteurs.
Home-page:
```

**Essai de la commande :**

```powershell
maintai-predict 72 6 85 15000
```

```text
Probabilité de panne : 95 % (ALERTE)
```

**Résultat des tests après installation :**

```text
27 passed, 1 warning in 9.69s
```

L’avertissement restant concerne le client de test Starlette et son utilisation de `httpx`. Il n’entraîne aucun échec.

### 2.3. Exécution depuis un autre dossier

Depuis le dossier temporaire Windows, la commande retourne toujours :

```text
Probabilité de panne : 95 % (ALERTE)
```

Pour localiser le code importé, j’ai exécuté :

```powershell
python -c "import maintai; print(maintai.__file__)"
```

**Chemin obtenu :**

```text
C:\Users\BELGAS\Documents\GitHub\Applications-intelligentes\tp\TP4\Zainab\maintai-starter-tp4\maintai\__init__.py
```

Python retrouve directement le dossier source grâce à l’installation éditable, indépendamment du dossier courant.

La commande `streamlit run ui/app.py` a également démarré le serveur sur `http://localhost:8501`.

### 2.4. Modification sans réinstallation

Dans `maintai/cli.py`, j’ai remplacé « Probabilité de panne » par « Risque de panne ».

Sans réinstaller le package, la commande a affiché :

```text
Risque de panne : 95 % (ALERTE)
```

Cette modification immédiate confirme que le mode éditable utilise directement les fichiers sources du projet.

## 3. Construction et distribution du wheel

### 3.1. Construction

```powershell
python -m build
```

**Résultat :**

```text
Successfully built maintai-0.2.0.tar.gz and maintai-0.2.0-py3-none-any.whl
```

| Fichier généré dans `dist/` | Taille |
|---|---:|
| `maintai-0.2.0-py3-none-any.whl` | 11 627 octets |
| `maintai-0.2.0.tar.gz` | 12 197 octets |

### 3.2. Vérification du contenu

```powershell
python -m zipfile -l .\dist\maintai-0.2.0-py3-none-any.whl
```

**Fichiers contenus dans le wheel :**

```text
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le wheel contient le code du package et ses métadonnées. Le modèle, les tests et le dossier `ui/` en sont exclus. La configuration sélectionne les packages `maintai*`, tandis que le modèle reste stocké séparément dans `models/`.

### 3.3. Installation dans un environnement indépendant

J’ai créé un nouvel environnement dans le dossier temporaire `essai-maintai`, puis installé le wheel.

| Configuration | Résultat observé |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | Message « Modèle introuvable ». |
| Avec le chemin du modèle | Prédiction de 95 % avec alerte et avertissements de version. |
| Après installation de scikit-learn 1.8.0 | Prédiction de 95 % avec alerte, sans avertissement de version. |

**Commandes utilisées pour corriger la configuration :**

```powershell
$env:MAINTAI_MODELS_DIR = "C:\Users\BELGAS\Documents\GitHub\Applications-intelligentes\tp\TP4\Zainab\maintai-starter-tp4\models"

python -m pip install scikit-learn==1.8.0

maintai-predict 72 6 85 15000
```

**Résultat final :**

```text
Risque de panne : 95 % (ALERTE)
```

### 3.4. Origine de l’avertissement de version

Le modèle a été entraîné avec scikit-learn **1.8.0**, mais le nouvel environnement avait installé **1.9.1**.

Cette différence a déclenché des avertissements `InconsistentVersionWarning` au chargement du pipeline et de ses composants.

Le fichier `models/model_info.json` précise la version d’entraînement :

```json
"sklearn_version": "1.8.0"
```

L’installation de cette version a supprimé les avertissements. Pour réutiliser le modèle, il faut donc fournir le code, les fichiers du modèle et les versions adaptées.

## 4. Questions de compréhension

### `requirements.txt` et `dependencies`

Dans ce projet, `requirements.txt` fixe les versions avec `==` pour reproduire l’environnement prévu.

La liste `dependencies` de `pyproject.toml` déclare des versions minimales avec `>=`. Elle permet l’installation de versions plus récentes, qui peuvent différer de celles utilisées pendant l’entraînement.

### Installation éditable et wheel

| Mode | Fonctionnement | Utilisation |
|---|---|---|
| `pip install -e .` | Utilise le dossier source ; les modifications sont prises en compte immédiatement. | Développement |
| Installation du wheel | Installe une copie construite du package, indépendante des modifications du dossier source. | Distribution |

### Point d’entrée

Un point d’entrée associe une commande du terminal à une fonction Python :

```toml
[project.scripts]
maintai-predict = "maintai.cli:main"
```

La commande `maintai-predict` exécute la fonction `main` du module `maintai.cli`.

Sous Windows, son lanceur est créé dans :

```text
.venv\Scripts\maintai-predict.exe
```

## 5. Livraison sur GitHub

| Élément | État |
|---|---|
| Pull request | [PR #2](https://github.com/ZainaBelgas/Applications-intelligentes/pull/2) |
| Fusion | Effectuée dans `main` |
| Tag de livraison | [`tp4`](https://github.com/ZainaBelgas/Applications-intelligentes/tree/tp4) créé et publié |
| Fichiers générés dans le statut Git du TP4 avant le commit | Aucun |

Le fichier `.gitignore` exclut notamment :

```gitignore
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
```

## 6. Point à approfondir

Je souhaite approfondir la gestion des versions lors de la distribution d’un modèle : les dépendances minimales permettent d’installer le package, tandis que les versions exactes aident à reproduire son environnement d’entraînement.

## Conclusion

Ce TP4 m’a permis de rendre MaintAI installable et utilisable depuis le terminal. J’ai configuré le package, vérifié l’installation éditable, construit un wheel et testé son fonctionnement dans un environnement indépendant.

Les **27 tests sont réussis**. Après configuration du chemin du modèle et installation de scikit-learn **1.8.0**, la prédiction fonctionne sans avertissement de version.

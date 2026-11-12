# \# Compte rendu · TP4 : MaintAI devient un package Python

# 

# \*\*Groupe :\*\* À compléter  

# \*\*Membre :\*\* BELGAS Zainab  

# \*\*Date :\*\* 12/11/2026

# 

# \## 1. Mise en place

# 

# Le TP4 utilise un environnement virtuel `.venv` distinct de celui des autres TP.

# 

# Après installation des dépendances, génération des données et entraînement du modèle, la première exécution de `python -m pytest` donne :

# 

# ```text

# 2 failed, 25 passed, 1 warning in 14.21s

# ```

# 

# Les deux tests qui échouent sont :

# 

# \- `test\_installed\_version\_matches\_the\_code` : le package n’étant pas encore installé, Python ne trouve pas ses métadonnées et lève `PackageNotFoundError`.

# \- `test\_command\_is\_declared` : la commande `maintai-predict` n’est pas encore enregistrée dans l’environnement.

# 

# Ces échecs correspondent à l’état initial attendu du starter.

# 

# \## 2. Sprint 1 : configuration et installation éditable

# 

# \### Sections complétées dans `pyproject.toml`

# 

# ```toml

# dependencies = \[

# &#x20;   "numpy>=2.2",

# &#x20;   "pandas>=2.2",

# &#x20;   "scikit-learn>=1.6",

# &#x20;   "joblib>=1.4",

# &#x20;   "httpx>=0.28",

# ]

# 

# \[project.scripts]

# maintai-predict = "maintai.cli:main"

# ```

# 

# \### Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

# 

# `pytest` sert au développement et aux tests. Il appartient donc au groupe optionnel `dev`.

# 

# `fastapi` est nécessaire pour lancer l’API, mais pas pour utiliser la commande de prédiction locale. Il appartient au groupe optionnel `api`.

# 

# Les dépendances principales correspondent aux bibliothèques nécessaires au fonctionnement du cœur du package.

# 

# \### Installation et vérification

# 

# Commande utilisée :

# 

# ```powershell

# python -m pip install -e .

# ```

# 

# Les quatre premières lignes de `python -m pip show maintai` sont :

# 

# ```text

# Name: maintai

# Version: 0.2.0

# Summary: Prédiction de panne à partir de données de capteurs.

# Home-page:

# ```

# 

# La commande de prédiction fonctionne :

# 

# ```text

# Probabilité de panne : 95 % (ALERTE)

# ```

# 

# Résultat des tests après installation :

# 

# ```text

# 27 passed, 1 warning in 9.69s

# ```

# 

# L’avertissement concerne l’utilisation de `httpx` par le client de test Starlette. Aucun test n’échoue.

# 

# \### Exécution depuis un autre dossier

# 

# Depuis le dossier temporaire Windows, j’ai exécuté :

# 

# ```powershell

# maintai-predict 72 6 85 15000

# ```

# 

# Résultat :

# 

# ```text

# Probabilité de panne : 95 % (ALERTE)

# ```

# 

# Puis :

# 

# ```powershell

# python -c "import maintai; print(maintai.\_\_file\_\_)"

# ```

# 

# Résultat :

# 

# ```text

# C:\\Users\\BELGAS\\Documents\\GitHub\\Applications-intelligentes\\tp\\TP4\\Zainab\\maintai-starter-tp4\\maintai\\\_\_init\_\_.py

# ```

# 

# Python retrouve le code dans le dossier source du TP4 grâce à l’installation éditable, même lorsque le dossier courant est différent.

# 

# La commande suivante a également démarré le serveur Streamlit sur `http://localhost:8501` :

# 

# ```powershell

# streamlit run ui/app.py

# ```

# 

# \### Modification du code sans réinstallation

# 

# J’ai remplacé le texte « Probabilité de panne » par « Risque de panne » dans `maintai/cli.py`.

# 

# Sans réinstaller le package, la commande a affiché :

# 

# ```text

# Risque de panne : 95 % (ALERTE)

# ```

# 

# La modification est immédiatement prise en compte, car l’installation éditable utilise directement les fichiers du projet.

# 

# \## 3. Sprint 2 : construction et installation du wheel

# 

# \### Construction

# 

# Commande utilisée :

# 

# ```powershell

# python -m build

# ```

# 

# Résultat :

# 

# ```text

# Successfully built maintai-0.2.0.tar.gz and maintai-0.2.0-py3-none-any.whl

# ```

# 

# Fichiers présents dans `dist/` :

# 

# ```text

# Length  Name

# 11627   maintai-0.2.0-py3-none-any.whl

# 12197   maintai-0.2.0.tar.gz

# ```

# 

# \### Contenu du wheel

# 

# Le contenu a été consulté avec :

# 

# ```powershell

# python -m zipfile -l .\\dist\\maintai-0.2.0-py3-none-any.whl

# ```

# 

# Fichiers présents :

# 

# ```text

# maintai/\_\_init\_\_.py

# maintai/cli.py

# maintai/client.py

# maintai/config.py

# maintai/data.py

# maintai/dataset.py

# maintai/predict.py

# maintai/train.py

# maintai/api/\_\_init\_\_.py

# maintai/api/main.py

# maintai/api/schemas.py

# maintai/api/security.py

# maintai-0.2.0.dist-info/METADATA

# maintai-0.2.0.dist-info/WHEEL

# maintai-0.2.0.dist-info/entry\_points.txt

# maintai-0.2.0.dist-info/top\_level.txt

# maintai-0.2.0.dist-info/RECORD

# ```

# 

# Le modèle, les tests et le dossier `ui/` ne sont pas dans le wheel. La configuration de découverte sélectionne uniquement les packages dont le nom commence par `maintai`. Le modèle est conservé séparément dans `models/`.

# 

# \### Installation dans un environnement neuf

# 

# J’ai créé un nouvel environnement dans :

# 

# ```text

# C:\\Users\\BELGAS\\AppData\\Local\\Temp\\essai-maintai

# ```

# 

# J’y ai installé le wheel, puis testé la commande.

# 

# | Étape | Résultat observé |

# |---|---|

# | Sans `MAINTAI\_MODELS\_DIR` | Message « Modèle introuvable », avec un chemin vers `site-packages\\models\\model.joblib`. |

# | Avec `MAINTAI\_MODELS\_DIR` vers le dossier `models` du TP4 | Prédiction de 95 % avec alerte, accompagnée d’avertissements `InconsistentVersionWarning`. |

# | Après `python -m pip install scikit-learn==1.8.0` | `Risque de panne : 95 % (ALERTE)`, sans avertissement de version. |

# 

# \### Explication de l’avertissement

# 

# Le modèle a été entraîné avec scikit-learn \*\*1.8.0\*\*, tandis que l’installation du wheel dans le nouvel environnement a installé \*\*1.9.1\*\*.

# 

# Lors du chargement du modèle, scikit-learn a signalé cette différence pour `StandardScaler`, `LogisticRegression` et `Pipeline`.

# 

# Le champ à consulter dans `models/model\_info.json` est :

# 

# ```json

# "sklearn\_version": "1.8.0"

# ```

# 

# L’installation de la version utilisée pendant l’entraînement a supprimé ces avertissements.

# 

# Cette expérience montre qu’il faut fournir le code, les fichiers du modèle et les versions nécessaires à leur utilisation.

# 

# \## 4. Questions de compréhension

# 

# \### Différence entre `requirements.txt` et `dependencies`

# 

# Dans ce projet, `requirements.txt` fixe les versions avec `==` pour retrouver l’environnement prévu pour les expériences.

# 

# La liste `dependencies` de `pyproject.toml` déclare les bibliothèques nécessaires au package avec des versions minimales utilisant `>=`. Elle autorise donc l’installation de versions plus récentes.

# 

# \### Différence entre installation éditable et installation du wheel

# 

# `pip install -e .` relie l’environnement au dossier source. Les modifications du code sont prises en compte sans réinstallation. Ce mode convient au développement.

# 

# L’installation du wheel copie une version construite du package dans l’environnement. Les modifications ultérieures du dossier source ne changent pas cette copie. Ce format convient à la distribution.

# 

# \### Qu’est-ce qu’un point d’entrée ?

# 

# Un point d’entrée associe une commande du terminal à une fonction Python.

# 

# Dans ce projet :

# 

# ```toml

# \[project.scripts]

# maintai-predict = "maintai.cli:main"

# ```

# 

# La commande `maintai-predict` appelle la fonction `main` du module `maintai.cli`.

# 

# Sous Windows, pip crée le lanceur `maintai-predict.exe` dans le dossier `Scripts` de l’environnement virtuel :

# 

# ```text

# .venv\\Scripts\\maintai-predict.exe

# ```

# 

# \## 5. Le rendu Git

# - **Lien de la pull request :** https://github.com/ZainaBelgas/Applications-intelligentes/pull/2
# - **État de la pull request :** Fusionnée dans main.
# - **Présence de dist/, build/ ou maintai.egg-info/ dans git status avant le commit :** Non.

#- **Tag de livraison prévu :** tp4, à créer après ce commit.


# \- \*\*Présence de `dist/`, `build/` ou `maintai.egg-info/` dans `git status` :\*\* À vérifier avant le commit.

# 

# Les dossiers `dist/`, `build/`, `maintai.egg-info/` et `.venv/` ne doivent pas être ajoutés au dépôt.

# 

# \## 6. Ce qui reste flou

# 

# Je souhaite approfondir la gestion des versions nécessaires pour réutiliser un modèle sauvegardé, notamment la différence entre des dépendances minimales pour installer un package et des versions exactes pour reproduire son environnement d’entraînement.

# 

# \## Conclusion

# 

# Ce TP4 m’a permis de transformer MaintAI en un package Python installable et utilisable depuis le terminal.

# 

# J’ai configuré les dépendances, déclaré la commande `maintai-predict` et vérifié le fonctionnement de l’installation éditable. J’ai ensuite construit un wheel et testé son installation dans un environnement indépendant.

# 

# Les 27 tests passent. La configuration du chemin du modèle et l’installation de scikit-learn 1.8.0 ont permis d’obtenir une prédiction sans avertissement de version dans le nouvel environnement.


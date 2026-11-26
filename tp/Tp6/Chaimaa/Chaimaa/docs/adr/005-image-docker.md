# ADR 005 : Modèle et données fournis à l'exécution, hors de l'image Docker

**Date :** 26/11/2026  
**Groupe :** G1  
**Étudiante :** Chaimaa EZZERAG  
**Classe :** 5IAD

## Contexte
MaintAI doit fonctionner de manière reproductible sur un PC ou un serveur sans préparation manuelle de l'environnement Python. Le code et ses dépendances doivent être empaquetés, tandis que le modèle, les données et les secrets doivent pouvoir être remplacés sans reconstruire une image qui les contiendrait.

Cette architecture soutient trois principes :
1. **Reproductibilité** : l'image est identique sur tous les environnements.
2. **Flexibilité** : modèle et données évoluent indépendamment du code.
3. **Sécurité** : les secrets ne sont jamais embarqués dans l'image.

## Options étudiées

### Option 1 : Inclure le modèle et les données dans l'image
**Avantages :**
- Image autonome : tous les artefacts nécessaires au déploiement sont inclus.
- Versions du code et du modèle regroupées et traçables.
- Pas de configuration manuelle des volumes sur l'hôte.

**Inconvénients :**
- Image volumineuse : augmente les temps de reconstruction, le stockage et le transfert réseau.
- Chaque mise à jour du modèle ou des données impose une reconstruction et une redistribution complète de l'image.
- Risque d'embarquer des données sensibles ou volumineuses dans un dépôt d'images publiques.
- Rend difficile les itérations de tuning du modèle sans redéploiement.

### Option 2 : Fournir le modèle et les données au lancement par des volumes (retenue)
**Avantages :**
- Image plus légère : réduction du stockage, du transfert réseau et des temps de reconstruction.
- Modèle et données remplaçables indépendamment du code : permet l'itération rapide.
- Montage en lecture seule : protège les données contre les modifications accidentelles.
- Pas de reconstruction pour actualiser les fichiers montés.
- Secrets fournis via fichier `.env`, jamais embarqués dans l'image.

**Inconvénients :**
- Fichiers à fournir manuellement sur l'hôte : nécessite une documentation claire.
- Chemins de volumes à configurer correctement : erreurs possibles de cheminage.
- Validation manuelle que les fichiers attendus existent sur l'hôte au démarrage.

## Décision
Nous retenons la **deuxième option** : volumes externes et secrets injectés au lancement.

### Architecture retenue

**Image Docker :**
- Contient Python 3.11 (image de base `python:3.11-slim`).
- Contient les dépendances Python figées dans `requirements-docker.txt`.
- Contient le code source (répertoires `maintai/` et `ui/`).
- N'inclut PAS le modèle, les données, MLflow, DVC, pytest, ni les secrets.

**Configuration Docker Compose :**
- Le modèle est monté de `./models` (hôte) vers `/app/models` (conteneur) en **lecture seule** (`ro`).
- Les données sont montées de `./data` (hôte) vers `/app/data` (conteneur) en **lecture seule** (`ro`).
- La clé API est injectée via `env_file: .env`, jamais copiée dans l'image.
- L'API écoute sur `0.0.0.0:8000` pour être accessible depuis l'extérieur du conteneur.
- L'interface Streamlit écoute sur `0.0.0.0:8501` et se connecte à l'API par le nom DNS `http://api:8000`.

**Règles du `.dockerignore` :**
Excluent du contexte de construction :
- `data/`, `models/`, `.env` : secrets et artefacts locaux.
- `mlflow.db`, `mlruns/`, `.dvc/` : suivi et versionnement non pertinents en exécution.
- `.pytest_cache/`, `tests/` : tests inutiles en exécution.
- `.venv/`, `__pycache__/`, `*.egg-info/` : caches Python.

## Conséquences

### Positives
- **Image plus légère** : environ 1,13 Go au lieu de 2+ Go avec modèle intégré.
- **Reconstruction rapide** : cache Docker efficace ; le code change fréquemment, les dépendances rarement.
- **Flexibilité du déploiement** : remplacer le modèle sans redéployer le code.
- **Sécurité** : les secrets ne transitent pas dans les couches Docker.
- **Conformité** : facilite le respect des politiques de gestion des modèles et des données.

### Contraintes
- **Validation manuelle** : l'exploitant doit vérifier que `./models` et `./data` existent et sont accessibles.
- **Documentation** : nécessite des instructions claires sur l'organisation des fichiers et des secrets.
- **Volume en lecture seule** : l'application ne peut pas modifier les fichiers montés (par conception, c'est un avantage).

## Alignement avec les bonnes pratiques
Cette décision s'aligne avec les recommandations officielles Docker :
- Réduire la taille des images en séparant les couches statiques (code) des artefacts dynamiques (modèle, données).
- Utiliser des volumes pour l'injection de configuration et de secrets au lancement.
- Maintenir la traçabilité entre versions du code et versions du modèle dans une gestion séparate (MLflow, registry, etc.).

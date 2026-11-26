# ADR 005 : Modèle et données fournis à l'exécution, hors de l'image Docker

Date : 26/11/2026 · Auteurs : À compléter avec les noms du groupe

## Contexte
MaintAI doit fonctionner de manière reproductible sur un PC ou un serveur sans préparation manuelle de l'environnement Python. Le code et ses dépendances doivent être empaquetés, tandis que le modèle, les données et les secrets doivent pouvoir être remplacés sans reconstruire une image qui les contiendrait.

## Options étudiées
1. **Inclure le modèle et les données dans l'image**
   - Avantages : image autonome et versions du code et du modèle regroupées.
   - Inconvénients : image plus volumineuse ; chaque mise à jour du modèle ou des données impose une reconstruction et une redistribution ; risque d'embarquer des données sensibles.
2. **Fournir le modèle et les données au lancement par des volumes**
   - Avantages : image plus légère ; modèle et données remplaçables indépendamment du code ; montage en lecture seule ; pas de reconstruction pour actualiser ces fichiers.
   - Inconvénients : fichiers à fournir sur l'hôte et chemins de volumes à configurer correctement.

## Décision
Nous retenons la deuxième option : l'image contient Python, les dépendances figées et le code ; le modèle est monté de `./models` vers `/app/models` en lecture seule, et les données de `./data` vers `/app/data` en lecture seule. La clé API est injectée au lancement avec `env_file: .env` et n'est jamais copiée dans l'image.

Le `.dockerignore` exclut `data/`, `models/`, `.env`, `mlflow.db`, `mlruns/` et `.dvc/` afin de ne pas intégrer données, modèles, secrets et artefacts locaux au contexte de construction.

## Conséquences
L'image est plus légère et peut être reconstruite à partir du Dockerfile ; modèle et données évoluent séparément. En contrepartie, le déploiement doit fournir les dossiers attendus sur l'hôte. Le fichier `.env` doit rester local et ne jamais être versionné.

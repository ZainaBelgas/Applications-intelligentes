# ADR 005 — Fournir le modèle MaintAI au démarrage

## Contexte

Le modèle de prédiction peut être réentraîné indépendamment du code de l’API. Il faut choisir comment fournir ses fichiers au conteneur.

## Options étudiées

- Inclure le modèle dans l’image simplifie le démarrage et associe une version du modèle à chaque image. Après un réentraînement, il faut reconstruire l’image.
- Monter le dossier `models/` permet de mettre le modèle à jour sans reconstruire l’image. Les fichiers du modèle doivent alors être disponibles sur la machine qui lance le conteneur.

## Décision

Nous montons `models/` dans `/app/models` en lecture seule. `.dockerignore` exclut le modèle, les données, `.env` et les fichiers locaux de suivi MLflow et DVC du contexte de build. La clé API est fournie au démarrage via `.env`.

## Conséquences

Après un réentraînement, nous remplaçons les fichiers du modèle et redémarrons l’API pour qu’elle les recharge. Le modèle doit être compatible avec la version de scikit-learn installée dans l’image.
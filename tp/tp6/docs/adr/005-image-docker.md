# ADR 005 : le contenu de l'image Docker de MaintAI

Date : 26/11/2026 · Auteurs : [ZAHR AMIRA]

## Contexte
MaintAI doit tourner sur un PC ou un serveur où personne ne prépare de .venv. Il faut décider ce que l'image contient, sachant que le modèle et les données changent sans nouveau code et que l'image peut être partagée.

## Décision 1 : le modèle est-il dans l'image ou fourni par un volume ?

### Options étudiées
1. **Modèle dans l'image** (`COPY models`).
   - Gains : une seule chose à livrer ; code et modèle figés ensemble ; retour en arrière en relançant l'ancienne image.
   - Pertes : chaque nouveau modèle impose un build et une livraison ; il faut avoir le modèle avant le build.
2. **Modèle par un volume** (`./models:/app/models:ro`).
   - Gains : changement de modèle sans reconstruire (redémarrage de l'API) ; la même image sert plusieurs modèles.
   - Pertes : l'image seule ne suffit pas ; il faut fournir le bon dossier, suivre la version du modèle et vérifier sa compatibilité avec scikit-learn 1.8.0.

### Décision
**Volume en lecture seule**, car le modèle change sans nouveau code. Le conteneur ne peut pas le modifier.

## Décision 2 : ce que .dockerignore laisse dehors

| Exclu | Pourquoi | Ce que l'inclure ferait gagner / perdre |
|---|---|---|
| `.env` | secret, fourni au lancement | gain : lancement plus simple ; perte : clé exposée avec l'image |
| `data/` | les données changent sans nouveau code | gain : image autonome ; perte : image plus lourde, données diffusées |
| `models/` | voir décision 1 | voir décision 1 |
| `mlflow.db`, `mlruns/` | inutiles pour servir | gain : historique embarqué ; perte : poids, historique exposé |
| `.dvc/` | inutile pour servir | gain : configuration DVC disponible ; perte : poids, copies de données |
| `.venv/` | environnement Windows, inutilisable sous Linux | aucun gain ; image plus lourde |
| caches, `dist/`, `build/`, `*.egg-info/` | fichiers régénérables | aucun gain utile |
| `.git/`, `tests/` | on ne versionne pas et on ne teste pas dans l'image | gain : tests possibles dans le conteneur ; perte : poids, historique exposé |

## Conséquences
- Plus facile : image réutilisable, changement de modèle sans build, clé hors de l'image.
- Plus difficile : il faut fournir `models/` et `.env` au lancement (et `data/` pour l'interface).
- À surveiller : `/health` doit indiquer `model_loaded: true` ; la version de scikit-learn doit rester celle de l'entraînement.
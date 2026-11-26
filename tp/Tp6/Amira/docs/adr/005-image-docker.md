# ADR 005 : le contenu de l'image Docker de MaintAI

Date : 26/11/2026 · Auteurs : [noms]

## Contexte
MaintAI doit tourner sur un PC ou un serveur où personne ne prépare de .venv. Il faut décider ce que l'image contient, sachant que le modèle et les données changent sans nouveau code et que l'image peut être partagée.

## Décision 1 : le modèle arrive-t-il dans l'image ou par un volume ?

### Options étudiées
1. **Modèle dans l'image** (`COPY models`).
   - Gains : une seule chose à livrer ; le code et le modèle sont figés ensemble ; revenir en arrière revient à relancer l'ancienne image ; aucun dossier à préparer sur le serveur.
   - Pertes : chaque nouveau modèle impose un build et une livraison ; une image par modèle ; il faut entraîner ou récupérer le modèle avant le build.
2. **Modèle par un volume** (`./models:/app/models:ro`).
   - Gains : on change de modèle sans reconstruire (un redémarrage de l'API suffit) ; la même image sert plusieurs modèles.
   - Pertes : l'image seule ne suffit pas ; le serveur doit avoir le bon dossier ; il faut suivre quelle version du modèle tourne et vérifier sa compatibilité avec scikit-learn 1.8.0.

### Décision
**Volume en lecture seule**, car le modèle change plus souvent que le code (séance 7). Le conteneur ne peut pas le modifier.

## Décision 2 : ce que .dockerignore laisse dehors

| Exclu | Pourquoi | Ce que l'inclure ferait gagner / perdre |
|---|---|---|
| `.env` | secret ; il arrive par `--env-file` ou `env_file` | gain : lancement plus court ; perte : la clé est lisible par quiconque a l'image |
| `data/` | les données changent sans nouveau code ; volume | gain : image autonome ; perte : image plus lourde, données diffusées avec elle |
| `models/` | voir décision 1 | voir décision 1 |
| `mlflow.db`, `mlruns/` | suivi des entraînements, inutile pour servir | gain : historique embarqué ; perte : poids, historique exposé |
| `.dvc/` | cache et configuration DVC, inutiles pour servir | gain : configuration DVC disponible ; perte : poids, copies des données |
| `.venv/` | environnement du PC (Windows), inutilisable sous Linux | aucun gain ; image beaucoup plus lourde |
| caches, `dist/`, `build/`, `*.egg-info/` | fichiers régénérables | aucun gain utile |
| `.git/`, `tests/` | on ne versionne pas et on ne teste pas dans l'image | gain : tests possibles dans le conteneur ; perte : poids, historique exposé |

Le Dockerfile ne copie que `requirements-docker.txt`, `maintai/` et `ui/`. `.dockerignore` est une seconde protection (par exemple si un `COPY . .` est ajouté un jour) et réduit ce qui est envoyé au build.

## Conséquences
- Plus facile : une image réutilisable, changement de modèle sans build, aucun secret dans l'image.
- Plus difficile : il faut fournir `models/` et `.env` au lancement (et `data/` pour l'interface).
- À surveiller : `/health` doit indiquer `model_loaded: true` ; la version de scikit-learn de l'image doit rester celle de l'entraînement.

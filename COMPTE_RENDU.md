# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** …  ·  **Membres :** …  ·  **Date :** 19/11/2026

> Les sorties ci-dessous viennent de l'exécution réelle du TP (Python 3.13, versions de `requirements.txt`).
> Les champs « Groupe », « Membres » et le lien de la pull request restent à compléter par vous.

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
5 failed, 27 passed, 2 warnings in 4.29s
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` : `log_run` était un squelette qui renvoyait `""` sans rien enregistrer, donc MLflow ne contenait aucun run (« aucun run MLflow : log_run n'a rien enregistré »). Avant `pip install -e .`, 2 tests de `tests/test_package.py` échouaient aussi (7 failed, 25 passed) : `version("maintai")` ne trouvait aucun package installé, et la commande `maintai-predict` n'était déclarée dans aucun point d'entrée.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant : nulle part (`pip show maintai` répond « Package(s) not found »). Le code n'était importable que parce qu'on lançait Python depuis le dossier du projet (`pythonpath = .` dans `pytest.ini`). Après : `pip show maintai` indique « Editable project location : …/TP5 » ; `maintai` est enregistré dans l'environnement comme un lien vers le dossier du projet, importable depuis n'importe quel dossier (`/home/claude/tp5/TP5/maintai/__init__.py`), et les modifications du code sont prises en compte sans réinstaller.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
        return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
32 passed, 4 warnings in 10.17s
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training »), sur la v1 des données (5000 lignes) :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --threshold 0.1` (mon essai) | 0.919 | 0.434 | 0.826 |

La baseline (toujours « pas de panne ») a une accuracy de 0.864 et un recall de 0 : l'accuracy seule est trompeuse, car seulement 13,6 % des relevés sont des pannes.

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

`--threshold 0.2` (régression logistique, C=1.0) : recall 0.838, soit environ 8 pannes sur 10 détectées contre 7,5 sur 10 au seuil 0,3. La précision reste à 0.543, donc un peu plus d'une alerte sur deux est justifiée. Le seuil 0,1 attrape plus de pannes (0.919) mais plus de la moitié des alertes seraient fausses (précision 0.434). Le modèle forêt n'apporte rien de mieux au même seuil. C'est un compromis : la forme de la courbe recall/précision dépend du coût réel d'une fausse alerte, que nous ne connaissons pas.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

`scikit-learn==1.8.0` (avec `numpy==2.4.4`, `pandas==3.0.2`, `mlflow==3.18.0`, etc.). Au TP4, `model.joblib` était sauvegardé sans savoir avec quelles versions de bibliothèques : le charger avec une autre version de scikit-learn peut donner des avertissements, des résultats faux ou une erreur. Avec MLflow, chaque modèle est livré avec ses versions exactes (`requirements.txt`, `conda.yaml`, `python_env.yaml`), donc on sait quel environnement recréer pour le recharger. Il est aussi enregistré au format `.skops`, plus sûr que le pickle.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans `mlflow.db` (base SQLite : paramètres, métriques) et dans le dossier `mlruns/` (artefacts : modèle, `requirements.txt`…), à la racine du projet. Non : ils sont dans `.gitignore`. Ce sont des fichiers générés, volumineux, qui changent à chaque entraînement et propres à chaque machine ; Git garde le code, pas les résultats d'exécution.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: b7fec4274774842dc1f48202c6013490
  size: 121814
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Elles sont identiques : `b7fec4274774842dc1f48202c6013490` (et `md5sum data/sensors.csv` donne la même valeur). `file_md5` dans `tracking.py` calcule la même empreinte que DVC. Chaque run MLflow est donc relié à la version exacte des données avec lesquelles il a été entraîné.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Git n'est pas fait pour les gros fichiers de données : chaque version resterait dans l'historique et alourdirait le dépôt. Le petit fichier `.dvc` (quelques lignes de texte) ne contient que l'empreinte et la taille ; Git versionne ce « pointeur », et DVC range le vrai fichier dans son cache et son stockage. Quand on change de commit Git, `dvc checkout` retrouve les données qui correspondent au pointeur.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data/sensors.csv.dvc:
	changed outs:
		modified:           data/sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | 22c9f8b | b7fec427 | 5000 |
| v2 | 4589c41 | 31ef5ebb | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après retour à la v1 : 5001 lignes dans le fichier, soit 5000 relevés plus l'en-tête (`wc -l`), et le `.dvc` affiche le md5 `b7fec427…`. Après retour à la v2 : 8001 lignes (8000 relevés plus l'en-tête).

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC retrouve le fichier dans le stockage distant (`1 file fetched and 1 file added`) et recrée `data/sensors.csv` (8001 lignes, la v2 indiquée par le `.dvc` courant). Les données ne sont donc pas perdues tant qu'elles ont été envoyées avec `dvc push`.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages (`python -m maintai.train`, seuil 0,3, C=1.0) :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | b7fec427 | 4000 | 0.750 | 0.622 |
| v2 | 31ef5ebb | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le recall baisse un peu (0.750 → 0.741) et la précision monte un peu (0.622 → 0.650) : c'est un mélange, pas un progrès net. Surtout, les deux runs ne sont pas mesurés sur le même jeu de test : chaque version a son propre jeu de test (1000 lignes contre 1600) et un taux de panne différent (13,6 % contre 12,8 %). Un écart de quelques millièmes peut venir des données plutôt que du modèle. On ne compare proprement que des runs qui ont le même `data_md5` ; c'est précisément ce que ce paramètre permet de vérifier.

## 5. Décision : l'ADR 004

Voir `docs/adr/004-choix-du-modele.md` : régression logistique (C=1.0), seuil d'alerte 0,2. Run `3f6c5a6337734f82897e292f7efae242`, `data_md5` = `b7fec4274774842dc1f48202c6013490` (v1). Confirmé sur la v2 (run `1cef043e253a4c07bd6a5f3232accb28` : recall 0.824, precision 0.567).

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code (et les petits fichiers texte, dont les `.dvc`). DVC versionne les données volumineuses : Git garde un pointeur (md5), DVC garde le fichier dans son cache et son stockage. MLflow ne versionne pas, il enregistre les entraînements : paramètres, version des données (`data_md5`), métriques et modèle avec ses dépendances, pour les comparer.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   `--local` écrit la configuration dans `.dvc/config.local`, fichier non versionné par Git : le chemin du stockage est propre à chaque machine (ici un dossier local) et ne doit pas être imposé aux autres. Pour partager, il faut un stockage accessible à tout le groupe (dossier réseau, S3, Google Drive, serveur SSH…) déclaré comme remote dans `.dvc/config` (versionné), puis chacun fait `dvc pull`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code (package `maintai`, dans Git, installable avec `pip install -e .` ou le wheel), les dépendances aux bonnes versions (`requirements.txt`, et pour chaque modèle le `requirements.txt` stocké par MLflow), et le modèle entraîné (`model.joblib` dans `models/`, ainsi que dans MLflow dans `mlruns/`, relié au run et aux données par `data_md5`). Les données, elles, sont suivies par DVC.

## 7. Le rendu Git

- Lien de la pull request : … (à créer par vous : je n'ai pas accès à votre dépôt GitHub)
- Le tag `tp5` existe sur GitHub : non (à créer avec `git tag tp5 && git push --tags`)
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non (`mlflow.db`, `mlruns/` et `data/*.csv` sont dans `.gitignore`, et DVC ignore `.dvc/cache`)

## 8. Ce qui reste flou

Le seuil de 0,2 est un compromis choisi sans connaître le coût réel d'une fausse alerte par rapport à une panne manquée ; il faudrait ce coût pour optimiser le seuil plutôt que le deviner. De plus, les métriques viennent d'un seul découpage test sur des données synthétiques.

# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Nom :** ZAHR AMIRA  ·  **Groupe :** G1  ·  **Date :** 19/11/2026 HEURE:12:04

> Les sorties viennent d'exécutions sous Windows (Python 3.14, versions de `requirements.txt`).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
5 failed, 27 passed, 2 warnings in 4.29s
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` : `log_run` était un squelette qui renvoyait `""` sans rien enregistrer, donc MLflow ne contenait aucun run (« aucun run MLflow : log_run n'a rien enregistré »). Avant `pip install -e .`, 2 tests de `tests/test_package.py` échouaient aussi (7 failed, 25 passed) : `version("maintai")` ne trouvait aucun package installé, et la commande `maintai-predict` n'était déclarée dans aucun point d'entrée.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant : nulle part (`pip show maintai` répond « Package(s) not found »). Le code n'était importable que parce qu'on lançait Python depuis le dossier du projet (`pythonpath = .` dans `pytest.ini`). Après `pip install -e .` (« Successfully installed maintai-0.3.0 »), `pip show maintai` indique « Editable project location : C:\Users\user\Downloads\TP5-rendu\TP5 » ; `maintai` est enregistré dans l'environnement comme un lien vers le dossier du projet, importable depuis n'importe quel dossier, et les modifications du code sont prises en compte sans réinstaller.

## 2. Sprint 1 : MLflow

La fonction `log_run` (`maintai/tracking.py`) :

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
32 passed, 6 warnings in 26.74s
```

Vos 5 runs, relevés dans `mlflow ui` (mode « Model training »), sur la v1 des données (5000 lignes, `data_md5` = `73e0b7cb…`) :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --threshold 0.1` (mon essai) | 0.919 | 0.434 | 0.826 |

Identifiants de run : `2ee71e47…` (défaut), `e3aeb465…` (C=0.01), `e5dedf3d…` (seuil 0.2), `e14caac2…` (forêt). Le run en seuil 0.1 s'appelle `intrigued-shark-950` dans MLflow.

La baseline (toujours « pas de panne ») a une accuracy de 0.864 et un recall de 0 : l'accuracy seule est trompeuse, car seulement 13,6 % des relevés sont des pannes.

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

`--threshold 0.2` (régression logistique, C=1.0) : recall 0.838, soit environ 8 pannes sur 10 détectées contre 7,5 sur 10 au seuil 0,3. La précision reste à 0.543, donc un peu plus d'une alerte sur deux est justifiée. Le seuil 0,1 attrape plus de pannes (0.919) mais plus de la moitié des alertes seraient fausses (précision 0.434). Le modèle forêt n'apporte rien de mieux au même seuil. C'est un compromis : la forme de la courbe recall/précision dépend du coût réel d'une fausse alerte, que nous ne connaissons pas.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

`scikit-learn==1.8.0` (avec `numpy==2.4.4`, `pandas==3.0.2`, `mlflow==3.18.0`, etc.). Au TP4, `model.joblib` était sauvegardé sans savoir avec quelles versions de bibliothèques : le charger avec une autre version de scikit-learn peut donner des avertissements, des résultats faux ou une erreur. Avec MLflow, chaque modèle est livré avec ses versions exactes (`requirements.txt`, `conda.yaml`, `python_env.yaml`), donc on sait quel environnement recréer pour le recharger. Il est aussi enregistré au format `.skops`, plus sûr que le pickle.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans `mlflow.db` (base SQLite : paramètres, métriques) et dans le dossier `mlruns/` (tous deux dans `TP5-rendu\TP5`) (artefacts : modèle, `requirements.txt`…), à la racine du projet. Non : ils sont dans `.gitignore`. Ce sont des fichiers générés, volumineux, qui changent à chaque entraînement et propres à chaque machine ; Git garde le code, pas les résultats d'exécution.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Elles sont identiques : `73e0b7cb3c6f795c70c3ddf970b99c15`. Remarque : cette empreinte diffère de celle d'une génération sous Linux (`b7fec427…`, 121814 octets) car sous Windows `pandas` écrit les fins de ligne en `\r\n` : le contenu est le même, mais pas les octets (126815 − 121814 = 5001 octets, un par ligne). `file_md5` dans `tracking.py` calcule la même empreinte que DVC. Chaque run MLflow est donc relié à la version exacte des données avec lesquelles il a été entraîné.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Git n'est pas fait pour les gros fichiers de données : chaque version resterait dans l'historique et alourdirait le dépôt. Le petit fichier `.dvc` (quelques lignes de texte) ne contient que l'empreinte et la taille ; Git versionne ce « pointeur », et DVC range le vrai fichier dans son cache et son stockage. Quand on change de commit Git, `dvc checkout` retrouve les données qui correspondent au pointeur.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
        changed outs:
                modified:   data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | 0052f17 | 73e0b7cb | 5000 |
| v2 | 6da6164 | 93fdeef2 | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 0052f17 -- data/sensors.csv.dvc` et `dvc checkout` : `(Get-Content data\sensors.csv).Count` affiche 5001, soit 5000 relevés plus la ligne d'en-tête. Après `git checkout 6da6164 -- data/sensors.csv.dvc` et `dvc checkout` : 8001 lignes (8000 relevés plus l'en-tête).

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

`dvc pull` répond « 1 file fetched and 1 file added » : DVC retrouve le fichier dans le stockage (`C:/dvc-stockage`) et recrée `data/sensors.csv` (8001 lignes, la v2 indiquée par le `.dvc` courant). Les données ne sont pas perdues tant qu'elles ont été envoyées avec `dvc push`.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages (`python -m maintai.train`, seuil 0,3, C=1.0) :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | 73e0b7cb | 4000 | 0.750 | 0.622 |
| v2 | 93fdeef2 | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le recall baisse un peu (0.750 → 0.741) et la précision monte un peu (0.622 → 0.650) : c'est un mélange, pas un progrès net. Surtout, les deux runs ne sont pas mesurés sur le même jeu de test : chaque version a son propre jeu de test (1000 lignes contre 1600) et un taux de panne différent (13,6 % contre 12,8 %). Un écart de quelques millièmes peut venir des données plutôt que du modèle. On ne compare proprement que des runs qui ont le même `data_md5` ; c'est précisément ce que ce paramètre permet de vérifier.

## 5. Décision : l'ADR 004

**Modèle retenu : régression logistique (`LogisticRegression`) avec `C=10` et un seuil d'alerte de `0.15`.** C'est le meilleur essai de la recherche sur grille (partie 7, essai n°22) : recall 0.859, precision 0.507, accuracy 0.875.

- **Données utilisées :** v2 (8000 relevés, commit `6da6164`), `data_md5` = `93fdeef2cac1893c4f720c16457eea75`.
- **Identifiant du run :** `20a8adfb6db74272a90f102efad4ab1c` (run `bustling-flea-164` dans MLflow : réentraînement du meilleur réglage de la grille, `C=10`, `threshold=0.15`, modèle sauvegardé dans `models/`).
- **Pourquoi ce modèle :** une panne manquée coûte plus cher qu'une fausse alerte, donc on choisit le recall le plus élevé parmi les essais dont la précision reste au moins égale à 0,5. Les 25 essais comparés sont dans la partie 7.
- **Avant la grille** (5 runs sur la v1, partie 2), j'avais retenu `--threshold 0.2` avec C=1.0 (run `e5dedf3d034047b3bae46cb2c7206607`, `data_md5` = `73e0b7cb3c6f795c70c3ddf970b99c15`, recall 0.838, precision 0.543). La grille, plus complète, affine ce choix : le seuil 0.15 détecte davantage de pannes avec une précision encore au-dessus de 0,5.
- **Limite :** la précision de 0.507 est tout juste au-dessus du seuil de 0,5. Si les fausses alertes coûtent cher, le seuil 0.20 (recall 0.824, precision 0.567) est une alternative plus prudente.

Le raisonnement détaillé est aussi dans `docs/adr/004-choix-du-modele.md`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code (et les petits fichiers texte, dont les `.dvc`). DVC versionne les données volumineuses : Git garde un pointeur (md5), DVC garde le fichier dans son cache et son stockage. MLflow ne versionne pas, il enregistre les entraînements : paramètres, version des données (`data_md5`), métriques et modèle avec ses dépendances, pour les comparer.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   `--local` écrit la configuration dans `.dvc/config.local`, fichier non versionné par Git : le chemin du stockage est propre à chaque machine (ici un dossier local) et ne doit pas être imposé aux autres. Pour partager, il faut un stockage accessible à tout le groupe (dossier réseau, S3, Google Drive, serveur SSH…) déclaré comme remote dans `.dvc/config` (versionné), puis chacun fait `dvc pull`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le code (package `maintai`, dans Git, installable avec `pip install -e .` ou le wheel), les dépendances aux bonnes versions (`requirements.txt`, et pour chaque modèle le `requirements.txt` stocké par MLflow), et le modèle entraîné (`model.joblib` dans `models/`, ainsi que dans MLflow dans `mlruns/`, relié au run et aux données par `data_md5`). Les données, elles, sont suivies par DVC.

## 7. Recherche sur grille (grid search)

Consigne du prof : lancer une boucle de 25 entraînements, comparer les résultats et donner le modèle le plus performant.

**Méthode.** Le script `maintai/grid.py` (`python -m maintai.grid`) entraîne 25 régressions logistiques : 5 valeurs de `C` (0.001, 0.01, 0.1, 1, 10) × 5 seuils d'alerte (0.10, 0.15, 0.20, 0.25, 0.30). Chaque essai est un run MLflow (`data_md5` = `93fdeef2…`, v2 des données, 6400 lignes d'entraînement, 1600 de test). Les résultats complets sont dans `grid_results.csv`.

**Critère de choix.** Une panne manquée coûte plus cher qu'une fausse alerte : on retient le **recall le plus élevé parmi les essais dont la précision reste au moins égale à 0,5** (au moins une alerte sur deux est justifiée). En cas d'égalité, on prend la meilleure précision.

Recall :

| C \ seuil | 0.10 | 0.15 | 0.20 | 0.25 | 0.30 |
|---|---|---|---|---|---|
| 0.001 | 1.000 | 0.917 | 0.737 | 0.517 | 0.400 |
| 0.01 | 0.966 | 0.893 | 0.829 | 0.761 | 0.698 |
| 0.1 | 0.922 | 0.863 | 0.829 | 0.790 | 0.732 |
| 1 | 0.907 | 0.859 | 0.824 | 0.780 | 0.741 |
| 10 | 0.902 | 0.859 | 0.824 | 0.780 | 0.741 |

Précision :

| C \ seuil | 0.10 | 0.15 | 0.20 | 0.25 | 0.30 |
|---|---|---|---|---|---|
| 0.001 | 0.253 | 0.437 | 0.616 | 0.774 | 0.872 |
| 0.01 | 0.384 | 0.470 | 0.547 | 0.612 | 0.688 |
| 0.1 | 0.445 | 0.496 | 0.559 | 0.625 | 0.652 |
| 1 | 0.458 | 0.506 | 0.567 | 0.620 | 0.650 |
| 10 | 0.457 | 0.507 | 0.567 | 0.620 | 0.650 |

**Comparaison.**
- Le **seuil** change tout : de 0.30 à 0.10, le recall monte (par exemple 0.741 → 0.902 pour C=10) mais la précision chute (0.650 → 0.457). C'est le compromis entre pannes manquées et fausses alertes.
- Le **`C`** compte peu dès que `C ≥ 0.1` : les essais C=1 et C=10 donnent exactement les mêmes résultats à 3 décimales près. Un `C` trop petit (0.001) régularise trop : à seuil 0.30, le recall tombe à 0.400.
- Un seuil de 0.10 avec C=0.001 détecte 100 % des pannes (recall 1.000) mais seulement 25 % des alertes sont justifiées (précision 0.253) : inutilisable.
- Le meilleur F2 (score qui privilégie le recall) est 0.759, pour C=0.1 et seuil 0.10 ; mais sa précision (0.445) est sous notre limite de 0,5.

**Modèle le plus performant (selon notre critère) : essai 22, régression logistique avec `C=10` et seuil `0.15` : recall 0.859, precision 0.507, accuracy 0.875.** L'essai 17 (C=1, même seuil) est quasiment identique (0.859 / 0.506) ; la différence est négligeable. La précision de 0.507 est tout juste au-dessus de la limite de 0,5 : si l'on veut moins de fausses alertes, le seuil 0.20 (recall 0.824, précision 0.567) est une alternative proche. Le meilleur modèle est sauvegardé dans `models/` à la fin du script.

## 8. Le rendu Git

- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non. `git status` affichait « nothing to commit, working tree clean » : `mlflow.db`, `mlruns/` et `data/*.csv` sont dans `.gitignore`, et DVC ignore `.dvc/cache`.

## 9. Ce qui reste flou

Le seuil de 0,2 est un compromis choisi sans connaître le coût réel d'une fausse alerte par rapport à une panne manquée ; il faudrait ce coût pour optimiser le seuil plutôt que le deviner. De plus, les métriques viennent d'un seul découpage test sur des données synthétiques.

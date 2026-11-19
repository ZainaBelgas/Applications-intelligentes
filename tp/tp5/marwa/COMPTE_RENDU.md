# Compte rendu — TP5 MaintAI

## Suivi des entraînements avec MLflow, versionnement des données avec DVC et recherche sur grille

- **Étudiante :** Marwa Elomari Alaoui
- **Groupe :** G1
- **Date :** 19/11/2026
- **heure :** 12:15
- **Environnement :** Windows PowerShell, Python 3.13.3, environnement virtuel `.venv`, pytest 9.1.1, DVC 3.67.1 et MLflow 3.18.0

---

## 1. Objectifs du TP

Le TP5 prolonge le projet MaintAI, qui prédit les pannes à partir de relevés synthétiques de capteurs. Le travail réalisé porte sur quatre objectifs :

1. Installer le projet et vérifier son fonctionnement avec `pytest`.
2. Enregistrer et comparer les entraînements avec MLflow : paramètres, métriques, empreinte des données et modèle.
3. Versionner le jeu de données avec DVC, puis vérifier les pointeurs des différentes versions.
4. Évaluer 25 réglages avec une recherche sur grille, exporter les résultats et choisir un réglage adapté au coût élevé des pannes manquées.

---

## 2. Installation et tests

### 2.1 Préparation de l’environnement

Depuis le dossier du projet, l’environnement virtuel a été activé sous PowerShell, puis les dépendances, le package et DVC ont été installés :

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
pip install --no-cache-dir dvc
```

L’installation en mode éditable (`pip install -e .`) rend le package `maintai` disponible dans l’environnement tout en utilisant directement le code du dossier du projet. Les modifications du code sont ainsi prises en compte sans réinstallation.

### 2.2 Évolution des tests

Au premier lancement, le résultat était **5 échecs, 27 réussites et 2 avertissements**. Les tests de suivi échouaient parce que `log_run` n’enregistrait pas encore les expériences dans MLflow. Avant l’installation éditable du package, deux tests du package échouaient également, car les métadonnées et le point d’entrée de la commande n’étaient pas installés dans l’environnement.

Après l’implémentation du suivi MLflow et l’installation éditable, la suite complète a réussi. Le contrôle final effectué pour ce compte rendu confirme le résultat :

```text
32 passed, 4 warnings in 227.94s
```

Les tests couvrent l’API, la CLI, le client, les données, le package, la sécurité, le suivi MLflow, l’entraînement et l’interface. Les quatre avertissements proviennent de dépendances (Starlette, SQLAlchemy et MLflow) ; aucun test n’a échoué.

---

## 3. Suivi des entraînements avec MLflow

### 3.1 Enregistrement d’un run

La fonction `log_run` de `maintai/tracking.py` enregistre chaque entraînement dans l’expérience `maintai`. Pour chaque run, elle journalise :

- les paramètres, dont le modèle, la valeur de `C` et le seuil ;
- `data_md5`, l’empreinte MD5 du fichier de données utilisé ;
- les métriques `accuracy`, `recall` et `precision` ;
- le modèle et son exemple d’entrée.

La commande d’entraînement et le lancement de l’interface sont :

```powershell
python -m maintai.train
mlflow ui
```

L’interface est accessible à l’adresse `http://localhost:5000`. Les captures réalisées montrent l’expérience `maintai`, les paramètres et métriques des runs, les artefacts du modèle et une liste de **39 runs correspondants** aux filtres affichés. Un run ouvert dans l’interface a notamment l’identifiant `aadce660f2794ee5a8343faf608d92e4` ; les captures permettent aussi d’inspecter les runs nommés `wistful-kite-283` et `adaptable-shrew-867`.

Les fichiers locaux `mlflow.db` et `mlruns/` contiennent les informations et artefacts MLflow. Ils sont générés pendant l’exécution et ne sont pas destinés à être versionnés dans Git.

### 3.2 Comparaison de quelques entraînements

Sur la v1 (5 000 relevés), les essais consignés dans MLflow donnent notamment :

| Réglage | Recall | Précision | Accuracy |
|---|---:|---:|---:|
| Régression logistique, `C=1.0`, seuil `0.3` | 0.750 | 0.622 | 0.904 |
| Régression logistique, `C=0.01`, seuil `0.3` | 0.691 | 0.653 | 0.908 |
| Régression logistique, `C=1.0`, seuil `0.2` | 0.838 | 0.543 | 0.882 |
| Forêt aléatoire, seuil `0.3` | 0.728 | 0.562 | 0.886 |
| Régression logistique, `C=1.0`, seuil `0.1` | 0.919 | 0.434 | 0.826 |

La baseline qui prédit toujours « pas de panne » obtient une accuracy de 0.864, mais un recall de 0. Une accuracy élevée ne suffit donc pas : elle masque le fait que la baseline ne détecte aucune panne.

Au seuil de 0.2, le rappel augmente par rapport au seuil 0.3, avec une baisse de précision. Le seuil 0.1 détecte encore davantage de pannes, mais génère beaucoup de fausses alertes. Ces premiers essais ont motivé la recherche d’un compromis entre rappel et précision.

MLflow conserve aussi les dépendances associées au modèle dans ses artefacts (par exemple `model/requirements.txt`). Cela permet de connaître les versions de bibliothèques nécessaires pour recharger le modèle, contrairement à un fichier de modèle isolé.

---

## 4. Versionnement des données avec DVC

### 4.1 Configuration et suivi du fichier

Le fichier CSV est suivi par DVC au moyen du petit pointeur `data/sensors.csv.dvc`. Le fichier de données lui-même est stocké dans le cache et le remote DVC, et non dans Git.

Configuration du remote local, ajout du jeu de données et envoi vers le stockage :

```powershell
python -m dvc remote add --local -f -d stockage C:/dvc-stockage
python -m dvc add data/sensors.csv
git add data/sensors.csv.dvc
git commit -m "Suivi du jeu de données avec DVC"
python -m dvc push
python -m dvc status
```

Le remote est ajouté avec `--local` parce que son chemin dépend de la machine. Sa configuration locale est conservée dans `.dvc/config.local` et n’est pas partagée par Git.

### 4.2 Historique et empreintes des données

L’historique Git contient plusieurs états du pointeur DVC. Il faut distinguer le premier jeu v2 enregistré de l’état v2 final :

| État | Commit du pointeur DVC | Relevés | Empreinte MD5 | Taille |
|---|---|---:|---|---:|
| v1 | `22c9f8b` | 5 000 | `b7fec4274774842dc1f48202c6013490` | 121 814 octets |
| v2, premier état enregistré | `4589c41` | 8 000 | `31ef5ebb63ef2331a31dfe009ef8796a` | 194 833 octets |
| v2, état final courant | `9f4e6e8` | 8 000 | `93fdeef2cac1893c4f720c16457eea75` | 202 834 octets |

Le pointeur actuellement présent dans `data/sensors.csv.dvc` est celui de l’état final v2 (`93fdeef2...`). Le fichier courant contient **8 001 lignes**, soit 8 000 relevés et une ligne d’en-tête. Cette empreinte est également celle enregistrée par le run d’entraînement correspondant à la v2.

La génération de la v2 a été effectuée ainsi :

```powershell
python -m maintai.dataset --n 8000 --seed 7
python -m dvc status
python -m dvc add data/sensors.csv
git add data/sensors.csv.dvc
git commit -m "Données v2"
python -m dvc push
```

Après la génération d’une nouvelle version, `dvc status` signale la sortie modifiée tant que le pointeur n’a pas été mis à jour avec `dvc add`. Une fois le pointeur commité et les données poussées, `dvc checkout` ou `dvc pull` permet de replacer/récupérer le fichier associé au pointeur courant.

### 4.3 Test de bascule entre les versions

Les pointeurs v1 et v2 ont été retrouvés dans l’historique Git. Lors des essais de restauration, l’objet correspondant à l’ancien pointeur v1 n’était pas disponible dans le cache ou le remote DVC utilisé. La bascule vers cet objet ne pouvait donc pas être validée par une restauration DVC complète. Un jeu de 5 000 relevés a été regénéré localement avec `--n 5000 --seed 42` pour contrôler la forme et le nombre de lignes, puis les données ont été réalignées sur le pointeur final v2.

Le jeu actuellement présent est donc la v2 finale. Son empreinte vérifiée est `93fdeef2cac1893c4f720c16457eea75`. Le contrôle final avec `dvc status` indique `Data and pipelines are up to date.` Le remote local configuré est `stockage` (`C:/dvc-stockage`). Il ne faut pas confondre cette vérification avec une restauration réussie de l’objet v1 manquant.

### 4.4 Pourquoi Git et DVC sont complémentaires

- **Git** versionne le code et les petits fichiers texte, dont le pointeur `.dvc`.
- **DVC** versionne et stocke les jeux de données volumineux ; le pointeur Git relie chaque commit à l’empreinte du contenu attendu.
- **MLflow** suit les expériences et associe paramètres, métriques, empreinte des données et artefacts du modèle.

Le CSV est ignoré par Git, alors que le pointeur DVC est suivi. Les fichiers `mlflow.db`, `mlruns/`, le cache DVC et les fichiers de configuration locale sont des fichiers générés ou spécifiques à la machine.

---

## 5. Comparaison des résultats sur v1 et v2

Un run de base sur la v2, avec le seuil 0.3, donne :

| Version | MD5 (début) | `n_train` | `n_test` | Recall | Précision | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| v1 | `b7fec427` | 4 000 | 1 000 | 0.750 | 0.622 | 0.904 |
| v2 finale | `93fdeef2` | 6 400 | 1 600 | 0.741 | 0.650 | 0.916 |

Ces résultats ne permettent pas de conclure directement que l’un des modèles est meilleur. Les données, leur volume, le taux de panne et les partitions d’entraînement/test diffèrent. Pour une comparaison rigoureuse, il faudrait mesurer les modèles sur un même jeu de test indépendant et documenter les mêmes conditions d’évaluation. `data_md5` permet au minimum d’identifier la version exacte utilisée par chaque run.

---

## 6. Recherche sur grille

### 6.1 Méthode

Le module `maintai.grid` teste les combinaisons de cinq valeurs de régularisation `C` et cinq seuils d’alerte, soit **25 entraînements** :

- `C` : `0.001`, `0.01`, `0.1`, `1.0`, `10.0` ;
- seuil : `0.10`, `0.15`, `0.20`, `0.25`, `0.30`.

Pour chaque combinaison, le script calcule le recall, la précision, l’accuracy et le score F2, puis exporte le tableau dans `grid_results.csv`. Le score F2 donne davantage de poids au recall. Le critère de sélection final est le **recall maximal parmi les résultats dont la précision est au moins 0.50**. Le modèle correspondant est réentraîné et sauvegardé dans `models/`.

Commande exécutée :

```powershell
python -m maintai.grid 2>$null
```

### 6.2 Résultats des 25 essais

| Essai | `C` | Seuil | Recall | Précision | Accuracy | F2 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.001 | 0.10 | 1.000 | 0.253 | 0.623 | 0.629 |
| 2 | 0.001 | 0.15 | 0.917 | 0.437 | 0.838 | 0.752 |
| 3 | 0.001 | 0.20 | 0.737 | 0.616 | 0.907 | 0.709 |
| 4 | 0.001 | 0.25 | 0.517 | 0.774 | 0.919 | 0.554 |
| 5 | 0.001 | 0.30 | 0.400 | 0.872 | 0.916 | 0.449 |
| 6 | 0.01 | 0.10 | 0.966 | 0.384 | 0.797 | 0.741 |
| 7 | 0.01 | 0.15 | 0.893 | 0.470 | 0.858 | 0.757 |
| 8 | 0.01 | 0.20 | 0.829 | 0.547 | 0.890 | 0.752 |
| 9 | 0.01 | 0.25 | 0.761 | 0.612 | 0.907 | 0.726 |
| 10 | 0.01 | 0.30 | 0.698 | 0.688 | 0.921 | 0.696 |
| 11 | 0.1 | 0.10 | 0.922 | 0.445 | 0.843 | 0.759 |
| 12 | 0.1 | 0.15 | 0.863 | 0.496 | 0.870 | 0.752 |
| 13 | 0.1 | 0.20 | 0.829 | 0.559 | 0.894 | 0.756 |
| 14 | 0.1 | 0.25 | 0.790 | 0.625 | 0.912 | 0.750 |
| 15 | 0.1 | 0.30 | 0.732 | 0.652 | 0.916 | 0.714 |
| 16 | 1.0 | 0.10 | 0.907 | 0.458 | 0.851 | 0.758 |
| 17 | 1.0 | 0.15 | 0.859 | 0.506 | 0.874 | 0.754 |
| 18 | 1.0 | 0.20 | 0.824 | 0.567 | 0.897 | 0.756 |
| 19 | 1.0 | 0.25 | 0.780 | 0.620 | 0.911 | 0.742 |
| 20 | 1.0 | 0.30 | 0.741 | 0.650 | 0.916 | 0.721 |
| 21 | 10.0 | 0.10 | 0.902 | 0.457 | 0.850 | 0.755 |
| **22** | **10.0** | **0.15** | **0.859** | **0.507** | **0.875** | **0.754** |
| 23 | 10.0 | 0.20 | 0.824 | 0.567 | 0.897 | 0.756 |
| 24 | 10.0 | 0.25 | 0.780 | 0.620 | 0.911 | 0.742 |
| 25 | 10.0 | 0.30 | 0.741 | 0.650 | 0.916 | 0.721 |

### 6.3 Réglage retenu

Le meilleur réglage selon le critère annoncé est **l’essai 22** :

- `C = 10.0` ;
- seuil `= 0.15` ;
- recall `= 0.859` ;
- précision `= 0.507` ;
- accuracy `= 0.875` ;
- F2 `= 0.754`.

L’essai 17 a le même recall à l’arrondi, mais une précision légèrement inférieure (0.506 contre 0.507). Le choix de l’essai 22 respecte donc le critère de rappel maximal avec précision minimale de 0.50, puis le départage par précision. Le seuil de 0.10 atteint un recall supérieur, mais sa précision (0.253 pour `C=0.001`) est trop faible pour respecter la contrainte.

Ce résultat est une recommandation issue des données et du critère du TP, pas une validation métier définitive. Le choix du seuil devra être confirmé avec le coût réel des fausses alertes et des pannes manquées.

---

## 7. Conclusion et livrables

Le TP a permis de relier les trois niveaux de traçabilité :

1. le code et les pointeurs de données sont suivis dans Git ;
2. les contenus des jeux de données sont gérés par DVC ;
3. les entraînements et leurs modèles sont comparables dans MLflow.

Le grid search produit 25 résultats dans `grid_results.csv` et retient `C=10.0`, seuil `0.15`, sous la contrainte de précision minimale. Le fichier `data/sensors.csv.dvc` courant pointe vers la v2 finale de 8 000 relevés (`93fdeef2...`). L’objet de données correspondant au pointeur v1 n’était pas disponible lors de l’essai de restauration ; cette limite est indiquée afin de ne pas présenter la bascule v1 comme une restauration DVC réussie.

### Vérifications finales et état du rendu Git

La suite de tests passe (**32 tests réussis, 4 avertissements**) et DVC confirme que les données courantes correspondent à leur pointeur. Le contrôle de Git montre toutefois que le rendu n’est pas encore commité : `git status --short` indique les deux fichiers non suivis suivants :

```text
?? grid_results.csv
?? maintai/grid.py
```

Ces deux fichiers sont les livrables de la recherche sur grille et doivent être ajoutés au commit du TP avec le compte rendu et l’ADR. Les données CSV, le cache DVC, les fichiers MLflow et les modèles générés ne doivent pas être ajoutés à Git. Le tag local `tp5` n’existe pas et aucun remote Git n’est configuré dans ce dépôt ; par conséquent, la Pull Request et la publication du tag sur GitHub ne peuvent pas être confirmées ni effectuées depuis l’état actuel du dépôt.

---

## 8. Réponses aux questions de compréhension

### Quelle différence entre Git, DVC et MLflow ?

Git versionne principalement le code et les fichiers texte. DVC gère les versions des données volumineuses, auxquelles Git fait référence par des pointeurs. MLflow suit les exécutions d’entraînement : paramètres, empreinte des données, métriques et artefacts des modèles.

### Pourquoi le remote DVC est-il configuré avec `--local` ?

Le chemin `C:/dvc-stockage` dépend de l’ordinateur utilisé. La configuration locale évite de publier dans Git un chemin qui ne fonctionnerait pas sur les autres postes. Pour partager les données, le groupe devrait utiliser un remote commun accessible à tous (serveur, stockage réseau ou stockage objet) et chacun pourrait récupérer les contenus avec `dvc pull`.

### Pourquoi ne pas comparer naïvement les métriques v1 et v2 ?

Les runs portent sur des jeux de données et des partitions test différents. Une variation de métrique peut provenir des données, du taux de panne ou du découpage, pas uniquement du modèle. La comparaison doit utiliser un protocole d’évaluation commun.

### Quels éléments faut-il pour livrer un modèle ?

Il faut le code, les dépendances compatibles et le modèle entraîné. Ici, le package et ses dépendances sont décrits dans le projet, MLflow archive les dépendances avec chaque artefact de modèle, et le modèle final est généré dans `models/`. Les données sont suivies séparément avec DVC.

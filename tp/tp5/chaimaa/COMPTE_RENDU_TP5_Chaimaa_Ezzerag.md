# Compte rendu TP5 MaintAI

COMPTE RENDU TP5

MaintAI
Suivi des entraînements
et recherche sur grille

Chaimaa Ezzerag
19 novembre 2026 · 12 h 15

### Objectif et résultat principal

MaintAI prédit le risque de panne à partir de relevés de température, vibration, charge et durée de fonctionnement. Ce TP associe le suivi des entraînements avec MLflow, le versionnement des données avec DVC et une recherche sur grille de 25 combinaisons.

Le réglage retenu est une régression logistique avec C = 0,1 et un seuil d’alerte de 0,2. Il obtient le meilleur F2 de validation de la grille, soit 0,7618. Après réentraînement sur 6 400 relevés, son rappel sur le test atteint 82,93 %.

| Vérification | Résultat |
| --- | --- |
| Tests automatisés | 32 réussis, 4 avertissements ; dernière durée : 33,25 s |
| Versions des données | v1 : 5 000 relevés ; v2 : 8 000 relevés |
| DVC | Deux envois réussis et restauration v1 ↔ v2 vérifiée |
| Recherche sur grille | 25 essais terminés ; essai 7 retenu selon le F2 |
| Point restant | Récupération par dvc pull après cache vide non vérifiée |

### Environnement d’exécution

Windows, PowerShell et Python 3.12.10 dans un environnement virtuel .venv. Installation du projet en mode éditable. Les versions ci-dessous sont celles confirmées par le journal d’installation.

| Composant | Version | Composant | Version |
| --- | --- | --- | --- |
| NumPy | 2.4.4 | pandas | 3.0.2 |
| scikit-learn | 1.8.0 | MLflow | 3.18.0 |
| DVC | 3.67.1 | pytest | 9.1.1 |
| FastAPI | 0.141.1 | Streamlit | 1.66.1 |


---

## 1 Installation et tests automatisés

La première installation de requirements.txt a été interrompue par des délais de connexion à PyPI et une erreur de socket lors du téléchargement de python-dotenv. Le lancement de pytest a ensuite échoué avec « No module named pytest ». L’installation a été relancée avec un délai plus long, puis a réussi.

```text
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --timeout 120 --retries 10
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m pytest -v
```

Le mode éditable rend le package maintai importable depuis l’environnement et déclare la commande maintai-predict. Les modifications du code source sont prises en compte sans réinstaller le package à chaque édition.

| Famille de tests | Nombre | Résultat |
| --- | --- | --- |
| API et contrat de prédiction | 7 | Réussis |
| Commande CLI | 2 | Réussis |
| Client HTTP | 3 | Réussis |
| Données et découpage | 3 | Réussis |
| Installation du package | 2 | Réussis |
| Sécurité et CORS | 5 | Réussis |
| Suivi MLflow | 5 | Réussis |
| Entraînement et artefacts | 3 | Réussis |
| Interface Streamlit | 2 | Réussis |
| Total | 32 | Aucun échec |

```text
Première exécution réussie : 32 passed, 4 warnings in 55.11s
Dernière exécution réussie : 32 passed, 4 warnings in 33.25s
```

### Interprétation des avertissements

Un avertissement concerne l’utilisation de httpx par le client de test Starlette ; un autre concerne la stratégie noload de SQLAlchemy utilisée par MLflow. Deux avertissements MLflow signalent la gestion des valeurs manquantes dans les colonnes entières. Ils n’ont provoqué aucun échec dans ces exécutions.

Les tests emploient leurs propres données et modèles temporaires. Ils valident le fonctionnement du code ; les entraînements réalisés séparément sur v1 et v2 vérifient l’utilisation des fichiers de données du projet.


---

## 2 Entraînements initiaux et suivi MLflow

Le pipeline combine une standardisation et un classifieur. Les modèles étudiés sont la régression logistique et une forêt aléatoire de 200 arbres. Le découpage initial réserve 20 % des données au test, avec stratification et une graine de 42.

### Résultats sur la v1

La v1 comprend 4 000 relevés d’entraînement et 1 000 relevés de test. Les métriques affichées par maintai.train sont arrondies à trois décimales.

| Modèle et réglage | Seuil | Recall | Precision | Accuracy |
| --- | --- | --- | --- | --- |
| Logistique C = 1 | 0,3 | 0,750 | 0,622 | 0,904 |
| Logistique C = 0,01 | 0,3 | 0,691 | 0,653 | 0,908 |
| Logistique C = 1 | 0,2 | 0,838 | 0,543 | 0,882 |
| Forêt de 200 arbres | 0,3 | 0,728 | 0,562 | 0,886 |

La baseline prédit toujours « pas de panne » : accuracy = 0,864 et recall = 0. Une accuracy élevée ne suffit donc pas à montrer que les pannes sont détectées. Parmi ces quatre essais, le seuil 0,2 fournit le rappel le plus élevé, au prix d’une précision plus faible.

### Résultats sur la v2

La v2 comprend 6 400 relevés d’entraînement et 1 600 relevés de test. Les deux entraînements ci-dessous ont été exécutés après restauration de la v2 par DVC.

| Modèle et réglage | Seuil | Recall | Precision | Accuracy |
| --- | --- | --- | --- | --- |
| Logistique C = 1 | 0,3 | 0,741 | 0,650 | 0,916 |
| Logistique C = 1 | 0,2 | 0,824 | 0,567 | 0,897 |

Sur le test v2, la baseline a une accuracy de 0,872 et un rappel nul. À C = 1 et au seuil 0,3, le passage v1 → v2 augmente la précision de 0,622 à 0,650, mais diminue le rappel de 0,750 à 0,741. Les jeux de test étant différents, ces écarts ne prouvent pas une amélioration générale du modèle.

### Traçabilité des expériences

La fonction log_run enregistre les paramètres, les métriques, l’empreinte MD5 du CSV et le modèle avec son exemple d’entrée. L’expérience MLflow porte le nom maintai. Les métadonnées sont conservées dans mlflow.db et les artefacts dans mlruns/.

Le paramètre data_md5 relie chaque entraînement à un contenu de données précis. Une comparaison fiable demande aussi le même découpage et le même protocole : partager une empreinte MD5 ne suffit pas à garantir ces conditions.


---

## 3 Versionnement des données avec DVC

| Version | Relevés | Commit | Empreinte MD5 |
| --- | --- | --- | --- |
| v1 | 5 000 | 22c9f8b | b7fec4274774842dc1f48202c6013490 |
| v2 | 8 000 | 4589c41 | 31ef5ebb63ef2331a31dfe009ef8796a |

Git conserve le fichier data/sensors.csv.dvc, qui décrit le contenu attendu du CSV. DVC conserve les données dans son cache et dans le stockage configuré. Les comptes de 5 000 et 8 000 excluent la ligne d’en-tête.

### Configuration et sauvegardes effectuées

Le stockage initial /tmp/dvc-stockage correspondait à l’environnement d’origine. Il a été remplacé localement par un dossier dvc-stockage-TP5 dans le profil Windows. Le paramètre --local évite de versionner un chemin propre à la machine.

```text
$stockageDvc = Join-Path $env:USERPROFILE "dvc-stockage-TP5"
New-Item -ItemType Directory -Force -Path $stockageDvc
.\.venv\Scripts\dvc.exe remote modify --local stockage url "$stockageDvc"
.\.venv\Scripts\dvc.exe push
```

L’envoi de la v2 a retourné « 1 file pushed ». La première restauration de v1 a échoué parce que son contenu manquait dans le cache, et le CSV n’était alors plus présent dans le dossier de travail.

### Reconstruction et vérification de la v1

La v1 a été reconstruite à partir de 5 000 relevés synthétiques, avec une graine de 42 et des fins de ligne LF. Get-FileHash a confirmé exactement l’empreinte B7FEC4274774842DC1F48202C6013490. Après dvc add puis dvc push, un second message « 1 file pushed » a confirmé sa sauvegarde.

### Restauration des deux versions

```text
git checkout 4589c41 -- data/sensors.csv.dvc
.\.venv\Scripts\dvc.exe checkout
(Import-Csv .\data\sensors.csv).Count
# Résultat observé : 8000

git checkout 22c9f8b -- data/sensors.csv.dvc
.\.venv\Scripts\dvc.exe checkout
(Import-Csv .\data\sensors.csv).Count
# Résultat observé : 5000
```

La v2 a ensuite été restaurée pour la recherche sur grille. Les sauvegardes et les restaurations depuis le cache sont vérifiées. En revanche, un dvc pull après retrait du CSV et du cache n’a pas encore été vérifié. Le stockage est local : il ne constitue pas une sauvegarde sur une autre machine.


---

## 4 Recherche sur grille de 25 essais

La recherche compare 15 combinaisons logistiques (3 valeurs de C × 5 seuils) et 10 combinaisons de forêt (2 tailles minimales de feuille × 5 seuils). Chaque combinaison est entraînée et enregistrée dans MLflow. Il s’agit d’une grille avec validation fixe, et non d’une validation croisée.

Découpage v2 : 4 800 relevés pour entraîner les candidats, 1 600 pour les classer et 1 600 pour tester le gagnant après réentraînement. Les deux séparations sont stratifiées, avec la graine 42. Le scaler est ajusté uniquement sur l’ensemble d’entraînement.

Critère fixé : F2 de validation maximal, puis rappel, précision et numéro d’essai en cas d’égalité. F2 = 5 × précision × rappel / (4 × précision + rappel). Le rappel reçoit ainsi davantage de poids. Toutes les valeurs ci-dessous sont celles affichées dans le journal des 25 essais, arrondies à quatre décimales ; les durées sont en secondes.

| Essai | Réglage | Seuil | Recall val. | Precision val. | F2 val. | Temps fit |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | LR 0,01 | 0,1 | 0,9657 | 0,3493 | 0,7138 | 0,018 |
| 2 | LR 0,01 | 0,2 | 0,8529 | 0,5273 | 0,7592 | 0,018 |
| 3 | LR 0,01 | 0,3 | 0,7108 | 0,6938 | 0,7073 | 0,012 |
| 4 | LR 0,01 | 0,4 | 0,5735 | 0,7597 | 0,6031 | 0,011 |
| 5 | LR 0,01 | 0,5 | 0,4559 | 0,8304 | 0,5011 | 0,013 |
| 6 | LR 0,1 | 0,1 | 0,9265 | 0,4065 | 0,7377 | 0,017 |
| 7 | LR 0,1 | 0,2 | 0,8529 | 0,5337 | 0,7618 | 0,011 |
| 8 | LR 0,1 | 0,3 | 0,7598 | 0,6540 | 0,7360 | 0,025 |
| 9 | LR 0,1 | 0,4 | 0,6716 | 0,7135 | 0,6796 | 0,019 |
| 10 | LR 0,1 | 0,5 | 0,5784 | 0,7468 | 0,6057 | 0,011 |
| 11 | LR 1,0 | 0,1 | 0,9216 | 0,4206 | 0,7443 | 0,015 |
| 12 | LR 1,0 | 0,2 | 0,8480 | 0,5356 | 0,7594 | 0,026 |
| 13 | LR 1,0 | 0,3 | 0,7598 | 0,6513 | 0,7353 | 0,018 |
| 14 | LR 1,0 | 0,4 | 0,6912 | 0,7050 | 0,6939 | 0,014 |
| 15 | LR 1,0 | 0,5 | 0,6176 | 0,7500 | 0,6402 | 0,011 |
| 16 | RF feuille 1 | 0,1 | 0,9020 | 0,4026 | 0,7227 | 2,251 |
| 17 | RF feuille 1 | 0,2 | 0,8333 | 0,5105 | 0,7398 | 2,313 |
| 18 | RF feuille 1 | 0,3 | 0,7500 | 0,5977 | 0,7136 | 2,421 |
| 19 | RF feuille 1 | 0,4 | 0,7010 | 0,6651 | 0,6935 | 2,330 |
| 20 | RF feuille 1 | 0,5 | 0,6373 | 0,7514 | 0,6572 | 2,462 |
| 21 | RF feuille 5 | 0,1 | 0,9118 | 0,4000 | 0,7260 | 2,133 |
| 22 | RF feuille 5 | 0,2 | 0,8382 | 0,5213 | 0,7474 | 2,289 |
| 23 | RF feuille 5 | 0,3 | 0,7745 | 0,6270 | 0,7397 | 2,187 |
| 24 | RF feuille 5 | 0,4 | 0,6716 | 0,6850 | 0,6742 | 2,706 |
| 25 | RF feuille 5 | 0,5 | 0,5931 | 0,7610 | 0,6205 | 2,366 |

LR : régression logistique, valeur de C indiquée. RF : forêt de 200 arbres, min_samples_leaf indiqué. L’essai 7 est surligné. Le CSV classement.csv contient aussi val_accuracy et les identifiants des runs ; les journaux détaillés transmis ne donnent pas val_accuracy pour chacun des 25 candidats.


---

## 5 Modèle retenu et résultats finaux

L’essai 7 est retenu : régression logistique C = 0,1, max_iter = 1000, standardisation et seuil d’alerte 0,2. C’est le meilleur réglage de cette grille selon le F2 de validation ; cela ne signifie pas qu’il maximise séparément toutes les métriques.

| Mesure | Validation | Test après réentraînement |
| --- | --- | --- |
| Accuracy | 0,8862 | 0,8944 |
| Precision | 0,5337 | 0,5592 |
| Recall | 0,8529 | 0,8293 |
| F2 | 0,7618 | 0,7562 |

Le modèle final est réentraîné sur les 6 400 relevés de développement. Sur 1 600 relevés de test, il détecte 82,93 % des pannes et 55,92 % des alertes sont justifiées. Son accuracy est de 89,44 %. La durée du réentraînement final mesurée est de 0,01545 s, hors suivi MLflow.

### Comparaison des meilleurs candidats

| Essai | Réglage | Seuil | F2 validation |
| --- | --- | --- | --- |
| 7 | Logistique C = 0.1 | 0,2 | 0,7618 |
| 12 | Logistique C = 1.0 | 0,2 | 0,7594 |
| 2 | Logistique C = 0.01 | 0,2 | 0,7592 |
| 22 | Forêt, feuille min. = 5 | 0,2 | 0,7474 |
| 11 | Logistique C = 1.0 | 0,1 | 0,7443 |

Le meilleur F2 de forêt est 0,7474, contre 0,7618 pour le modèle retenu. L’écart avec la logistique C = 1 est faible (environ 0,0024). Sans répétitions ni intervalle de confiance, cette différence ne démontre pas une supériorité statistique.

### Temps de calcul et sobriété

| Famille | Essais | Temps moyen fit | Temps cumulé fit |
| --- | --- | --- | --- |
| Régression logistique | 15 | 0,0159 s | 0,239 s |
| Forêt aléatoire | 10 | 2,3458 s | 23,458 s |

Dans cette exécution, la régression logistique combine le meilleur F2 de validation et un entraînement plus rapide. Ces durées isolent fit : elles excluent l’évaluation et l’enregistrement MLflow. Elles dépendent de la machine et ne mesurent ni consommation électrique ni émissions de CO2.

Une amélioration possible consiste à entraîner seulement les cinq configurations de modèles, puis à réutiliser leurs probabilités pour les cinq seuils. On conserverait les 25 évaluations tout en évitant les réentraînements dus au seul changement de seuil.


---

## 6 Traçabilité et décision d’architecture

Les identifiants ci-dessous permettent de retrouver les exécutions dans MLflow. Les quatre runs v1 et les deux runs v2 correspondent aux entraînements initiaux ; le dernier correspond au candidat sélectionné sur validation.

| Exécution | Run MLflow |
| --- | --- |
| v1 · C = 1 · seuil 0,3 | 3cf45b2bc9dc49a695573b9f8abc4654 |
| v1 · C = 0,01 · seuil 0,3 | 36d2332d5e0e4ee98e8d8ad5e62030f7 |
| v1 · C = 1 · seuil 0,2 | 8fd2b9808e8144d894cb583b3b788544 |
| v1 · forêt · seuil 0,3 | fca56ea0467f4006bb49b439000e7018 |
| v2 · C = 1 · seuil 0,3 | 75b92c77f4bb431ca6521c7690d22d8c |
| v2 · C = 1 · seuil 0,2 | 4c256b0b52024112a74dcbd880f183dc |
| Grille · essai 7 · validation | ba69ea8ff7f142d2bb1e70682f6ae09e |

Lot de recherche : 20261119_122823_509149. Les 25 runs sont filtrables avec params.grid_batch. Les colonnes de comparaison sont val_f2, val_recall, val_precision et val_accuracy ; les anciennes colonnes sans préfixe restent vides pour ces runs.

### Décision à reporter dans l’ADR 004

Retenir la régression logistique C = 0,1 et un seuil de 0,2, choisis sur la validation de la v2. Ce choix remplace le réglage initial C = 1. Il privilégie le rappel tout en conservant une mesure de précision dans le critère F2 et présente un coût de calcul inférieur aux forêts testées.

Le modèle final et ses résultats se trouvent dans resultats_grid/20261119_122823_509149/. Ce dossier contient model.joblib, meilleur_modele.json, classement.csv, resultats_25_essais.csv et compte_rendu_grid.md.

Le run MLflow sélectionné contient le candidat entraîné sur 4 800 lignes. Le model.joblib du dossier resultats_grid est réentraîné sur 6 400 lignes. Le script n’a pas remplacé automatiquement le modèle utilisé par l’application dans models/. Pour une intégration, conserver le modèle avec son seuil, ses caractéristiques d’entrée et des métadonnées compatibles avec l’application.

### Limites et état de la remise

Les données sont synthétiques et la recherche utilise un seul découpage. Le test avait déjà été consulté pendant les essais précédents : l’évaluation reste exploratoire, même si la grille ne l’utilise pas pour classer les candidats. Le coût métier exact des fausses alertes et des pannes manquées reste à préciser.

Git versionne le code et les pointeurs .dvc ; DVC gère le contenu des données ; MLflow suit les entraînements et les artefacts. Une livraison reproductible doit réunir le code, les dépendances, le modèle, son seuil et la référence des données. Un stockage partagé est nécessaire pour récupérer les données depuis une autre machine.

Les 32 tests, les entraînements v1/v2, les deux sauvegardes DVC, les restaurations entre versions et les 25 essais sont confirmés. La récupération via dvc pull avec cache vide et la publication éventuelle d’une PR et du tag tp5 restent à vérifier avant une remise qui les exige.

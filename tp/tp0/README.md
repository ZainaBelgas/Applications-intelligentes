# Projet MaintAI / CantineAI

Projet de machine learning qui compare plusieurs modèles et sauvegarde le meilleur.
Il est configuré pour **CantineAI** (prédire le nombre de repas de la cantine).

## Structure

```
projet_complet/
├── data/                  les fichiers CSV
├── docs/                  etude-de-conception.md et choix-modele.md
├── models/                le modèle sauvegardé après l'entraînement
├── monprojet/
│   ├── config.py          le seul fichier à adapter à votre sujet
│   ├── data.py            lecture des données et découpage entraînement / test
│   ├── models.py          les 4 modèles à comparer
│   └── train.py           entraînement, comparaison, sauvegarde
├── tests/                 tests automatiques
├── pytest.ini
└── requirements.txt
```

## Commandes (à taper dans un terminal, dans le dossier du projet)

```
pip install -r requirements.txt
python -m monprojet.train
pytest
```

- `python -m monprojet.train` affiche le tableau des scores et le meilleur modèle.
- `pytest` lance les tests automatiques (il doit afficher « 4 passed »).

## Passer à MaintAI

Le fichier `exemple_pannes.csv` est déjà dans `data/`.

1. Dans `monprojet/config.py`, changez ces lignes :

```python
DATA_PATH = ROOT / "data" / "exemple_pannes.csv"
TARGET = "failure"
TASK = "classification"
MAIN_METRIC = "recall"
SPLIT = "random"
TIME_COLUMN = None
THRESHOLD = 0.3
```

2. Relancez `python -m monprojet.train`.

Pour MaintAI, regardez la colonne `recall` (pannes détectées) et la colonne `precision` (alertes justes) : le critère est un rappel ≥ 90 % avec une précision ≥ 40 %.

Avec `THRESHOLD = 0.5`, le rappel du meilleur modèle est de 84,7 % : trop bas. Avec `THRESHOLD = 0.3`, la régression logistique atteint 92,0 % de rappel et 42,0 % de précision. Baisser le seuil détecte plus de pannes mais déclenche plus de fausses alertes.

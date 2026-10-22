# Étude de conception : MaintAI et CantineAI

Séance 3 · Développement et déploiement d'applications intelligentes

MaintAI est une classification (panne oui/non). CantineAI est une régression sur série temporelle (nombre de repas). Ce projet est configuré pour **CantineAI** ; les chiffres de CantineAI ont été mesurés avec `python -m monprojet.train`.

## Sections 1 à 5

| Section | MaintAI | CantineAI |
| --- | --- | --- |
| 1. Utilisateur principal | Le responsable de maintenance de l'usine. | Le gestionnaire de la cantine du lycée. |
| 2. Décision et fréquence | Choisir quelles machines inspecter. Chaque matin. | Choisir combien de repas commander pour demain. Chaque jour à 10 h. |
| 2. Coût d'une erreur | Panne ratée : une ligne arrêtée toute une journée (très cher). Fausse alerte : une heure d'inspection pour rien (peu cher). | Trop de repas : on jette, environ 15 DH perdus par repas. Pas assez : des élèves sans déjeuner et des parents mécontents. |
| 3. Approche | Machine learning simple (arbre ou forêt aléatoire). Pas de deep learning ni de LLM : le tableau est petit. Des règles seules ne suffisent pas, car plusieurs capteurs agissent ensemble. | Machine learning simple (régression linéaire). Pas de deep learning ni de LLM : seulement 340 lignes. Des règles seules ne suffisent pas, car le menu, la pluie et les examens jouent tous. |
| 4. Données | `data/exemple_pannes.csv`. Données inventées pour le cours (usage pédagogique). 5 000 lignes, 17,6 % de pannes. Aucune donnée personnelle. | `data/cantine_repas.csv`. Données inventées pour le cours (usage pédagogique). 340 jours d'école, sept. 2024 à juin 2026. Aucune donnée personnelle. |
| 5. Baseline | Une règle simple : alerte si la vibration dépasse un seuil. | Copier le chiffre de la semaine précédente (ce que fait le gestionnaire aujourd'hui). MAE = 76,0 repas sur le test. |
| 5. Métrique principale | Le rappel : la part des vraies pannes qu'on détecte. Rater une panne coûte très cher, donc on veut en détecter un maximum. | La MAE : l'erreur moyenne, en nombre de repas. Facile à comprendre pour le gestionnaire. |
| 5. Critère d'acceptation | Détecter au moins 90 % des pannes (rappel ≥ 90 %) sur le jeu de test, avec au moins 40 % d'alertes justes (précision ≥ 40 %). | Erreur moyenne ≤ 40 repas par jour sur le jeu de test (les 20 % derniers jours), et au moins 30 % meilleure que la baseline. |

## Réglages de config.py

| Réglage | MaintAI | CantineAI |
| --- | --- | --- |
| `DATA_PATH` (le fichier) | `ROOT / "data" / "exemple_pannes.csv"` | `ROOT / "data" / "cantine_repas.csv"` |
| `TARGET` (ce qu'on prédit) | `"failure"` | `"repas_servis"` |
| `TASK` (type de problème) | `"classification"` | `"regression"` |
| `MAIN_METRIC` (la mesure) | `"recall"` | `"mae"` |
| `SPLIT` (séparer entraînement et test) | `"random"` (80 % / 20 %, même part de pannes dans les deux) | `"chronologique"` (80 % des jours les plus anciens pour s'entraîner, 20 % des plus récents pour tester) |
| `TIME_COLUMN` (colonne de date) | `None` | `"date"` |

## Résultat mesuré pour CantineAI

Sur le jeu de test (68 derniers jours, du 25/02/2026 au 19/06/2026) :

- Baseline (semaine précédente) : MAE = 76,0 repas.
- Meilleur modèle (régression linéaire) : MAE = 22,2 repas, soit 71 % mieux que la baseline.
- Critère d'acceptation (MAE ≤ 40 et au moins 30 % meilleure que la baseline) : **atteint**.

## Résultat mesuré pour MaintAI

Données réelles du cours : 5 000 relevés (température, vibration, charge, heures de fonctionnement), 17,6 % de pannes. Jeu de test : 1 000 relevés tirés au hasard (stratifiés), dont 176 pannes.

| Modèle | Rappel | Précision | Critère (rappel ≥ 90 % et précision ≥ 40 %) |
| --- | --- | --- | --- |
| Régression logistique, seuil 0,5 | 84,7 % | 52,7 % | non atteint |
| Régression logistique, seuil 0,3 | 92,0 % | 42,0 % | **atteint** |
| Arbre de décision, seuil 0,3 | 89,8 % | 33,5 % | non atteint |
| Forêt aléatoire, seuil 0,3 | 81,2 % | 49,0 % | non atteint |
| Gradient boosting, seuil 0,3 | 73,3 % | 60,3 % | non atteint |
| Baseline « jamais de panne » | 0 % | 0 % | non atteint |

Avec le seuil par défaut (0,5), aucun modèle n'atteint un rappel de 90 %. En baissant le seuil d'alerte à 0,3, la régression logistique détecte 92 % des pannes, avec 42 % d'alertes justes. La marge sur la précision est faible (42 % pour un minimum de 40 %), et le seuil a été choisi en regardant le jeu de test : le résultat est un peu optimiste.

## Les deux questions finales

**MaintAI.** Un modèle qui ne prédit jamais de panne a **82,4 %** d'accuracy (100 − 17,6). Ça semble bon, mais il ne détecte aucune panne. Or une panne ratée coûte une journée de production. L'accuracy ne convient donc pas : seulement 17,6 % des cas sont des pannes, et elle ne dit rien sur les pannes ratées.

**CantineAI.** Si on tire les jours de test au hasard, le modèle voit déjà les jours voisins pendant l'entraînement (la veille, la semaine d'avant). Il « triche » sans le vouloir, et le résultat paraît meilleur qu'il n'est vraiment. Dans la vraie vie, on prédit le futur avec le passé. Il faut donc s'entraîner sur les premiers jours et tester sur les derniers.

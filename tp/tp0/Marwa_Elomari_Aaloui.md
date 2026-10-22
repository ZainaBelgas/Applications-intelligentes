# TP0 : MaintAI

**Nom :** Marwa Elomari Aaloui · **Groupe :** G1

## Le problème

L’objectif est de prédire une panne à partir des mesures de quatre capteurs. Une panne manquée peut entraîner l’arrêt d’une ligne ; il est donc important de détecter le plus grand nombre possible de pannes.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline | 0,824 | 0,000 | 0,000 |
| Régression logistique | 0,889 | 0,574 | 0,737 |

## Mon choix, et pourquoi

Parmi les deux modèles présentés, je retiens la régression logistique. Elle améliore l’accuracy de 0,824 à 0,889 et, contrairement à la baseline, détecte une partie des pannes. Sa précision de 0,737 indique que ses alertes sont souvent correctes. Toutefois, son rappel reste insuffisant pour un usage où manquer une panne est coûteux.

## Le critère (rappel >= 0,75) est-il atteint ?

Non. Le rappel obtenu est de 0,574, soit 0,176 point en dessous du seuil de 0,75. Le modèle manque donc environ 42,6 % des pannes du jeu de test. Il faudrait améliorer la détection avant de retenir ce modèle pour une utilisation opérationnelle.

## Ce qui reste flou

- Le nombre d’exemples dans le jeu de test, et en particulier le nombre de pannes, n’est pas indiqué. Les scores peuvent donc être sensibles à quelques exemples.
- La méthode de découpage des données et la représentativité du jeu de test ne sont pas précisées.
- Le seuil de décision de la régression logistique n’est pas indiqué. Le modifier pourrait augmenter le rappel, au prix possible d’une baisse de précision et d’un plus grand nombre de fausses alertes.
- Le coût concret des fausses alertes par rapport aux pannes manquées reste à préciser.

## Validation du projet

La suite de tests du projet a été exécutée avec succès : **8 tests passés**. Elle vérifie notamment le chargement et le découpage des données, les modèles candidats, l’évaluation, ainsi que la sauvegarde du meilleur modèle et des métriques.

## Analyse complémentaire du projet (résultats du code fourni)

Cette section complète le rapport ci-dessus sans le modifier. Elle s'appuie sur une nouvelle exécution de `python -m monprojet.train` (graine 42, version de scikit-learn 1.8.0), dont les scores sont enregistrés dans `models/metrics.json`.

### Données et découpage

- Fichier : `data/exemple_pannes.csv`, 5 000 lignes, 4 capteurs (`temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`) et la cible `failure`. Aucune valeur manquante.
- Découpage aléatoire stratifié (80 % / 20 %) : 4 000 lignes d'entraînement, 1 000 lignes de test.
- Jeu de test : 176 pannes (17,6 %) et 824 cas sans panne. La baseline, qui prédit toujours « pas de panne », obtient donc 0,824 d'accuracy et 0 de rappel.
- Métrique principale du projet (`config.py`) : le rappel, ce qui correspond au risque d'une panne manquée.

### Résultats mesurés sur le jeu de test

| Modèle | Accuracy | Rappel | Précision | F1 |
|---|---:|---:|---:|---:|
| Baseline | 0,824 | 0,000 | 0,000 | 0,000 |
| Régression logistique | 0,839 | 0,847 | 0,527 | 0,649 |
| KNN | 0,878 | 0,540 | 0,699 | 0,609 |
| Random forest | 0,882 | 0,540 | 0,720 | 0,617 |
| Gradient boosting | 0,888 | 0,608 | 0,713 | 0,656 |

### Écart avec le tableau du rapport

Les valeurs de la régression logistique du tableau initial (accuracy 0,889, rappel 0,574, précision 0,737) ne correspondent pas à celles produites par le code du projet (0,839 / 0,847 / 0,527). Elles sont proches de celles d'un modèle d'arbres comme le gradient boosting (0,888 / 0,608 / 0,713), mais ne sont identiques à aucune ligne de `metrics.json`. Il faut donc vérifier leur origine avant de les citer comme résultats du projet. La baseline (0,824 / 0 / 0) est, elle, cohérente.

### Le critère (rappel >= 0,75) avec les résultats mesurés

- La régression logistique atteint le critère : rappel de 0,847, soit 0,097 point au-dessus du seuil. Elle détecte environ 149 des 176 pannes du jeu de test et en manque environ 27 (15,3 %).
- Aucun des trois autres modèles ne l'atteint : KNN et random forest sont à 0,540, gradient boosting à 0,608.
- Le prix à payer est la précision : 0,527, soit environ 134 fausses alertes pour 149 pannes détectées, donc à peu près une alerte sur deux est une fausse alerte. Les modèles d'arbres, plus précis (0,71 à 0,72), laissent passer près de 40 % des pannes (69 manquées pour le gradient boosting).
- Cette observation s'explique en partie par `class_weight="balanced"`, qui pousse la régression logistique à signaler davantage de pannes. Elle est à privilégier si une panne manquée coûte nettement plus cher qu'une inspection inutile.

### Précisions sur les points restés flous

- Taille du jeu de test : 1 000 lignes dont 176 pannes. Un écart d'un point de rappel correspond à environ 1,8 panne, donc les scores restent sensibles à quelques exemples.
- Méthode de découpage : aléatoire, stratifié sur la cible, graine 42. Pour des mesures prises dans le temps, un découpage chronologique serait plus réaliste, car un découpage aléatoire peut rendre les résultats un peu trop optimistes.
- Seuil de décision : le seuil par défaut de 0,5 est utilisé, aucun réglage n'a été fait. Il reste à explorer pour arbitrer entre rappel et précision.
- Reste à préciser : le coût réel d'une fausse alerte par rapport à une panne manquée. Il permettrait de dire si 134 fausses alertes sont acceptables.

### Validation technique

- Tests : `python -m pytest` donne 8 passed.
- Correction faite pendant la mise au point : `_file_` remplacé par `__file__` dans `monprojet/config.py`, ce qui débloquait la collecte des tests.
- Pour un test plus fiable, il serait utile de comparer les modèles par validation croisée plutôt que sur un seul découpage.

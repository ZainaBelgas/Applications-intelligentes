\# TPO : MaintAI



\*\*Nom : ZAHR\*\* Prénom  : Amira

\*\*Groupe :\*\* G1

\*\*Module :\*\* Développement et déploiement d'applications intelligentes — S4



\---



\## Le problème



Prédire une panne à partir de 4 capteurs (température, vibration, charge, heures de fonctionnement). Une panne manquée arrête une ligne de production : le coût d'un faux négatif est bien supérieur à celui d'une fausse alarme. Le \*\*rappel\*\* (part des pannes réellement détectées) est donc la métrique prioritaire, sous contrainte d'une précision minimale pour limiter les fausses alertes.



\*\*Critère de réussite :\*\* rappel ≥ 90 % \*\*et\*\* précision ≥ 40 %.



\*\*Données :\*\* 5 000 lignes, découpées aléatoirement (graine 42) en 4 000 pour l'entraînement et 1 000 pour le test. Seuil d'alerte utilisé : \*\*0,3\*\*.



\## Résultats sur le jeu de test



| Modèle                              | Accuracy | Rappel | Précision | F1    |

|-------------------------------------|----------|--------|-----------|-------|

| Baseline (classe la plus fréquente) | 0.824    | 0.000  | 0.000     | 0.000 |

| \*\*Régression logistique\*\*           | 0.762    | \*\*0.920\*\* | \*\*0.420\*\* | 0.577 |

| Arbre de décision                   | 0.668    | 0.898  | 0.335     | 0.488 |

| Forêt aléatoire                     | 0.818    | 0.812  | 0.490     | 0.611 |

| Gradient boosting                   | 0.868    | 0.733  | 0.603     | 0.662 |



\*\*Lecture :\*\*

\- La baseline atteint 0.824 d'accuracy sans détecter aucune panne : les classes sont déséquilibrées (environ 17,6 % de pannes). L'accuracy seule est trompeuse.

\- Le gradient boosting a la meilleure accuracy (0.868) et la meilleure précision (0.603), mais son rappel (0.733) est trop faible pour le critère.

\- La régression logistique a une accuracy plus basse que la baseline (0.762), car le seuil bas déclenche beaucoup d'alertes. C'est le prix à payer pour un rappel élevé, et c'est le seul modèle qui satisfait les deux conditions.

\- Effet du seuil : à 0,5, le meilleur rappel n'est que de 84,7 % (insuffisant). Abaisser le seuil à 0,3 augmente le rappel mais réduit la précision.



\## Le critère (rappel ≥ 90 % et précision ≥ 40 %) est-il atteint ?



\*\*Oui, mais de justesse, et uniquement avec la régression logistique à un seuil de 0,3.\*\*



\- Rappel : 0.920 ≥ 0.90 ✔ (marge de 2 points)

\- Précision : 0.420 ≥ 0.40 ✔ (marge de 2 points)



Aucun autre modèle ne remplit les deux conditions : l'arbre de décision échoue de très peu sur le rappel (0.898) et nettement sur la précision (0.335) ; la forêt aléatoire et le gradient boosting ont une bonne précision mais un rappel insuffisant.



En pratique (ordre de grandeur sur 1 000 exemples de test, environ 176 pannes) : environ 160 pannes détectées sur 176, soit une quinzaine de pannes manquées, au prix d'environ 220 fausses alertes.



\## Ce qui reste flou



\- \*\*Choix du seuil sur le jeu de test\*\* : le seuil de 0,3 a été retenu en observant les résultats du test. Les marges (+2 points) sont faibles et pourraient disparaître sur de nouvelles données. Il faudrait choisir le seuil sur un jeu de validation séparé.

\- \*\*Fiabilité de l'estimation\*\* : avec environ 176 pannes dans le test, le rappel est incertain de plusieurs points. Une validation croisée stratifiée et un intervalle de confiance sont nécessaires pour conclure.

\- \*\*Coût réel d'une fausse alerte\*\* : environ 220 fausses alertes pour 1 000 mesures peuvent être acceptables ou non selon le coût d'une inspection inutile. Le seuil de 40 % de précision doit être validé avec le métier.

\- \*\*Modèle retenu\*\* : un modèle linéaire gagne grâce à un seuil bas. Le gradient boosting, plus précis, pourrait atteindre le critère avec un seuil encore plus bas ; ce cas n'a pas été testé.

\- \*\*Déséquilibre des classes\*\* : aucune technique (pondération, sur-échantillonnage) n'a été essayée.

\- \*\*Données\*\* : qualité des capteurs, dérive dans le temps, et découpage aléatoire (et non chronologique) qui peut être trop optimiste pour un usage réel.

\- \*\*Déploiement\*\* : horizon de prédiction (combien de temps avant la panne ?), fréquence de ré-entraînement et surveillance du modèle en production non définis.



\## Reproduire les résultats



```powershell

pip install -r requirements.txt

python -m monprojet.train

python -m pytest

```



Configuration utilisée (`monprojet/config.py`) : `TARGET = "failure"`, `TASK = "classification"`, `MAIN\_METRIC = "recall"`, `SPLIT = "random"`, `SEED = 42`, `THRESHOLD = 0.3`.


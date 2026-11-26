# Choix du modèle (CantineAI)

## Comparaison

Quatre modèles sont entraînés sur les 272 premiers jours et évalués sur les 68 derniers jours (découpage chronologique). Plus la MAE est petite, mieux c'est.

| Modèle | MAE (repas) | RMSE (repas) | R² |
| --- | --- | --- | --- |
| Régression linéaire | 22,2 | 28,2 | 0,88 |
| Gradient boosting | 29,9 | 37,7 | 0,79 |
| Forêt aléatoire | 31,5 | 41,3 | 0,75 |
| Arbre de décision | 42,0 | 54,8 | 0,56 |
| Baseline (semaine précédente) | 76,0 | 95,6 | −0,35 |

## Modèle choisi : la régression linéaire

- **Meilleur score** : MAE de 22,2 repas, contre 76,0 pour la baseline (71 % mieux).
- **Critère d'acceptation atteint** : MAE ≤ 40 repas et au moins 30 % meilleure que la baseline.
- **Simple à expliquer** : chaque information (menu, pluie, examens, sortie scolaire) ajoute ou enlève un nombre de repas.
- **Adapté à peu de données** : avec 340 lignes, un modèle simple se trompe moins qu'un modèle complexe qui apprend le bruit.

## Limites

- Le jeu de test sert à la fois à comparer et à choisir : le score du meilleur modèle est un peu optimiste.
- Les données sont inventées pour le cours : les résultats ne disent rien sur une vraie cantine.
- Le test ne contient que 68 jours : un autre découpage pourrait changer l'ordre des modèles.

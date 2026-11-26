# Choix du modèle

**Auteure :** CHAIMAA EZZERAG
**Projet :** Entraîner et comparer des modèles
**Tâche :** Régression
**Métrique principale :** MAE (erreur absolue moyenne, plus elle est basse, mieux c'est)

## 1. Vérification du projet

Tous les tests fournis passent :

```
python -m pytest
8 passed in 40.18s
```

Les fonctions `load_data()`, `split()`, `candidates()`, `evaluate()` et `main()` sont donc conformes à ce qui est attendu.

## 2. Résultats sur le jeu de test

Résultats obtenus avec `python -m monprojet.train`, triés selon la MAE :

| Rang | Modèle | MAE ↓ | RMSE ↓ | R² ↑ |
|---|---|---|---|---|
| 1 | **ridge** | **22.377** | **28.315** | **0.882** |
| 2 | gradient_boosting | 29.852 | 37.727 | 0.790 |
| 3 | random_forest | 31.825 | 41.647 | 0.745 |
| 4 | knn | 40.274 | 49.450 | 0.640 |
| 5 | baseline | 70.271 | 88.416 | -0.151 |

## 3. Modèle retenu

Le modèle retenu est **Ridge** (régression linéaire avec régularisation L2).

Il obtient le meilleur score sur la métrique principale (MAE = 22.377), mais aussi sur les deux autres métriques (RMSE et R²). Le choix est donc cohérent quelle que soit la métrique regardée. Son R² de 0.882 signifie qu'il explique environ 88 % de la variance de la cible sur le jeu de test.

Ridge devance le deuxième modèle, Gradient Boosting, de 7.475 points de MAE, soit une erreur environ 25 % plus faible. Le fait qu'un modèle linéaire batte des modèles plus complexes (Gradient Boosting, Random Forest) suggère que la relation entre les variables et la cible est en grande partie linéaire. C'est aussi un avantage pratique : Ridge est rapide à entraîner, léger et facile à interpréter.

Le modèle est sauvegardé dans `models/model.joblib` et les scores dans `models/metrics.json`.

## 4. Écart avec la baseline

| Métrique | Baseline | Ridge | Amélioration |
|---|---|---|---|
| MAE | 70.271 | 22.377 | −47.894 (−68.2 %) |
| RMSE | 88.416 | 28.315 | −60.101 (−68.0 %) |
| R² | -0.151 | 0.882 | +1.033 |

La baseline a un R² négatif : elle fait moins bien qu'une prédiction constante égale à la moyenne. Ridge réduit l'erreur moyenne de plus des deux tiers par rapport à elle, ce qui montre que le modèle apprend réellement quelque chose des données.

## 5. Critère d'acceptation

**Critère fixé :** _à compléter (ex. « MAE inférieure à X » ou « au moins Y % de mieux que la baseline »)_

**Résultat :** _Atteint / Non atteint_ — avec une MAE de 22.377 et une amélioration de 68.2 % par rapport à la baseline.

## 6. Limites et pistes d'amélioration

Les résultats reposent sur un seul découpage entraînement / test ; une validation croisée donnerait une estimation plus fiable. Les hyperparamètres des modèles (par exemple `alpha` pour Ridge, ou la profondeur et le nombre d'arbres pour Gradient Boosting et Random Forest) pourraient être optimisés avec `GridSearchCV`, ce qui pourrait réduire l'écart ou changer le classement.
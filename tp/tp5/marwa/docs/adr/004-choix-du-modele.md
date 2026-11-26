# ADR 004 : choix du modèle et du seuil d'alerte

**Date :** 19/11/2026
**Auteur :** Marwa Elomari Alaoui

## Contexte

MaintAI prédit les pannes à partir de relevés synthétiques de capteurs. Une panne manquée est considérée comme plus coûteuse qu'une fausse alerte. Le modèle doit donc conserver un recall élevé tout en respectant une précision minimale acceptable.

Les données sont identifiées par leur empreinte DVC/MLflow. Le grid search a été exécuté sur la v2 finale de 8 000 relevés, `data_md5 = 93fdeef2cac1893c4f720c16457eea75`.

## Options étudiées

Une première comparaison sur la v1 (5 000 relevés, `data_md5 = b7fec4274774842dc1f48202c6013490`) avait conduit à retenir provisoirement la régression logistique `C=1.0`, seuil `0.2` : recall `0.838`, précision `0.543` et accuracy `0.882`. Ce choix privilégiait la détection des pannes par rapport au seuil standard `0.3`.

La recherche sur grille a ensuite comparé 25 couples de `C` et de seuil sur la v2. La règle de sélection était : recall maximal parmi les résultats dont la précision est au moins `0.50`.

| Essai | `C` | Seuil | Recall | Précision | Accuracy | F2 |
|---:|---:|---:|---:|---:|---:|---:|
| 17 | 1.0 | 0.15 | 0.859 | 0.506 | 0.874 | 0.754 |
| **22** | **10.0** | **0.15** | **0.859** | **0.507** | **0.875** | **0.754** |
| 23 | 10.0 | 0.20 | 0.824 | 0.567 | 0.897 | 0.756 |
| 25 | 10.0 | 0.30 | 0.741 | 0.650 | 0.916 | 0.721 |

Le seuil `0.10` peut donner un recall supérieur, mais les meilleures combinaisons à ce seuil ne respectent pas la précision minimale de `0.50`. Les essais 17 et 22 ont le même recall à trois décimales ; l'essai 22 a la précision et l'accuracy légèrement supérieures.

## Décision

Retenir comme candidat issu du TP la régression logistique avec **`C=10.0` et un seuil d'alerte de `0.15`**.

- Essai retenu : 22.
- Recall : `0.859`.
- Précision : `0.507`.
- Accuracy : `0.875`.
- F2 : `0.754`.
- Données utilisées : v2 finale, `data_md5 = 93fdeef2cac1893c4f720c16457eea75`.

Ce choix suit le critère annoncé, c'est-à-dire maximiser le recall tout en maintenant la précision à au moins `0.50`. Il remplace la décision provisoire v1 (`C=1.0`, seuil `0.2`) pour les résultats du grid search sur la v2.

## Conséquences et limites

- Une précision de `0.507` implique un volume conséquent de fausses alertes ; les équipes de maintenance doivent valider si ce compromis est acceptable.
- Le seuil retenu par le grid search est `0.15`. La valeur par défaut du projet peut rester `0.3` ; le seuil doit être explicitement configuré à `0.15` pour reproduire ce résultat.
- Les mesures proviennent d'un seul découpage test et de données synthétiques. Le choix doit être réévalué sur des données réelles, un jeu de test indépendant et avec les coûts opérationnels des erreurs.
- Les métriques v1 et v2 ne sont pas directement comparables sans protocole d'évaluation commun.
- L'objet DVC correspondant à la v1 n'était pas disponible dans le cache/remote lors de la tentative de restauration ; cette bascule n'a donc pas été certifiée par un `dvc checkout` réussi.

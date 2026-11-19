# ADR 004 : choix du modèle et du seuil d'alerte

Date : 19/11/2026 · Auteurs : groupe TP5

## Contexte
MaintAI prédit une panne à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte : il faut un rappel (recall) élevé, sans que la précision s'effondre au point de noyer les équipes sous les fausses alertes. Les essais sont suivis dans MLflow, et les données sont versionnées avec DVC.

## Options étudiées
Runs sur la v1 des données (`data_md5` = `b7fec4274774842dc1f48202c6013490`, 5000 lignes), même découpage (SEED 42) :

| Run | Réglage | recall | precision | accuracy |
|---|---|---|---|---|
| `777c87e1…` | logreg, C=1.0, seuil 0,3 | 0,750 | 0,622 | 0,904 |
| `565a13fb…` | logreg, C=0,01, seuil 0,3 | 0,691 | 0,653 | 0,908 |
| `3f6c5a63…` | logreg, C=1.0, seuil 0,2 | 0,838 | 0,543 | 0,882 |
| `d116b817…` | forêt aléatoire, seuil 0,3 | 0,728 | 0,562 | 0,886 |
| `ff9c6f36…` | logreg, C=1.0, seuil 0,1 | 0,919 | 0,434 | 0,826 |

La baseline (toujours « pas de panne ») a un recall de 0 : tous les runs la battent.

## Décision
Régression logistique (C=1.0) avec un **seuil d'alerte de 0,2**.
- Run retenu : `3f6c5a6337734f82897e292f7efae242`, données `data_md5` = `b7fec4274774842dc1f48202c6013490` (v1).
- Raison principale : une panne manquée coûte plus cher qu'une fausse alerte, donc on privilégie le recall (0,838 contre 0,750 au seuil 0,3). On ne va pas jusqu'au seuil 0,1 : la précision tomberait à 0,434, soit plus d'une alerte sur deux fausse.
- La forêt aléatoire ne fait pas mieux que la régression logistique à seuil égal et est plus lourde ; on garde le modèle le plus simple.

Vérification sur la v2 (`data_md5` = `31ef5ebb…`, 8000 lignes), run `1cef043e253a4c07bd6a5f3232accb28` : recall 0,824, precision 0,567. Même ordre de grandeur, la décision tient.

## Conséquences
- Plus d'alertes (précision ≈ 0,55) : à surveiller avec les équipes de maintenance.
- Le seuil est lu dans `MAINTAI_THRESHOLD` (défaut 0,3) : le fixer à 0,2 en production.
- Les métriques viennent d'un seul découpage test de 20 % et de données synthétiques ; à revalider sur des données réelles et si les données changent (comparer les `data_md5`).

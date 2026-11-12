# ADR 000 : Sélection du modèle de classification pour la prédiction des pannes

Date : 09/11/2026 · Auteurs : ZAHR Amira

## Contexte

L'objectif du projet MaintAI est d'estimer la probabilité d'une panne à partir de différentes mesures issues de capteurs, notamment la température, les vibrations, la charge et les heures de fonctionnement. Le système repose sur un modèle entraîné sur des données synthétiques, dont les prédictions sont ensuite accessibles à travers une API FastAPI et exploitables depuis une interface Streamlit ainsi qu'un client web.

Le principal enjeu est de mettre en place une solution suffisamment performante pour répondre aux objectifs du projet, tout en privilégiant la simplicité de développement, le déploiement et la maintenance.

## Options étudiées

1. **Approche linéaire : StandardScaler + LogisticRegression**
   - Avantages : entraînement rapide, bonne interprétabilité des résultats et consommation limitée des ressources. Ce modèle convient aux données numériques structurées et peut être facilement sauvegardé puis intégré dans l'API.
   - Inconvénients : ses capacités restent limitées lorsqu'il s'agit de représenter des relations non linéaires ou des interactions complexes entre les variables.

2. **Approche basée sur des modèles plus complexes : arbres de décision, forêts aléatoires, etc.**
   - Avantages : permet de mieux prendre en compte les relations non linéaires et les interactions entre les différentes mesures des capteurs.
   - Inconvénients : nécessite davantage de ressources et peut rendre l'interprétation, le déploiement et la maintenance plus complexes. Ces modèles représentent également une solution plus avancée que nécessaire pour une première version du projet.

## Décision

Nous avons choisi d'utiliser un pipeline de classification avec Scikit-learn, associant `StandardScaler` à `LogisticRegression`.

Cette solution est adaptée à notre problématique de classification binaire, qui consiste à distinguer les situations présentant un risque de panne de celles qui n'en présentent pas. Elle permet de traiter les variables numériques après normalisation, tout en fournissant une probabilité exploitable par l'application. Le modèle entraîné peut également être sauvegardé avec `joblib`, puis rechargé facilement lors de son utilisation dans l'API.

Ce choix constitue donc un compromis pertinent entre simplicité, interprétabilité et facilité d'intégration dans l'architecture de MaintAI.

## Conséquences

L'utilisation de ce modèle présente plusieurs avantages :
- simplification et accélération de la phase d'entraînement ;
- possibilité de reproduire les expériences dans les mêmes conditions ;
- sauvegarde et rechargement faciles du modèle grâce à `joblib` ;
- intégration directe dans les services FastAPI et dans l'interface Streamlit ;
- meilleure compréhension de l'influence des variables sur les prédictions.

Cependant, certaines limites doivent être prises en considération :
- le modèle peut être moins adapté aux comportements complexes et non linéaires ;
- ses performances peuvent diminuer face à des données réelles plus variées ou plus bruitées.

Il sera donc nécessaire de porter une attention particulière à la qualité des données utilisées, au réglage du seuil de classification (`threshold`) selon les besoins du projet, ainsi qu'à l'évaluation régulière des performances. Si les résultats deviennent insuffisants, l'utilisation d'un modèle plus avancé pourra être envisagée.
# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G1  
**Membre :** Chaimaa Ezzerag  
**Date :** 12/11/2026

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` après la mise en place :

```text
À compléter avec la sortie du premier lancement de pytest.
```

**Quels fichiers de tests échouent, et quelle erreur donnent-ils ?**

À compléter avec les résultats du premier lancement. Les résultats finaux présentés dans la partie 4 montrent que tous les tests passent après les corrections.

## 2. Lancer Streamlit

Première commande exécutée :

```powershell
streamlit run ui/app.py
```

**Résultat observé dans le navigateur :**

```text
À compléter avec le message exact obtenu lors du premier lancement.
```

Deuxième commande exécutée :

```powershell
python -m streamlit run ui/app.py
```

**Pourquoi cette commande fonctionne-t-elle et pas la première ?**

La commande `python -m streamlit` lance le module Streamlit avec l'interpréteur Python actuellement actif dans l'environnement virtuel `.venv`.

La commande `streamlit` dépend de la résolution de l'exécutable dans le PATH de Windows. Si cet exécutable n'est pas trouvé ou ne correspond pas au bon environnement Python, la commande échoue.

L'utilisation de `python -m streamlit` permet donc de s'assurer que Streamlit est lancé avec le Python de l'environnement du projet.

## 3. Sprint 1 : l'onglet « Données »

### Code de l'onglet Données

```python
À compléter en copiant le code réel de ui/app.py,
depuis c1, c2, c3 = ... jusqu'au nuage de points.
```

### Indicateurs affichés

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5 000 |
| Taux de panne | 13,56 % |
| Température moyenne | À relever dans Streamlit |

### Analyse de la variable `vibration_mm_s`

Lorsque la vibration augmente, le taux de panne a tendance à augmenter. Une vibration importante peut être un signe de fonctionnement anormal d'une machine et donc un indicateur de risque de panne.

Le graphique permet de visualiser la relation entre le niveau de vibration et la fréquence des pannes dans le dataset.

### Expérience avec `print("relance")`

Après avoir ajouté `print("relance")` en haut de `ui/app.py`, puis déplacé un curseur dans Streamlit, le message apparaît de nouveau dans le terminal.

Cela montre que Streamlit réexécute le script lorsqu'un utilisateur interagit avec un widget. Cette réexécution permet de mettre à jour automatiquement l'interface en fonction des nouvelles valeurs.

### Rôle de `@st.cache_data`

Le décorateur `@st.cache_data` permet de mettre en cache le résultat d'une fonction qui charge ou transforme des données.

Dans notre projet, il est utilisé sur la fonction `charger` pour éviter de relire et de retraiter le fichier CSV à chaque réexécution de l'application, tant que les données et les paramètres restent identiques.

Cela améliore les performances et réduit les chargements inutiles.

## 4. Sprint 2 : l'onglet « Prédiction »

### Méthode `predict` de `maintai/client.py`

```python
À compléter en copiant la méthode predict réelle
depuis maintai/client.py.
```

Cette méthode permet à Streamlit de communiquer avec l'API MaintAI. Elle envoie les valeurs saisies par l'utilisateur à l'endpoint `/v1/predict` avec une requête HTTP POST.

Si une clé API est configurée, elle est transmise dans l'en-tête `X-API-Key`. Si l'API renvoie une erreur HTTP, le client récupère le statut et le détail de l'erreur et les transmet sous forme d'`APIError`. En cas de succès, il retourne la réponse JSON.

### Résultat des tests à la fin du Sprint 2

Commande exécutée :

```powershell
python -m pytest
```

Résultat final obtenu :

```text
======================================= 23 passed, 1 warning in 6.00s =======================================
```

Détail des tests :

- `tests/test_api.py` : 7 tests réussis.
- `tests/test_client.py` : 3 tests réussis.
- `tests/test_data.py` : 3 tests réussis.
- `tests/test_security.py` : 5 tests réussis.
- `tests/test_train.py` : 3 tests réussis.
- `tests/test_ui.py` : 2 tests réussis.

Les 23 tests passent. L'avertissement concerne une dépréciation liée à l'utilisation de `httpx` avec `starlette.testclient`. Il ne bloque pas l'exécution des tests.

### Essais de prédiction

| Essai | Ce qu'affiche Streamlit |
|---|---|
| Valeurs par défaut, bonne clé (`AZ`) | Résultat de la prédiction retourné par l'API, avec la probabilité de panne et l'état du risque, lorsque la clé est acceptée. |
| Valeurs par défaut, fausse clé | Erreur API 401 : clé API absente ou invalide. |
| API arrêtée (`Ctrl+C` dans le terminal Uvicorn) | Erreur de connexion à l'API, car le serveur n'est plus disponible. |

### Pourquoi la prédiction fonctionne-t-elle alors que le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS` ?

CORS est un mécanisme de sécurité appliqué principalement par les navigateurs lorsqu'une page web effectue une requête vers un autre domaine ou port.

Dans notre application, Streamlit exécute le code Python côté serveur. C'est donc le serveur Streamlit qui envoie la requête HTTP à l'API MaintAI, et non directement le navigateur.

La communication entre les deux serveurs n'est pas soumise à la politique CORS du navigateur. C'est pourquoi le port 8501 n'a pas besoin d'être ajouté à `MAINTAI_CORS_ORIGINS` pour cette communication.

## 5. Questions de compréhension

### 1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?

Dans le TP2, c'est le code JavaScript exécuté dans le navigateur du client qui envoie la requête HTTP à l'API.

Dans le TP3, c'est le code Python exécuté par le serveur Streamlit qui envoie la requête à l'API grâce à `MaintaiClient`.

### 2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'Uvicorn ?

Les tests de `test_client.py` vérifient le comportement du client HTTP de manière isolée, à l'aide d'un mécanisme de simulation des réponses HTTP.

Ils n'ont donc pas besoin de démarrer un véritable serveur Uvicorn. Cela rend les tests plus rapides et permet de vérifier différents scénarios, notamment les réponses réussies et les erreurs HTTP.

### 3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?

Pour une démonstration à un client, je choisirais HTML + JavaScript, car cette solution permet de créer une interface personnalisée, professionnelle et adaptée à l'identité visuelle de l'entreprise.

Pour une application destinée à un technicien de maintenance, je choisirais Streamlit pour sa simplicité de développement et son intégration avec Python. Il permet de consulter rapidement les données, de visualiser les indicateurs et de lancer des prédictions sans développer toute une interface web.

Le choix dépend donc de l'objectif : personnalisation et présentation pour le client, simplicité et visualisation des données pour le technicien.

## 6. Le rendu Git

- **Lien du dossier TP3 sur GitHub :** [TP3 — Chaimaa Ezzerag](https://github.com/ZainaBelgas/Applications-intelligentes/tree/main/tp/Tp3/chaimaa).
- **Lien de la pull request :** Aucune pull request trouvée. Les livrables sont disponibles sur la branche `main`.
- **Le tag `tp3` existe sur GitHub :** Le tag `tp3` n’a pas été trouvé lors de la vérification.
- **`git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ?** La sortie de cette commande n’a pas été conservée ; leur présence avant le commit ne peut donc pas être confirmée à partir de la capture GitHub.

Les livrables publiés comprennent les dossiers `maintai/`, `ui/` et le fichier `Compte-rendu.md`. Les fichiers contenant des secrets, comme `.env`, ne doivent pas être publiés. Les données générées et les modèles doivent être gérés conformément aux consignes du projet et au fichier `.gitignore`.

## 7. Ce qui reste flou

Les points que je souhaite encore approfondir sont :

- La différence entre une requête HTTP envoyée depuis le navigateur et une requête envoyée depuis un serveur Python.
- Le fonctionnement du cache Streamlit et les conditions qui provoquent une nouvelle lecture des données.
- La gestion des erreurs HTTP et des clés API dans une application connectée à un backend.
- La différence entre les tests unitaires utilisant des réponses simulées et les tests nécessitant une véritable API.

## Conclusion

Ce TP m'a permis de construire une interface Streamlit connectée à l'API MaintAI.

J'ai appris à explorer un dataset, à afficher des indicateurs et des graphiques, à utiliser des widgets interactifs et à envoyer des données à une API pour obtenir une prédiction.

J'ai également compris le rôle du client HTTP, la gestion des clés API, les tests automatisés et la différence entre une communication côté navigateur et une communication côté serveur.



# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Étudiante :** BELGAS Zainab   
**Date :** 09/11/2026

## 1. Mise en place (dans `TP/TP3`)

**Première exécution de `python -m pytest` pendant la mise en place :**

```text
1 failed, 22 passed, 1 warning in 9.30s
```

**Quels fichiers de tests échouent, et quelle erreur donnent-ils ?**

Le fichier concerné était `tests/test_ui.py`, notamment le test :

```text
tests/test_ui.py::test_ui_shows_the_prediction
```

Deux problèmes ont été rencontrés successivement pendant les corrections :

1. La fonction de prédiction utilisait une mauvaise clé dans le résultat retourné par l'API : `probability` au lieu de `failure_probability`. Cela provoquait une `KeyError`. Le test attendait également l'affichage de `95 %`, mais le dernier indicateur récupéré était celui de la température (`59.7 °C`).

2. Après une première correction, une erreur `NameError: name 'pct' is not defined` est apparue dans `ui/app.py`. La variable `pct` n'était pas définie correctement avant son utilisation dans `st.metric()`.

Ces deux problèmes ont été corrigés. À la fin du sprint 2, les 23 tests passent avec succès.

## 2. Lancer Streamlit

**Première commande demandée :**

```powershell
streamlit run ui/app.py
```

La sortie de cette première commande n'apparaît pas dans les traces conservées. Il n'est donc pas possible de confirmer le message exact affiché lors de cet essai.

**Commande effectivement exécutée :**

```powershell
python -m streamlit run ui/app.py
```

Au premier lancement documenté, Streamlit a affiché son message de bienvenue et demandé éventuellement une adresse e-mail. Ensuite, une erreur `FileNotFoundError` est apparue, car le fichier `data/sensors.csv` était absent du dossier TP3.

Le fichier a été retrouvé dans le projet TP2, puis copié dans le dossier TP3 avec :

```powershell
Copy-Item "C:\Users\pc\Downloads\S5_maintai-starter-tp2\maintai-starter-tp2\data\sensors.csv" ".\data\sensors.csv"
```

Après cette correction, Streamlit a démarré correctement et l'application était accessible à l'adresse :

```text
http://localhost:8501
```

**Pourquoi utiliser `python -m streamlit` ?**

Cette commande demande directement à l'interpréteur Python sélectionné d'exécuter le module Streamlit installé dans son environnement.

Si la commande `streamlit` seule n'est pas reconnue, cela peut être dû à l'absence de son lanceur dans le `PATH` Windows ou à une différence d'environnement Python. La commande `python -m streamlit` permet d'éviter ce problème.

## 3. Sprint 1 : l'onglet « Données »

**Code utilisé pour l'exploration des données :**

```python
# 1. Trois indicateurs
c1, c2, c3 = st.columns(3)
c1.metric("Nombre de relevés", len(df))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

# 2. Choisir une variable
variable = st.selectbox("Choisir une variable", FEATURES)

# 3. Taux de panne par tranche
tranches = pd.cut(df[variable], bins=10)
taux = df.groupby(tranches, observed=True).failure.mean()
taux.index = [round(i.mid, 2) for i in taux.index]
st.subheader(f"Taux de panne par {variable}")
st.bar_chart(taux)

# 4. Nuage de points température / vibration
df_nuage = df.copy()
df_nuage["Panne"] = df_nuage["failure"].map({0: "Non", 1: "Oui"})
st.subheader("Température et vibration")
st.scatter_chart(
    df_nuage,
    x="temperature_c",
    y="vibration_mm_s",
    color="Panne"
)
```

**Valeurs calculées à partir de `data/sensors.csv` :**

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5 000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

**Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?**

Le taux de panne augmente globalement avec le niveau de vibration. Cette évolution n'est pas parfaitement régulière entre toutes les tranches, car les données synthétiques comportent une part aléatoire.

Cela montre qu'une vibration plus élevée est associée à un risque de panne plus important dans ce jeu de données.

**Ajoutez `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?**

Le message `relance` apparaît dans le terminal lorsque Streamlit réexécute le script.

Streamlit réexécute automatiquement le script lorsqu'une interaction avec un widget déclenche une mise à jour. Cependant, dans mon application, les curseurs de prédiction sont placés dans un formulaire (`st.form`). Leurs modifications sont regroupées et envoyées lorsque l'utilisateur clique sur le bouton « Prédire ».

Cela montre que Streamlit fonctionne selon un mécanisme de réexécution du script à la suite des interactions de l'utilisateur.

**À quoi sert `@st.cache_data` sur la fonction `charger` ?**

Le décorateur `@st.cache_data` permet de mettre en cache le résultat de la lecture du fichier CSV.

Ainsi, lorsque Streamlit réexécute le script avec les mêmes arguments, il réutilise le DataFrame déjà chargé au lieu de relire le fichier à chaque interaction. Cela améliore les performances de l'application.

## 4. Sprint 2 : l'onglet « Prédiction »

**Méthode `predict` dans `maintai/client.py` :**

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""

    headers = {}

    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    if r.status_code != 200:
        raise APIError(r.status_code, r.json().get("detail"))

    return r.json()
```

**Dernière ligne de `python -m pytest` à la fin du sprint 2 :**

```text
=============================== 23 passed, 1 warning in 7.05s ================================
```

Les 23 tests sont réussis. L'avertissement restant est un `StarletteDeprecationWarning` concernant l'utilisation de `httpx` avec `starlette.testclient`. Il ne représente pas un échec de test.

**Avec l'API lancée, résultats des essais :**

| Essai | Ce qu'affiche Streamlit |
|---|---|
| Valeurs par défaut, bonne clé | Probabilité de panne : **95 %**. Message : « ALERTE : risque de panne détecté ! » |
| Valeurs par défaut, fausse clé | Le code prévoit un avertissement « Erreur 401 » indiquant que la clé API est absente ou invalide. |
| API arrêtée (Ctrl+C dans le terminal Uvicorn) | Le code prévoit un message « API injoignable », suivi du détail de l'erreur de connexion. |

**Vérification directe de l'API :**

Lors du premier essai, l'API a indiqué que le modèle n'était pas chargé. J'ai donc exécuté :

```powershell
python -m maintai.train
```

Le modèle a été entraîné et sauvegardé dans `models/model.joblib`.

Les métriques obtenues pendant l'entraînement étaient :

| Métrique | Modèle | Baseline |
|---|---:|---:|
| Accuracy | 0,904 | 0,864 |
| Recall | 0,75 | 0,0 |
| Precision | 0,622 | Non indiquée |
| Seuil | 0,3 | Non indiqué |

Après le redémarrage de l'API et la configuration de la clé API, une requête POST a retourné :

```text
failure_probability : 0.9553
alert               : True
threshold           : 0.3
```

La probabilité de panne obtenue était donc de **95,53 %**, avec une alerte activée.

Dans l'interface Streamlit, le résultat est arrondi à **95 %**.

**Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?**

Le navigateur communique avec le serveur Streamlit sur le port 8501. Ensuite, le code Python de Streamlit envoie la requête à l'API FastAPI avec la bibliothèque `httpx`.

La requête vers l'API est donc effectuée côté serveur Python et non directement depuis le navigateur. La politique CORS du navigateur ne bloque donc pas cet appel.

## 5. Questions de compréhension

**1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**

Dans le TP2, c'est le JavaScript exécuté dans le navigateur qui envoie la requête à l'API à l'aide de `fetch()`.

Dans le TP3, c'est le code Python de Streamlit qui envoie la requête avec le client `MaintaiClient` et la bibliothèque `httpx`.

La différence principale concerne donc l'endroit où la requête HTTP est exécutée : dans le navigateur pour le TP2 et côté serveur Python pour le TP3.

**2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'Uvicorn ?**

Les tests utilisent le `TestClient` de FastAPI pour envoyer des requêtes directement à l'application ASGI en mémoire.

Le client de test est injecté dans `MaintaiClient`, ce qui permet de tester les requêtes et les réponses de l'API sans démarrer un véritable serveur Uvicorn.

Cela rend les tests plus rapides et indépendants du démarrage d'un serveur réseau.

**3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?**

Pour une démonstration rapide à un client, je choisirais Streamlit, car il permet de développer rapidement une interface interactive pour visualiser les données et tester les prédictions du modèle.

Pour une application quotidienne destinée aux techniciens de maintenance, je privilégierais une interface HTML + JavaScript personnalisée. Elle offre davantage de liberté pour adapter l'expérience utilisateur aux besoins métier, aux appareils utilisés et aux fonctionnalités spécifiques des techniciens.



## 6. Le rendu Git

- **Lien du dépôt GitHub :**- **Lien du dépôt GitHub :** https://github.com/ZainaBelgas/Applications-intelligentes
- **Lien de la Pull Request :** Aucune Pull Request ouverte actuellement. Les Pull Requests existantes sont fermées.
- **Le tag `tp3` existe sur GitHub :** Oui, il a été créé et pointe vers le commit `6c06bb7` de la branche `main`.
- **`git status` avant le commit :** `On branch main`, `Your branch is up to date with 'origin/main'`, `nothing to commit, working tree clean`.

Le fichier `.env` contient des informations de configuration sensibles, notamment la clé API. Il ne doit pas être envoyé sur GitHub.

Le fichier `data/sensors.csv` et le modèle `models/model.joblib` doivent être gérés conformément aux consignes du TP et aux règles définies dans le `.gitignore`.

Le dossier local fourni ne permet pas de confirmer l'existence de la Pull Request ni du tag GitHub.

## 7. Ce qui reste flou

Le point qui reste à approfondir concerne l'avertissement `StarletteDeprecationWarning` affiché pendant les tests.

Il indique que l'utilisation de `httpx` avec `starlette.testclient` est dépréciée et recommande l'installation de `httpx2`. Je souhaite mieux comprendre les conséquences de cet avertissement et la manière de mettre à jour les dépendances sans perturber les tests existants.

## Conclusion

Ce TP3 m’a permis de concevoir une interface Streamlit reliée à une API FastAPI afin de consulter les données des capteurs et de prédire les risques de panne.

J’y ai intégré des indicateurs statistiques, des graphiques interactifs et un formulaire de prédiction, ainsi qu’une gestion des erreurs lors des échanges avec l’API.

Les difficultés rencontrées concernant le chargement des données, l’accès au modèle et la présentation des résultats ont été résolues. Les prédictions fonctionnent désormais et les **23 tests automatisés** passent avec succès.

L’application dispose ainsi d’une interface fonctionnelle qui facilite l’utilisation du modèle de maintenance prédictive.


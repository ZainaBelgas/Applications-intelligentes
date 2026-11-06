# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** Groupe 1  ·  **Membres :** Zainab BELGAS  ·  **Date :** 05/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed, 1 warning in 1.28s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Sans avoir rien codé, on a déjà 4 tests verts : `test_health`, `test_openapi_documents_predict`, `test_missing_field_is_rejected` et `test_out_of_range_value_is_rejected`. Les deux derniers attendent un 422 et l'obtiennent, mais pas pour la bonne raison. Au départ, `SensorReading` ne contient aucun champ, et avec `extra="forbid"` Pydantic rejette tout champ qu'il ne connaît pas. Résultat : n'importe quelle requête est rejetée en 422, y compris une requête correcte. Le test sur la température de 500 °C réussit donc par hasard : l'API ne contrôle pas la température, elle bloque simplement tout ce qui arrive.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Un moteur peut être dans un local très froid (-40 °C) ; à 150 °C l'isolant des bobinages est détruit, une valeur plus haute n'a pas de sens. |
| `vibration_mm_s` | float | 0 | 50 | Une vitesse de vibration est toujours positive ou nulle, et au-dessus de 50 mm/s la machine est en train de se casser. |
| `load_pct` | float | 0 | 100 | La charge est exprimée en pourcentage de la capacité nominale, donc entre 0 et 100. |
| `runtime_hours` | float | 0 | 100 000 | Le compteur d'heures commence à 0 ; 100 000 h correspondent à plus de 11 ans de fonctionnement sans arrêt. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
3 failed, 10 passed, 1 warning in 1.75s
```

Le nombre d'échecs ne change pas (3), mais la cause n'est plus la même : on n'a plus de 422, on a une `NotImplementedError`. Cette erreur vient de `predict()`, qui n'est pas encore codée. C'est encourageant : si on arrive dans `predict()`, c'est que la requête a été validée. Le schéma laisse donc bien passer les relevés corrects.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle n'est pas chargé. Lancer python -m maintai.train puis relancer l'API.",
        )
    resultat = predictor.predict(reading.model_dump())
    return PredictionOut(**resultat)
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Le code 500 indique une erreur interne, autrement dit un bug dans le programme. Ce n'est pas le cas ici : le code fonctionne, il manque seulement le fichier du modèle. Le code 503 (Service Unavailable) indique que le service ne peut pas répondre pour l'instant mais que la situation est temporaire. Avec le message d'erreur, le client sait aussi comment régler le problème (entraîner le modèle puis redémarrer).

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Charger `model.joblib` demande de lire le fichier sur le disque puis de recréer l'objet en mémoire, ce qui est lent. Comme le modèle reste le même d'une requête à l'autre, le recharger à chaque appel ferait perdre du temps et des ressources pour rien. Il est donc chargé au lancement, dans la fonction `lifespan`, et stocké dans `state` ; ensuite toutes les requêtes utilisent ce même objet.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
18 passed, 1 warning in 1.76s
```

On a 18 tests : les 13 fournis avec le TP et les 5 que j'ai ajoutés pour l'activité 1 (`tests/test_casser.py`). Le warning ne vient pas de notre code mais de la bibliothèque `starlette`.

Sortie de `ruff check .` :

```
All checks passed!
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-05T10:53:40Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

(Les valeurs `failure_probability` et `model_version` dépendent de ton entraînement : recopie ce que **toi** tu obtiens dans `/docs`.)

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

Elles se trouvent en bas de la page `/docs`, dans la partie **Schemas**. En ouvrant `SensorReading`, on voit pour chaque champ le type (`number`), la description, et les valeurs `minimum` et `maximum` définies dans le code. On les retrouve aussi en ouvrant `POST /v1/predict` puis l'onglet Schema du corps de la requête. FastAPI génère cette documentation tout seul à partir du modèle Pydantic.

### Activité 1 · Casser son API

| Cas | Requête (corps ou URL) | Prévu | Obtenu |
|---|---|---|---|
| champ manquant | relevé sans `load_pct` | 422 | 422 |
| valeur absurde | `load_pct` = 250 | 422 | 422 |
| texte au lieu d'un nombre | `temperature_c` = "chaud" | 422 | 422 |
| champ en trop | relevé valide + `"couleur": "rouge"` | 422 | 422 |
| mauvaise route | `POST /v1/predicte` | 404 | 404 |

Au lieu d'écrire cinq fonctions de test presque identiques, j'ai écrit une seule fonction `test_requete_refusee` dans `tests/test_casser.py`, avec le décorateur `@pytest.mark.parametrize`. Les cinq cas sont rangés dans la liste `CAS_REFUSES` ; pytest exécute la fonction une fois par cas, ce qui fait 5 tests au total.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST n'est pas un outil, c'est une façon de concevoir une API web : des adresses lisibles, les méthodes HTTP (GET, POST…), des codes de réponse adaptés, des échanges en JSON et un numéro de version. FastAPI est un framework Python qui sert à coder concrètement une API. On utilise FastAPI pour construire une API qui respecte les principes REST.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   D'abord la **validation** : chaque requête est vérifiée avant d'entrer dans la fonction, et une température de 500 °C est rejetée avec un 422. Ensuite la **documentation** : les champs, leurs types et leurs bornes apparaissent automatiquement dans `/docs`. Enfin, la fonction reçoit un **objet Python typé** : `reading.temperature_c` est un float déjà contrôlé, on peut l'utiliser directement.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` désigne mon propre ordinateur, c'est là que tourne le serveur. `8000` est le numéro de port sur lequel uvicorn attend les requêtes. `/v1/predict` est la route : un chemin déclaré dans le code Python, qui ne correspond à aucun dossier sur le disque. La partie `/v1` indique la version de l'API.
4. Pourquoi `/v1` dans l'adresse ?
   Le `/v1` permet de faire évoluer l'API sans casser ce qui existe. Si un jour le format d'entrée ou de sortie change, on publie la nouvelle version sous `/v2`, et les applications qui appellent encore `/v1` continuent de fonctionner.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   La partie avant les deux-points, `maintai.api.main`, est le chemin du module Python : c'est le fichier `maintai/api/main.py`, écrit avec des points à la place des `/` et sans l'extension. La partie après, `app`, est le nom de la variable de ce fichier qui contient l'objet `FastAPI(...)`, c'est-à-dire l'application que uvicorn doit lancer.

## 7. Le rendu Git

- Lien de la pull request : [colle le lien ici]
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  [nom du relecteur] : [son commentaire]

## 8. Ce qui reste flou

Je ne vois pas encore très bien à quoi sert `reading.model_dump()` : pourquoi faut-il transformer l'objet en dictionnaire avant de le donner au modèle ? Je ne comprends pas non plus complètement la différence entre `response_model=PredictionOut` dans le décorateur et le type de retour `-> PredictionOut` de la fonction, puisque les deux semblent dire la même chose.

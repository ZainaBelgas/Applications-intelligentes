# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** Groupe 1  ·  **Membres :** Marwa Elomari Alaoui  ·  **Date :** 05/11/2026


---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed, 1 warning in 1.28s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Les 4 tests qui passent sont `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`. Les deux premiers attendant un 422 passent pour une mauvaise raison : le schéma `SensorReading` est vide et `extra="forbid"` refuse tout champ inconnu. Donc n'importe quel corps JSON, même un relevé parfaitement valide, est refusé avec un 422. Le test « 500 °C donne 422 » est vert, mais l'API ne vérifie en réalité aucune température : elle refuse tout.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | float | -40 | 150 | Plage d'un moteur industriel, du grand froid d'un atelier à une température qui détruit l'isolation des bobinages. |
| `vibration_mm_s` | float | 0 | 50 | Une vitesse de vibration n'est jamais négative ; au-delà de 50 mm/s la machine se détruit. |
| `load_pct` | float | 0 | 100 | C'est un pourcentage de la capacité nominale. |
| `runtime_hours` | float | 0 | 100 000 | Un compteur d'heures n'est pas négatif ; 100 000 h font environ 11 ans de marche continue. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
3 failed, 10 passed, 1 warning in 1.75s
```

Il y a toujours 3 échecs, mais l'erreur n'est plus un 422 : c'est `NotImplementedError`, levée par le corps de `predict()` qui n'est pas encore écrit. C'est un bon signe, car cela prouve que le schéma accepte maintenant les relevés valides : la requête a passé la validation et est arrivée jusqu'à la fonction `predict()`.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API",
        )
    return PredictionOut(**predictor.predict(reading.model_dump()))
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Un 500 signifie « erreur du serveur » : un bug dans le code. Ici le code est correct, c'est le service qui n'est pas disponible tant que le modèle n'a pas été entraîné. Le 503 (service indisponible) dit au client que le problème est temporaire et du côté du serveur, et notre message lui dit quoi faire.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Lire `model.joblib` sur le disque et le reconstruire en mémoire prend du temps. Le faire à chaque requête ralentirait chaque réponse et gaspillerait des ressources, alors que le modèle ne change pas entre deux requêtes. On le charge donc une fois dans `state` au démarrage (fonction `lifespan`), puis chaque requête le réutilise.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
18 passed, 1 warning in 1.76s
```

(13 tests fournis + 5 tests de l'activité 1 dans `tests/test_casser.py`. Le warning vient de la bibliothèque `starlette` et pas de notre code.)

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

Dans `/docs`, on déplie `POST /v1/predict` puis la section **Schemas** → `SensorReading` : chaque champ y apparaît avec son type (`number`), son minimum, son maximum et sa description. C'est FastAPI qui construit cette page à partir du schéma Pydantic.

### Activité 1 · Casser son API

| Cas | Requête (corps ou URL) | Prévu | Obtenu |
|---|---|---|---|
| champ manquant | relevé sans `load_pct` | 422 | 422 |
| valeur absurde | `load_pct` = 250 | 422 | 422 |
| texte au lieu d'un nombre | `temperature_c` = "chaud" | 422 | 422 |
| champ en trop | relevé valide + `"couleur": "rouge"` | 422 | 422 |
| mauvaise route | `POST /v1/predicte` | 404 | 404 |

Ces cinq cas sont devenus un seul test `test_requete_refusee` dans `tests/test_casser.py`, avec `@pytest.mark.parametrize` : pytest lance la même fonction cinq fois, une par ligne de la liste `CAS_REFUSES`, et compte donc 5 tests.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un ensemble de règles pour concevoir une API web (URL claires, méthodes HTTP, codes précis, JSON, version). FastAPI est la bibliothèque Python qui permet d'écrire une API qui suit ces règles. On écrit donc une API REST *avec* FastAPI.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Il sert à **valider** chaque requête avant d'appeler la fonction (un 500 °C est refusé en 422), à **documenter** l'API dans `/docs` (champs, types, bornes, exemple), et à **donner un objet Python typé** à la fonction (`reading.temperature_c` est déjà un float vérifié).
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` est la machine elle-même (le serveur tourne sur mon PC). `8000` est le port, la « porte » sur laquelle uvicorn écoute. `/v1/predict` est la route, un chemin défini dans le code Python (et pas un dossier du disque) ; `/v1` est la version de l'API.
4. Pourquoi `/v1` dans l'adresse ?
   Pour versionner le contrat de l'API. Si on doit le changer plus tard, on peut créer `/v2` sans casser les clients qui utilisent encore `/v1`.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le fichier `maintai/api/main.py` écrit avec des points et sans `.py`. `app` est la variable de ce fichier qui contient l'application (`app = FastAPI(...)`).

## 7. Le rendu Git

- Lien de la pull request : (https://github.com/ZainaBelgas/Applications-intelligentes/pull/1)


## 8. Ce qui reste flou

Le rôle exact de la fonction `lifespan` dans `main.py` (comment FastAPI sait qu'elle doit s'exécuter au démarrage et à l'arrêt) n'est pas encore tout à fait clair pour moi. Je voudrais aussi mieux comprendre ce que fait `git pull` quand il fusionne des commits (le « merge » automatique).

# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Nom :** Marwa Elomari Alaoui  ·  **Établissement :** EMSI Casablanca (IADA)  ·  **Groupe :** G51
**Cours :** Développement et déploiement d'applications intelligentes · Séance 5  ·  **Date :** 05/11/2026
**Membres du groupe :** Marwa Elomari Alaoui, *(noms des coéquipiers)*

## Sommaire

1. Activité 1 : casser son API
2. ruff
3. Mise en place du TP2
4. La clé API (sprint 1)
5. La page web (sprint 2) et CORS
6. Les tests de l'activité 1 dans le TP2
7. Questions de compréhension
8. Le rendu Git
9. Ce qui reste flou

## Récapitulatif (critères de réussite du TP2)

| Critère | Résultat |
|---|---|
| 18 tests passent (23 avec `test_casser.py`) | oui : 23 passed |
| Sans clé, 401 | oui |
| `/health` reste public | oui (200 sans clé) |
| La page prédit depuis l'origine autorisée et échoue depuis l'autre | oui : 5600 autorisé / 5601 refusé (5500 bloqué par Windows, voir section 5) |
| `.env` n'est pas dans Git | oui (ignoré par `.gitignore`) |
| ADR 003 rempli (`docs/adr/003-securite.md`) | oui |
| Pull request fusionnée et tag `tp2` | voir section 8 |

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant (`load_pct` absent) | 422 | 422 |
| 2 | valeur absurde (`load_pct` = 250) | 422 | 422 |
| 3 | texte au lieu d'un nombre (`temperature_c` = "chaud") | 422 | 422 |
| 4 | champ en trop (`couleur` = "rouge") | 422 | 422 |
| 5 | mauvaise route (`/v1/predictt`) | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Aucune. Les quatre premiers cas sont refusés par la validation Pydantic (`schemas.py` : bornes `ge`/`le`, type `float`, `extra="forbid"`), donc 422. Le cinquième ne correspond à aucune route : FastAPI répond 404 avant même de regarder le corps. (Piège : en TP2 sans clé, les cinq premiers cas donneraient 401, voir partie 6.)

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
18 passed
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

Il lance la même fonction de test une fois par ligne de la liste `CAS_REFUSES`, en nommant chaque cas dans le rapport. pytest compte donc **5 tests** pour une seule fonction (13 + 5 = 18), et un cas qui échoue est identifié séparément des autres.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff` lit le code **sans l'exécuter** et signale ce qui est mal écrit (import inutile F401, imports mal rangés I001, variable inutilisée). `pytest` **exécute** le code et vérifie ce qu'il fait (codes de réponse, comportement du modèle). Il faut les deux : ruff avant chaque commit, pytest avant chaque push.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
2 failed, 16 passed
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

`test_missing_key_is_rejected` (sans clé) et `test_wrong_key_is_rejected` (fausse clé). Comme aucune protection n'est branchée, l'API répond **200** (et la prédiction) au lieu de 401.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    settings = get_settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API requise",
        )

    if not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API incorrecte",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Toujours **2** : la fonction existe, mais rien ne l'appelle. Le router n'a pas encore `dependencies=[Depends(require_api_key)]`, donc les routes `/v1` s'exécutent sans contrôle de clé.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
18 passed
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API requise"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API incorrecte"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.0027,"alert":false,"threshold":0.3,"model_version":"..."}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API requise"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150",...}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Les contrôles s'enchaînent dans l'ordre route, clé, données, modèle ; le premier qui échoue répond. Sans clé, la dépendance `require_api_key` échoue d'abord : **401**, et l'API ne regarde même pas les données. Avec la bonne clé, on passe le contrôle de la clé et c'est le schéma qui refuse 500 °C (> 150) : **422**.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

**500** (`{"detail":"Clé API non configurée"}`). Sans `.env` chargé, `get_settings().api_key` vaut `None` : c'est une erreur du **serveur** (il n'a pas de clé à comparer), pas une faute du client. 401 voudrait dire « votre clé est fausse », ce qui serait faux.

## 5. La page web (sprint 2)

> **Note sur le port 5500 (problème rencontré).** Sur mon PC, `python -m http.server 5500 -d web` échoue avec
> `PermissionError: [WinError 10013] Une tentative d'accès à un socket de manière interdite par ses autorisations d'accès a été tentée` :
> Windows refuse d'ouvrir le port 5500 (port déjà utilisé ou réservé par le système). Je n'ai donc pas pu servir la page sur 5500.
> Solution : j'ai pris un autre port, **5600**, à la place de 5500 (port « autorisé »), et **5601** à la place de 5501 (port « refusé »).
> Pour que le principe reste le même, j'ai changé la liste des origines dans `.env` :
>
> ```
> MAINTAI_CORS_ORIGINS=http://localhost:5600,http://127.0.0.1:5600
> ```
>
> puis relancé uvicorn avec `python -m uvicorn maintai.api.main:app --reload --env-file .env` (la liste est lue au démarrage).
> Dans la suite, « port 5500 » du sujet = **5600** chez moi, et « port 5501 » = **5601**. Le raisonnement ne change pas :
> une page servie depuis une origine présente dans `MAINTAI_CORS_ORIGINS` peut appeler l'API, une autre origine est bloquée par le navigateur.
> (Les tests automatiques `test_cors_*` ne dépendent pas de ce changement : ils utilisent les origines par défaut.)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
  const base = document.getElementById("url").value.replace(/\/+$/, "");
  const cle = document.getElementById("key").value;
  const adresse = base + "/v1/predict";
  try {
    const resp = await fetch(adresse, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle },
      body: JSON.stringify(reading),
    });
    const data = await resp.json();
    if (!resp.ok) {
      const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      show("err", "Erreur " + resp.status + " : " + detail);
    } else {
      const pct = (data.failure_probability * 100).toFixed(1);
      show(data.alert ? "alert" : "ok",
        (data.alert ? "ALERTE : " : "OK : ") + "probabilité de panne " + pct + " % (seuil " + data.threshold + ")");
    }
  } catch (e) {
    show("err", "API injoignable (arrêtée, ou bloquée par CORS) : " + e.message);
  }
```

Ce qu'affiche la page (servie sur le port 5500 du sujet, soit **5600** chez moi, voir la note ci-dessus) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | encadré vert : `OK : probabilité de panne 0.3 % (seuil 0.3)` (ou rouge « ALERTE » avec le relevé par défaut 72 °C / 6 mm/s / 85 % / 15000 h : probabilité ≈ 95 %) |
| 500 °C, bonne clé | encadré orange : `Erreur 422 : [{"type":"less_than_equal", ... "Input should be less than or equal to 150" ...}]` |
| relevé normal, fausse clé | encadré orange : `Erreur 401 : Clé API incorrecte` |

**Expérience CORS.** Servez la page sur le port 5501 (chez moi **5601**, port absent de `MAINTAI_CORS_ORIGINS`). Que dit la page, et que dit la console (F12) ?

La page affiche « API injoignable (arrêtée, ou bloquée par CORS) » (le `fetch` lève une exception, il n'y a pas de réponse lisible). La console indique que la requête vers `http://localhost:8000/v1/predict` est bloquée par la politique CORS : l'en-tête `Access-Control-Allow-Origin` est absent, car `http://localhost:5501` n'est pas dans `MAINTAI_CORS_ORIGINS`. Côté serveur, la requête `OPTIONS` reçoit 400 « Disallowed CORS origin » (vérifié par `curl`).

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 (5601 chez moi) est bloquée ?

CORS est une règle **du navigateur** : il protège l'utilisateur contre une page qui utiliserait son navigateur pour appeler l'API. `curl.exe` n'est pas un navigateur, il n'envoie pas de pré-requête `OPTIONS` et ne vérifie pas `Access-Control-Allow-Origin`. Ce n'est donc pas une protection de l'API : seule la clé protège l'API.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

**4 échouent**, avec **401** au lieu de 422 (la clé est vérifiée avant les données). Le cas « mauvaise route » passe quand même : `/v1/predictt` n'existe pas, donc 404 est renvoyé avant que la dépendance de clé du router `/v1` ne s'exécute.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
23 passed
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 = non authentifié (clé absente ou fausse : « qui es-tu ? ») ; 422 = requête bien authentifiée mais données invalides (le schéma les refuse). 403 = identifié mais sans le droit d'accéder à la ressource (autorisation, hors TP2) ; 401 = identité non établie.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   Ce qui est commité reste dans l'historique de Git pour toujours, même supprimé ensuite : il faudrait alors changer la clé. `.env` contient la vraie clé et reste sur le PC (ignoré par `.gitignore`) ; `.env.example` contient une fausse valeur et dit quoi configurer : c'est lui qui est commité.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Une URL est enregistrée partout (journaux du serveur, historique du navigateur, Referer) ; un en-tête n'y apparaît pas.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   Il compare en temps constant : `==` s'arrête au premier caractère différent, et la durée de la réponse trahirait combien de caractères sont justes (attaque par mesure du temps).
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` (5600 chez moi) et `http://localhost:8000` sont-elles la même origine ?
   Une origine = schéma + domaine + port. Non : les ports diffèrent (5500 et 8000), ce sont deux origines différentes, d'où le besoin de CORS.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/ZainaBelgas/Applications-intelligentes/pull/NUMERO
- Le tag `tp2` existe sur GitHub : oui
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non (il est ignoré par le `.gitignore`)
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  Marwa Elomari Alaoui : «- Lien de la pull request : https://github.com/ZainaBelgas/Applications-intelligentes/pull/NUMERO
- Le tag `tp2` existe sur GitHub : oui
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non (il est ignoré par le `.gitignore`)
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  Marwa Elomari Alaoui : « Les 18 tests passent chez moi, aucun fichier .env dans les changements, l'ADR 003 justifie bien l'en-tête et la liste d'origines CORS.»

## 9. Ce qui reste flou

- La différence concrète entre **authentification** (401) et **autorisation** (403) : en TP2 il n'y a qu'une seule clé pour tout le monde, donc je n'ai pas pu voir un cas de 403.
- Comment CORS se comporte avec d'autres méthodes ou en-têtes que `POST` et `X-API-Key` (requêtes « préalables » OPTIONS plus complexes).
- Comment gérer les clés en production (séance 8) : variable du serveur, rotation, une clé par client.

Difficultés rencontrées : le port 5500 refusé par Windows (`WinError 10013`, voir section 5) ; un ancien `.venv` copié depuis une autre machine (chemins invalides, `uvicorn.exe` introuvable), résolu en recréant l'environnement et en utilisant `python -m uvicorn` et `python -m pytest`.

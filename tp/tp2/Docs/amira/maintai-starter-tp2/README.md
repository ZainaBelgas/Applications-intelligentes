# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** Groupe 1  ·  **Membres :** Amira Zahr  ·  **Date :** 05/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | champ manquant (pas de `load_pct`) | 422 | 422 |
| 2 | valeur absurde (`load_pct` = 250) | 422 | 422 |
| 3 | texte au lieu d'un nombre (`temperature_c` = "chaud") | 422 | 422 |
| 4 | champ en trop (`"couleur": "rouge"`) | 422 | 422 |
| 5 | mauvaise route (`POST /v1/predicte`) | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Non, les cinq codes obtenus sont ceux que j'avais prévus. J'avais un doute pour le cas 3, parce que Pydantic sait convertir un texte comme `"72.5"` en nombre. Mais `"chaud"` ne peut pas devenir un float, donc la validation échoue et on a bien un 422. Pour le cas 5, l'erreur ne vient pas de Pydantic : la route n'existe pas, donc FastAPI répond 404 avant même de lire le corps.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
18 passed, 1 warning in 1.76s
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

Il permet de lancer la même fonction de test avec plusieurs jeux de valeurs, sans recopier le code. Ma fonction `test_requete_refusee` reçoit à chaque fois une route, un corps JSON et le code attendu. Comme la liste `CAS_REFUSES` contient 5 cas, pytest compte 5 tests séparés (un par cas), et si un seul cas échoue on voit tout de suite lequel.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff` lit le code sans l'exécuter. Il cherche les problèmes de style et les erreurs faciles à repérer : imports inutilisés, variables jamais utilisées, imports mal rangés, etc. `pytest`, lui, exécute vraiment le code à travers les tests et vérifie que le résultat est le bon (par exemple qu'une température de 500 donne un 422). Un code peut passer ruff et être faux, ou être juste et mal écrit : les deux outils sont complémentaires.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
2 failed, 16 passed, 1 warning in 1.44s
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Ce sont `test_missing_key_is_rejected` et `test_wrong_key_is_rejected` dans `tests/test_security.py`. Ils reçoivent un **200** au lieu de 401 : au départ rien ne protège `/v1/predict`, donc la requête sans clé (ou avec une fausse clé) est acceptée et le modèle répond normalement.

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

Toujours 2, les mêmes qu'au départ (`2 failed, 16 passed`). La fonction existe, mais personne ne l'appelle : tant qu'elle n'est pas déclarée comme dépendance du router, FastAPI ne l'exécute jamais avant `predict()`. Écrire la vérification ne suffit pas, il faut aussi la brancher sur les routes.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
18 passed, 1 warning in 1.06s
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API requise"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API incorrecte"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-05T11:34:10Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API requise"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

C'est une question d'ordre. La dépendance `require_api_key` du router est vérifiée en premier : sans clé, la requête est arrêtée tout de suite avec un 401 et le corps n'est même pas regardé. Avec la bonne clé, la requête passe ce contrôle, puis Pydantic valide le relevé et refuse les 500 °C avec un 422. On ne dit donc rien sur les données à quelqu'un qui n'est pas autorisé.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

On obtient **500** avec `{"detail":"Clé API non configurée"}`. Sans `--env-file .env`, la variable `MAINTAI_API_KEY` n'est pas chargée, donc `get_settings().api_key` vaut `None`. Ce n'est pas le client qui s'est trompé (sa clé est peut-être bonne), c'est le serveur qui est mal configuré : un 401 accuserait le client à tort, alors qu'un 500 dit que le problème est côté serveur.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
const base = document.getElementById("url").value.replace(/\/$/, "");
const key = document.getElementById("key").value;
try {
  const r = await fetch(base + "/v1/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": key },
    body: JSON.stringify(reading),
  });
  if (r.ok) {
    const data = await r.json();
    const pct = (data.failure_probability * 100).toFixed(1);
    show(data.alert ? "alert" : "ok",
      (data.alert ? "ALERTE : " : "OK : ") + "probabilité de panne " + pct + " %");
  } else if (r.status === 401) {
    show("err", "Clé API refusée (401)");
  } else if (r.status === 422) {
    show("err", "Valeurs refusées (422) : vérifiez les bornes");
  } else {
    show("err", "Erreur du serveur (" + r.status + ")");
  }
} catch (e) {
  show("err", "Impossible de joindre l'API : serveur éteint ou requête bloquée (CORS)");
}
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | ALERTE : probabilité de panne 94.8 % (fond rouge) |
| 500 °C, bonne clé | Valeurs refusées (422) : vérifiez les bornes |
| relevé normal, fausse clé | Clé API refusée (401) |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche « Impossible de joindre l'API : serveur éteint ou requête bloquée (CORS) », alors que le serveur tourne bien. Dans la console on lit une erreur du type : `Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.` Le navigateur envoie d'abord une requête `OPTIONS` (le preflight), l'API répond sans autoriser l'origine 5501 (elle n'est pas dans `MAINTAI_CORS_ORIGINS`), donc le navigateur n'envoie jamais le vrai `POST`.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

Le CORS n'est pas une protection du serveur, c'est une règle appliquée par le navigateur. Le navigateur protège l'utilisateur : il empêche une page d'un site de lire les réponses d'un autre site sans son accord. `curl.exe` n'est pas un navigateur, il n'envoie pas de preflight et ne vérifie pas les en-têtes `Access-Control-Allow-Origin`, donc il reçoit la réponse normalement. C'est pour ça que la vraie sécurité de l'API, c'est la clé, pas le CORS.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

4 tests échouent (`4 failed, 19 passed`) : les quatre cas qui attendaient un 422 reçoivent maintenant un **401**, car sans clé la requête est refusée avant la validation du corps. Le cas qui passe quand même est la mauvaise route `/v1/predicte` : cette route n'existe pas, donc FastAPI renvoie 404 directement. La dépendance `require_api_key` est attachée aux routes du router, et comme aucune route ne correspond, elle n'est jamais appelée.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
23 passed, 1 warning in 1.21s
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 veut dire « je ne sais pas qui tu es » : il manque une authentification valide (ici la clé). 422 veut dire que la requête est bien autorisée mais que son contenu est invalide (champ manquant, valeur hors bornes…). Entre 401 et 403 : avec 401 le client n'est pas identifié, avec 403 il est identifié mais n'a pas le droit de faire cette action. Dans notre API on n'a qu'une seule clé et pas de niveaux de droits, donc on n'utilise que 401.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   Tout ce qui est dans Git peut être lu par tous ceux qui ont accès au dépôt, et reste dans l'historique même si on l'efface ensuite. Si la clé était dans le code, n'importe qui pourrait l'utiliser. `.env` contient la vraie clé et les origines CORS ; il est dans le `.gitignore` et n'est jamais commité. `.env.example` est commité : il montre quelles variables il faut définir, avec des valeurs d'exemple, pour qu'un autre développeur sache quoi mettre dans son propre `.env`.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Une URL est enregistrée un peu partout : historique du navigateur, logs du serveur, logs des proxys, et elle peut être copiée ou partagée par erreur. Une clé dans l'URL finirait donc écrite en clair dans plein d'endroits. Un en-tête comme `X-API-Key` n'apparaît pas dans l'adresse et n'est en général pas enregistré dans les logs.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   `==` s'arrête au premier caractère différent, donc la comparaison est un peu plus rapide quand le début de la clé est faux. En mesurant ces temps de réponse, un attaquant pourrait deviner la clé caractère par caractère (attaque temporelle). `secrets.compare_digest` met toujours le même temps, quel que soit l'endroit où les deux chaînes diffèrent, ce qui empêche cette attaque.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine, c'est le trio protocole + nom d'hôte + port. Il suffit qu'un seul des trois change pour que ce soit une autre origine. `http://localhost:5500` et `http://localhost:8000` ont le même protocole et le même hôte, mais pas le même port : ce sont donc deux origines différentes, et c'est pour ça qu'il faut configurer le CORS pour que la page puisse appeler l'API.

## 8. Le rendu Git

- Lien de la pull request : [colle le lien ici]
- Le tag `tp2` existe sur GitHub : oui / non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non (il est listé dans `.gitignore`)
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  [nom du relecteur] : [son commentaire]

## 9. Ce qui reste flou

Je ne comprends pas encore bien comment FastAPI décide de l'ordre entre la dépendance du router et la validation du corps : j'ai vu le résultat (401 avant 422), mais pas où c'est géré dans le code. Je me demande aussi comment on ferait si plusieurs clients avaient chacun leur propre clé, avec des droits différents (et donc des 403).

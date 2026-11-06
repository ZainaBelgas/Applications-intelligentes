# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Chaimaa Ezzerag · 5IAD · G1 · EMSI Moulay Youssef · 6 novembre 2026**

## Tests du TP2

La suite fournie donne 18 tests réussis. Après ajout des cinq cas de `tests/test_casser.py`, la suite donne 23 tests réussis. Un avertissement de dépréciation concerne le client HTTP utilisé par les tests. La vérification a été faite sous Linux avec Python 3.12.

| Requête testée avec la clé de test | Résultat observé |
|---|---|
| Champ load_pct manquant | 422 |
| Température de 500 °C | 422 |
| Température « chaud » | 422 |
| Champ inconnu supplémentaire | 422 |
| Mauvaise route /v1/predictt | 404 |

Le décorateur pytest.mark.parametrize exécute la même fonction sur cinq jeux de données. Chaque jeu compte comme un test distinct. Ruff vérifie statiquement le code, tandis que pytest exécute les scénarios et contrôle leurs résultats. Les sorties historiques de Ruff et du TP1 ne sont pas disponibles dans cette archive.

## Authentification et prédiction

La fonction require_api_key lit la configuration du serveur et compare la clé reçue. Le routeur utilise `APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])`. Définir seulement la fonction de contrôle ne suffit pas, le routeur doit l’appeler. Le détail de la décision figure dans [ADR 003](docs/adr/003-securite.md).

GET /health est public. Une requête de prédiction sans clé ou avec une fausse clé reçoit 401. Avec une clé valide et un relevé valide, le serveur renvoie la probabilité de panne et la décision d’alerte. Une température de 500 °C avec une clé valide donne 422. Sans clé, le contrôle d’accès intervient avant la validation de ce relevé. Sur une route inexistante, le routeur renvoie 404. Si la clé du serveur est absente de son environnement, la configuration est en erreur et le code prévoit 500.

## Page web et CORS

Le [client JavaScript](web/index.html) envoie le relevé en JSON à /v1/predict avec X-API-Key. Il affiche le pourcentage calculé ou un message spécifique pour 401 et 422. Une origine se définit par le protocole, le nom d’hôte et le port. Avec les valeurs par défaut, localhost:5500 est autorisé et localhost:5501 est exclu. Un navigateur contrôle la réponse CORS avant de rendre le résultat accessible à JavaScript. curl peut lire la réponse indépendamment de cette politique. Cette description vient du code, sans capture d’un essai navigateur.

## Compréhension et remise

401 indique un problème d’authentification, 403 un refus d’autorisation et 422 un contenu invalide. La clé réelle reste dans l’environnement local. Un en-tête évite de l’exposer dans les URL conservées dans les historiques et journaux. Le dépôt contient le modèle de configuration .env.example.

Le dossier data contient un marqueur .gitkeep. Pour produire le CSV puis le modèle, exécuter `python -m maintai.dataset` puis `python -m maintai.train`.

La pull request, sa relecture et le tag tp2 restent à vérifier sur GitHub. Aucun résultat historique intermédiaire ni commentaire de relecture n’est attribué à cette exécution.

# ADR 003 — Accès à la prédiction MaintAI

**Statut** — Décision appliquée au TP2.

Le diagnostic de disponibilité doit rester consultable librement. La prédiction demande une clé configurée côté serveur.

Le routeur FastAPI applique `Depends(require_api_key)` à toutes les routes sous `/v1`. Le client envoie la clé dans l’en-tête `X-API-Key`. Le serveur utilise `secrets.compare_digest` pour limiter les variations de temps de comparaison. Une clé absente ou incorrecte donne 401. Une clé serveur non configurée donne 500.

Le fichier local `.env` est ignoré par Git. Le dépôt fournit `.env.example` pour documenter les paramètres. CORS autorise les origines de développement configurées. CORS est un contrôle du navigateur, la clé protège aussi les appels directs.

Une clé partagée suffit pour cet exercice. Elle ne distingue pas les utilisateurs et sa rotation demande de mettre à jour les clients.

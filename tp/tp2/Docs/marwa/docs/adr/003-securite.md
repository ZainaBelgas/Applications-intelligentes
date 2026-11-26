# ADR 003 — Sécurisation de l’API MaintAI

## 1. Contexte

L’API MaintAI doit être accessible uniquement aux clients autorisés. Elle doit être protégée par une clé API. De plus, seule la page web exécutée depuis l’origine `http://localhost:5500` doit pouvoir appeler l’API depuis le navigateur.

## 2. Décision 1 : Transmission de la clé API

**Décision retenue :** transmettre la clé API dans l’en-tête HTTP `X-API-Key`.

Exemple :

```http
X-API-Key: ma-cle
```

**Justification :**
- La clé n’apparaît pas dans l’URL.
- Elle est séparée des données envoyées dans le corps de la requête.
- L’API peut vérifier la clé avant de traiter la demande.

**Alternatives rejetées :**
- Dans l’URL : la clé peut apparaître dans les historiques et les journaux du serveur.
- Dans le corps : la clé est mélangée aux données de la requête.

## 3. Décision 2 : Stockage de la clé API

**Décision retenue :** stocker la clé dans un fichier `.env`, lu au démarrage de l’application.

Le fichier `.env` doit être ignoré par Git. Un fichier `.env.example` peut être partagé avec une fausse valeur pour indiquer la configuration nécessaire.

**Justification :** cela évite d'exposer la véritable clé dans le code source et sur GitHub.

## 4. Décision 3 : Configuration CORS

**Décision retenue :** autoriser uniquement l’origine :

`http://localhost:5500`

L’origine `http://localhost:5501` ne doit pas être autorisée.

La liste des origines autorisées est configurée dans les variables d’environnement.

**Justification :** limiter les appels provenant de pages web non autorisées.

**Alternative rejetée :** autoriser toutes les origines avec `*`, car cela permettrait à n’importe quel site web d’essayer d’appeler l’API depuis un navigateur.

## 5. Conséquences

- Une requête sans clé ou avec une clé invalide reçoit une réponse HTTP 401.
- La route `/health` reste accessible publiquement.
- La page web servie sur le port 5500 peut appeler l’API.
- La page web servie sur le port 5501 est bloquée par CORS.
- Le fichier `.env` ne doit jamais être envoyé sur GitHub.

## 6. Conclusion

Ces décisions permettent de protéger l’API MaintAI, de sécuriser la clé API et de limiter les origines autorisées à communiquer avec le service.

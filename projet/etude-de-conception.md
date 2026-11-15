# Étude de conception – Classification de réclamations clients (ShopExpress)

Groupe : Zainab Belgas (responsable), Marwa Elomari Alaoui, Amira Zahr, Chaimaa Ezzerag · Version : finale · Date : 15/11/2026

Projet : Applications intelligentes · Sujet n°5 (assistant RAG optionnel : FAQ et conditions de vente fictives)

**Résumé en 3 lignes.** Une boutique en ligne reçoit beaucoup de réclamations écrites par ses clients. Notre système lit chaque message et trouve automatiquement (1) de quoi parle la réclamation (livraison, remboursement, produit défectueux...) et (2) si elle est urgente. Ainsi, chaque réclamation arrive directement à la bonne équipe, et les cas graves sont traités en premier.

---

## 1. Contexte et utilisateurs

- **Organisation ou situation :** « ShopExpress », entreprise fictive : boutique en ligne de produits électroniques et d'équipement pour la maison (livraison à domicile, paiement en ligne ou à la livraison). Elle reçoit environ 600 réclamations par jour (formulaire web, e-mail, chat). Aujourd'hui, une petite équipe les trie à la main : délais longs et messages envoyés à la mauvaise équipe.
- **Utilisateur principal :** le responsable du service client (et ses conseillers). Il reçoit chaque réclamation déjà classée (catégorie + priorité), la traite ou la transmet à l'équipe concernée : logistique, SAV ou facturation.

## 2. Problème et décision

- **Décision que l'utilisateur prend avec le système :** pour chaque réclamation, le système propose une **catégorie** (livraison ; produit défectueux ou non conforme ; facturation et paiement ; retour et remboursement ; compte et service client ; autre) et une **priorité** (normale / urgente). Trois cas :

| Cas | Ce qui est décidé |
|---|---|
| Le système est très sûr | Envoi automatique à l'équipe concernée |
| Le système est peu sûr (confiance sous un seuil à calibrer) | File de tri manuel : un humain décide |
| Réclamation urgente (fraude, produit dangereux, double prélèvement, menace de recours) | Alerte immédiate au responsable, quelle que soit la catégorie |

- **Fréquence :** prédiction en temps réel à chaque nouvelle réclamation (< 1 seconde) ; ré-entraînement une fois par mois, ou plus tôt en cas de dérive des données (nouveaux produits, nouvelle politique de retour...).
- **Conséquence d'une erreur, et pour qui :**
  - **Faux négatif** (urgente classée « normale » ou envoyée à la mauvaise équipe) : traitement retardé de plusieurs jours, client très mécontent qui peut quitter la boutique, risque juridique et de réputation (fraude ou produit dangereux non signalé). **C'est l'erreur la plus coûteuse** : elle touche d'abord le client, puis l'entreprise.
  - **Faux positif** (normale classée « urgente ») : perte de temps pour l'équipe, file prioritaire encombrée. Le coût est réel mais récupérable.
  - Conséquence : contrainte forte sur le **rappel de la classe urgente** (section 5). *Le rappel mesure : parmi toutes les vraies réclamations urgentes, combien le système en a trouvées.*

## 3. Approche par sous-problème

| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| 1. Classification de la catégorie (multi-classes, texte français) | **ML puis DL.** Baseline : TF-IDF + régression logistique. Modèle cible : fine-tuning de CamemBERT / DistilCamemBERT, avec seuil de confiance et file de tri manuel. | Les règles par mots-clés échouent sur les reformulations, les négations (« je n'ai pas été remboursé ») et les messages mêlant plusieurs sujets. Le TF-IDF reste la baseline : le modèle de langue n'est retenu que s'il apporte un gain mesuré. |
| 2. Détection de priorité (urgent / normal) | **Règles + ML.** Classifieur binaire sur le même texte, combiné à des règles métier (montant élevé, mots liés à la fraude ou au danger), avec pondération de la classe urgente. | Cas urgents rares (5 à 8 %) et souvent écrits sans mot évident : les règles seules les manquent ; un modèle seul peut rater des cas critiques connus. La combinaison réduit les faux négatifs. |
| 3. (Optionnel) Suggestion de réponse | **RAG.** Recherche sémantique (embeddings + base vectorielle) dans la FAQ et les CGV fictives, puis brouillon de réponse par un LLM avec citation de la source. L'agent valide avant envoi. | Une recherche par mots-clés ne trouve pas la bonne clause quand le client formule autrement. Un LLM seul pourrait inventer des délais ou des règles : il faut l'ancrer dans les vrais documents. |

*Le RAG (Retrieval-Augmented Generation) cherche d'abord les bons passages dans nos documents, puis demande à l'IA de rédiger une réponse uniquement à partir de ces passages.*

## 4. Données

| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| Réclamations publiques (type CFPB), traduites et adaptées à l'e-commerce | Base publique CFPB (données ouvertes du gouvernement américain, réutilisables ; à vérifier et citer dans le rapport) | Une partie des 8 000 à 10 000 messages | Déjà partiellement masquées, mais anonymisation à vérifier |
| Messages synthétiques générés par un LLM à partir de scénarios, relus manuellement | Produits par l'équipe ; conditions d'utilisation du LLM utilisé à vérifier | Complément pour atteindre ≥ 500 exemples par catégorie | Non (fictifs) |
| FAQ + conditions générales de vente fictives (partie RAG) | Rédigées par l'équipe (licence : propriété du groupe) | 30 à 50 pages | Non |

**Volumes et période (hypothèse à confirmer) :** environ 8 000 à 10 000 réclamations étiquetées, représentant 12 mois simulés ; minimum 500 exemples par catégorie.

**Variables clés :** texte (objet + corps) = entrée principale ; catégorie et priorité = étiquettes à prédire ; canal (formulaire, e-mail, chat) = analyse des biais ; date = découpage train/test dans le temps ; montant de la commande = aide à repérer les cas urgents (si disponible).

**Qualité des données :**

| Problème attendu | Solution prévue |
|---|---|
| Classes déséquilibrées (« autre », « urgente ») | Pondération des classes, suivi du rappel par classe |
| Étiquettes ambiguës (deux sujets) | Double annotation de 300 messages, mesure du kappa de Cohen |
| Fautes, langage SMS | Nettoyage léger, modèle robuste |
| Doublons | Suppression avant entraînement |
| Données personnelles | Anonymisation (noms, e-mails, téléphones, adresses) avant tout entraînement |

## 5. Métriques, baseline et critères d'acceptation

- **Baseline et son résultat :** TF-IDF (mots + bigrammes) + régression logistique avec pondération des classes. Résultat attendu sur le jeu de test : macro-F1 ≈ 0,70 à 0,75 (hypothèse, à mesurer dès la première semaine). *La baseline est le modèle le plus simple possible : si le modèle complexe ne fait pas nettement mieux, on garde le simple.*
- **Métrique principale et pourquoi :** macro-F1 sur la catégorie, avec la contrainte **rappel ≥ 90 % sur la classe « urgente »**. Le macro-F1 traite chaque catégorie de la même façon (même les rares), et le rappel urgent est directement lié au coût du faux négatif (section 2). Suivi secondaire : précision/rappel par classe, matrice de confusion, taux de tri manuel, précision de la classe urgente (fausses alertes) ; pour le RAG : fidélité aux sources sur 50 questions.
- **Critères d'acceptation (à ajuster après la baseline) :**
  - **Performance :** macro-F1 ≥ 0,82 sur le jeu de test **et** rappel urgent ≥ 90 %. Découpage 70 % entraînement / 15 % validation / 15 % test, stratifié par classe et séparé par date (le test contient les messages les plus récents) pour éviter les fuites.
  - **Par rapport à la baseline :** gain ≥ 8 points de macro-F1, sinon on retient le modèle simple.
  - **Technique :** latence < 200 ms (p95) par réclamation sur CPU ; taux de tri manuel < 20 %.
  - **(Si RAG) :** ≥ 90 % de réponses fidèles à la source citée sur les 50 questions de test, et aucune réponse hors périmètre sans avertissement.

## 6. Architecture prévue

```
Réclamation (formulaire / e-mail / chat)
        |
        v
[Prétraitement + anonymisation]
        |
        v
[API FastAPI] --> [Modèle catégorie] + [Modèle priorité]
        |                    |
        |              (confiance faible)
        |                    v
        |            [File de tri manuel]
        v
[Base PostgreSQL : réclamations, prédictions, retours des agents]
        |
        v
[Interface agent (Streamlit)] <--- [Assistant RAG optionnel]
        |                              (FAQ + CGV -> embeddings -> base vectorielle -> LLM)
        v
[Suivi MLflow : métriques, versions, dérive] --> ré-entraînement mensuel
```

| N° | Composant | Rôle |
|---|---|---|
| 1 | Prétraitement et anonymisation | Nettoie le texte et supprime les données personnelles |
| 2 | Service de prédiction | Renvoie catégorie, priorité et score de confiance |
| 3 | Base de données | Stocke réclamations, prédictions et corrections des agents (réutilisées comme nouvelles étiquettes) |
| 4 | Interface agent | Permet au responsable de trier, visualiser et corriger |
| 5 | Module RAG (optionnel) | Brouillon de réponse avec citation de la source |
| 6 | Suivi MLflow | Historique des expériences, versions de modèles, performances dans le temps |

## 7. Choix technologiques

| Besoin | Outil | Justification |
|---|---|---|
| Baseline rapide et reproductible | Python + scikit-learn | Simple à construire, point de comparaison fiable |
| Modèle de langue pour le français | Hugging Face Transformers (CamemBERT / DistilCamemBERT) | Déjà entraînés pour le français, utilisables avec peu de données ; la version « Distil » est plus rapide, donc adaptée à la contrainte de latence |
| Exposer le modèle | FastAPI | API légère et rapide |
| Stockage des réclamations et retours des agents | PostgreSQL | Stockage structuré |
| Suivi des expériences et versions | MLflow | Historique et comparaison des modèles, suivi de la dérive |
| Recherche sémantique et génération ancrée (RAG) | Sentence-Transformers + ChromaDB ou FAISS + un LLM | Recherche en local, réponses ancrées dans les documents |
| Interface de démonstration | Streamlit | Création très rapide |
| Environnement commun | Docker | Même environnement sur les machines des 4 membres |

## 8. Risques, éthique, confidentialité

**1. Les données contiennent-elles des données personnelles ? Lesquelles ?**
Oui, potentiellement : noms, e-mails, téléphones, adresses, numéros de commande, montants, car le texte des réclamations est libre. *Mesure :* détection systématique avant tout traitement.

**2. Peut-on s'en passer ou les anonymiser ?**
On les anonymise (règles + reconnaissance d'entités nommées) avant l'entraînement et avant tout envoi à un LLM externe. Dans le projet, les données sont fictives ou publiques, mais la chaîne d'anonymisation est construite comme pour un cas réel. Accès restreint, durée de conservation limitée, respect de la loi marocaine 09-08 (CNDP) et des principes du RGPD.

**3. Qui peut être lésé par une erreur ?**
Les clients dont une réclamation urgente n'est pas détectée (fraude, produit dangereux, double prélèvement), ceux dont le message est mal routé, et ceux qui écrivent en dialecte, en plusieurs langues ou très brièvement (moins bien compris). *Mesure :* rappel urgent ≥ 90 %, F1 mesuré par canal et par type de message.

**4. Les données couvrent-elles tous les cas d'usage (lieux, périodes, populations) ?**
Non. Corpus en français uniquement (pas d'arabe ni de darija), 12 mois simulés (pas de vraie saisonnalité : soldes, fêtes), données synthétiques plus « propres » que la réalité, pas de pièces jointes. *Mesure :* résultats présentés comme indicatifs ; surveillance de la dérive (distribution des classes, taux de tri manuel).

**5. Quelle erreur coûte le plus, et à qui ?**
Le faux négatif sur la classe urgente : préjudice pour le client, risque juridique et de réputation pour ShopExpress. *Mesure :* contrainte de rappel urgent ≥ 90 %, alerte au responsable, quelques fausses alertes acceptées.

**6. Qui valide les décisions, et peut les corriger ?**
Un humain valide toujours : aucune réponse n'est envoyée automatiquement au client. Les agents et le responsable corrigent catégorie et priorité dans l'interface ; les corrections sont stockées et servent au ré-entraînement. *Mesure :* affichage du score de confiance, audits aléatoires pour éviter la validation sans relecture.

**7. Des données sortent-elles de l'organisation (API externe) ?**
Seulement pour la partie LLM (génération des messages synthétiques, brouillons RAG). *Mesure :* seuls du texte anonymisé et des passages de la FAQ/CGV fictives sont envoyés ; les modèles de classification et d'embeddings tournent en local ; possibilité d'utiliser un LLM local.

**8. Comment le système pourrait-il être détourné ?**
(a) Un client ajoute des mots-clés (« fraude », « danger ») pour passer en priorité ; (b) injection de consignes dans le texte d'une réclamation pour manipuler le LLM du RAG ; (c) usage du système pour noter ou sanctionner des clients ; (d) fuite des données. *Mesures :* règles d'urgence combinées au modèle et audits des alertes ; le LLM ne répond qu'à partir des passages retrouvés, avec citation obligatoire, refus si aucun passage pertinent et validation humaine ; le système trie mais ne décide aucune sanction ; accès restreint.

**Autres risques**

| Risque | Mesure |
|---|---|
| Dérive des données (nouveaux produits, promotions) | Surveillance des classes et du taux de tri manuel, ré-entraînement mensuel |
| Hallucinations du RAG | Citation obligatoire, refus sans source, validation humaine |
| Données synthétiques trop propres | Résultats présentés comme indicatifs |

## 9. Limites et hors périmètre

**Hors périmètre**
- Pas de réponse envoyée automatiquement au client : un humain valide toujours.
- Pas d'intégration à un vrai CRM ni à un vrai système de commande : données fictives.
- Français uniquement ; arabe et darija non couverts (extension possible).
- Pas de décision de remboursement, de sanction ou de compensation : le système trie, il ne tranche pas.
- Pas d'analyse de pièces jointes (photos, PDF).

**Limites connues**
- Un message traitant de plusieurs sujets n'a qu'une seule catégorie principale.
- Les résultats sur données synthétiques peuvent être plus optimistes que sur de vraies réclamations.
- Le module RAG est optionnel et dépend du temps disponible.

---

### Annexe : répartition du travail proposée

| Membre | Rôle proposé |
|---|---|
| Zainab Belgas (responsable) | Coordination, architecture et intégration (API, base de données) |
| Marwa Elomari Alaoui | Données : collecte, nettoyage, anonymisation, annotation |
| Amira Zahr | Modèles : baseline, fine-tuning, évaluation |
| Chaimaa Ezzerag | Assistant RAG, interface Streamlit, documentation et tests |

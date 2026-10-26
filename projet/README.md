# Étude de conception : Classification de réclamations clients

**Projet :** Applications intelligentes | **Sujet n°5** (assistant RAG optionnel : FAQ et conditions de vente fictives)

| Groupe | |
|---|---|
| **Responsable du groupe** | Zainab Belgas |
| **Membres** | Marwa Elomari Alaoui, Amira Zahr, Chaimaa Ezzerag |

> **Résumé du projet en 3 lignes.** Une boutique en ligne reçoit beaucoup de réclamations écrites par ses clients. Notre système lit chaque message et trouve automatiquement (1) de quoi parle la réclamation (livraison, remboursement, produit défectueux...) et (2) si elle est urgente. Ainsi, chaque réclamation arrive directement à la bonne équipe, et les cas graves sont traités en premier.

---

## 1. Contexte et utilisateurs

### Organisation

« **ShopExpress** » est une entreprise **fictive** : une boutique en ligne qui vend des produits électroniques et de l'équipement pour la maison. Elle propose la livraison à domicile et le paiement en ligne ou à la livraison.

- Elle reçoit environ **600 réclamations par jour**, par formulaire web, e-mail et chat.
- Aujourd'hui, une petite équipe lit et trie ces messages **à la main**.
- Problèmes de ce fonctionnement : les délais de traitement sont longs, et certains messages sont envoyés à la mauvaise équipe.

### Utilisateur principal

Le **responsable du service client** et ses conseillers.

- Ils reçoivent chaque réclamation **déjà classée** (catégorie + priorité).
- Ils la traitent eux-mêmes ou la transmettent à l'équipe concernée : logistique, SAV (service après-vente) ou facturation.

---

## 2. Problème et décision

### Décision

Pour chaque réclamation reçue, le système propose :

- une **catégorie** parmi : livraison, produit défectueux ou non conforme, facturation et paiement, retour et remboursement, compte et service client, autre ;
- une **priorité** : normale ou urgente.

Ensuite, trois cas sont possibles :

| Cas | Ce qui est décidé |
|---|---|
| Le système est **très sûr** de sa prédiction | La réclamation est envoyée automatiquement à l'équipe concernée. |
| Le système est **peu sûr** (score de confiance sous un seuil à calibrer) | La réclamation va dans une **file de tri manuel** : un humain décide. |
| La réclamation est **urgente** (fraude, produit dangereux, double prélèvement, menace de recours) | **Alerte immédiate** au responsable, quelle que soit la catégorie. |

### Fréquence

- **Prédiction en temps réel** : à chaque nouvelle réclamation, en moins d'une seconde.
- **Ré-entraînement du modèle** : une fois par mois, ou plus tôt si on détecte que les messages changent (nouveaux produits, nouvelle politique de retour...). On appelle cela la **dérive des données**.

### Conséquence d'une erreur

Il y a deux types d'erreurs. Pour la classe « urgente » :

- **Faux négatif** : une réclamation **urgente** est classée « normale » (ou envoyée à la mauvaise équipe).
  - Conséquences : traitement retardé de plusieurs jours, client très mécontent qui peut quitter la boutique, risque juridique ou de mauvaise réputation (fraude ou produit dangereux non signalé).
- **Faux positif** : une réclamation **normale** est classée « urgente » (ou envoyée à la mauvaise équipe).
  - Conséquences : perte de temps pour l'équipe, file prioritaire encombrée, retransmission interne. Le coût est réel mais **récupérable**.

> **Le faux négatif est le plus coûteux.** Il vaut mieux avoir quelques fausses alertes que rater un cas grave. C'est pourquoi nous fixons une contrainte forte sur le **rappel** de la classe urgente (voir section 5).
>
> *En clair : le rappel mesure « parmi toutes les vraies réclamations urgentes, combien le système en a trouvées ? ».*

---

## 3. Approche par sous-problème

Nous découpons le projet en trois sous-problèmes.

| Sous-problème | Approche | Pourquoi une approche plus simple ne suffit pas |
|---|---|---|
| **1. Classification de la catégorie** (plusieurs classes, texte en français) | **Baseline** : TF-IDF + régression logistique. **Modèle cible** : fine-tuning d'un modèle de langue pré-entraîné en français (CamemBERT ou DistilCamemBERT), avec seuil de confiance et file de tri manuel. | Les règles par mots-clés échouent sur les reformulations, les négations (« je n'ai pas été remboursé ») et les messages qui mélangent plusieurs sujets. Le TF-IDF reste notre baseline : le modèle de langue n'est retenu **que s'il apporte un gain mesuré**. |
| **2. Détection de priorité** (urgent / normal) | Classifieur binaire sur le même texte, combiné à quelques **règles métier** (montant élevé, mots liés à la fraude ou au danger), avec pondération de la classe urgente. | Les cas urgents sont rares (5 à 8 % des messages) et souvent écrits sans mot évident. Des règles seules les manquent ; un modèle seul peut rater des cas critiques connus. La combinaison réduit les faux négatifs. |
| **3. (Optionnel) Suggestion de réponse par assistant RAG** | **Recherche sémantique** (embeddings + base vectorielle) dans la FAQ et les conditions de vente fictives, puis **génération d'un brouillon de réponse** par un LLM, avec **citation de la source**. L'agent valide avant envoi. | Une recherche par mots-clés dans la FAQ ne trouve pas la bonne clause quand le client formule autrement. Un LLM seul pourrait inventer des délais ou des règles : il faut l'ancrer dans les vrais documents. |

> *En clair : le **RAG** (Retrieval-Augmented Generation) cherche d'abord les bons passages dans nos documents, puis demande à l'IA de rédiger une réponse **uniquement à partir de ces passages**.*

---

## 4. Données

### Sources

Nous construisons un corpus de réclamations en **français** :

- **(a)** données publiques de réclamations de consommateurs (par exemple la base CFPB), traduites et adaptées au contexte e-commerce ;
- **(b)** messages **synthétiques** générés par un LLM à partir de scénarios, puis relus manuellement pour vérifier qu'ils sont réalistes.

Pour la partie RAG : une **FAQ** et des **conditions générales de vente fictives**, rédigées par l'équipe (environ 30 à 50 pages).

### Volumes et période (hypothèse à confirmer)

- Environ **8 000 à 10 000 réclamations étiquetées**.
- Elles représentent **12 mois simulés**.
- Minimum **500 exemples par catégorie**.

### Variables clés

| Variable | Rôle |
|---|---|
| Texte de la réclamation (objet + corps) | Entrée principale du modèle |
| Catégorie | Étiquette à prédire (sous-problème 1) |
| Priorité | Étiquette à prédire (sous-problème 2) |
| Canal (formulaire, e-mail, chat) | Information complémentaire, utile pour analyser les biais |
| Date | Sert au découpage train / test dans le temps |
| Montant de la commande | Aide à repérer les cas urgents (si disponible) |

### Qualité des données

| Problème attendu | Solution prévue |
|---|---|
| Classes déséquilibrées (« autre » et « urgente » sont minoritaires) | Pondération des classes, suivi du rappel par classe |
| Étiquettes ambiguës (un message parle de deux sujets) | Double annotation d'un échantillon de 300 messages, mesure de l'accord entre annotateurs (**kappa de Cohen**) |
| Fautes d'orthographe, langage SMS | Nettoyage léger du texte, modèle robuste |
| Doublons | Suppression avant l'entraînement |
| Données personnelles | **Anonymisation** (noms, e-mails, téléphones, adresses) avant tout entraînement |

---

## 5. Métriques, baseline et critères d'acceptation

### Baseline et son résultat

- **Baseline retenue :** TF-IDF (mots et bigrammes) + régression logistique, avec pondération des classes.
- **Résultat attendu sur le jeu de test :** **macro-F1 d'environ 0,70 à 0,75** (hypothèse, à mesurer dès la première semaine).

> *En clair : la baseline est le modèle le plus simple possible. Elle sert de point de comparaison : si notre modèle plus complexe ne fait pas nettement mieux, on garde le simple.*

### Métrique principale

**Macro-F1** sur la catégorie, avec la contrainte : **rappel ≥ 90 % sur la classe « urgente »**.

> *En clair : le macro-F1 est la moyenne des scores F1 de toutes les classes. Il traite chaque catégorie de la même façon, même les rares, ce qui évite qu'un bon score sur les grosses catégories cache de mauvais résultats sur les petites.*

### Suivi secondaire

- Précision et rappel **par classe**, matrice de confusion.
- Taux de réclamations envoyées en **tri manuel**.
- **Précision** de la classe urgente (pour surveiller les fausses alertes).
- Pour le RAG : fidélité aux sources et taux de réponses correctes sur un jeu de 50 questions.

### Critères d'acceptation (à ajuster après la baseline)

1. **Performance :** macro-F1 ≥ 0,82 sur le jeu de test, avec un rappel urgent ≥ 90 %.
   *Découpage :* 70 % entraînement / 15 % validation / 15 % test, **stratifié par classe** et **séparé par date** (le test contient les messages les plus récents) pour éviter les fuites de données.
2. **Par rapport à la baseline :** gain d'au moins **8 points de macro-F1**. Sinon, on retient le modèle simple.
3. **Technique :** latence inférieure à **200 ms (p95)** par réclamation sur CPU ; taux de tri manuel inférieur à **20 %**.
4. **(Si RAG)** au moins **90 % des réponses fidèles** à la source citée sur les 50 questions de test, et aucune réponse hors périmètre sans avertissement.

---

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

### Description des composants

| N° | Composant | Rôle |
|---|---|---|
| 1 | Prétraitement et anonymisation | Nettoie le texte et supprime les données personnelles |
| 2 | Service de prédiction | Renvoie la catégorie, la priorité et un score de confiance |
| 3 | Base de données | Stocke les réclamations, les prédictions et les **corrections des agents** (réutilisées comme nouvelles étiquettes pour le ré-entraînement) |
| 4 | Interface agent | Permet au responsable de trier, visualiser et corriger |
| 5 | Module RAG (optionnel) | Propose un brouillon de réponse avec citation de la source |
| 6 | Suivi MLflow | Garde l'historique des expériences, des versions de modèles et des performances dans le temps |

---

## 7. Choix technologiques

| Technologie | Pourquoi ce choix |
|---|---|
| **Python + scikit-learn** | Baseline rapide à construire et reproductible |
| **Hugging Face Transformers (CamemBERT / DistilCamemBERT)** | Modèles déjà entraînés pour le français, utilisables avec peu de données. La version « Distil » est plus rapide, donc meilleure pour la contrainte de latence |
| **FastAPI** | API légère et rapide pour exposer le modèle |
| **PostgreSQL** | Stockage structuré des réclamations et des retours des agents |
| **MLflow** | Suivi des expériences et des versions de modèles |
| **Sentence-Transformers + ChromaDB ou FAISS, et un LLM** (partie RAG) | Recherche sémantique en local et génération ancrée dans les documents |
| **Streamlit** | Interface de démonstration créée très vite |
| **Docker** | Même environnement sur les machines des 4 membres du groupe |

---

## 8. Risques, éthique, confidentialité

| Risque | Explication | Mesure prévue |
|---|---|---|
| **Données personnelles** | Les réclamations contiennent noms, e-mails, téléphones, adresses, numéros de commande | Anonymisation (règles + reconnaissance d'entités nommées) avant l'entraînement et avant tout envoi à un LLM externe ; accès restreint ; durée de conservation limitée ; respect de la loi marocaine **09-08 (CNDP)** et des principes du **RGPD** |
| **Biais** | Résultats possiblement moins bons pour les messages en dialecte, mélangeant plusieurs langues ou très courts : certains clients seraient moins bien traités | Mesure du F1 **par canal et par type de message** |
| **Dérive des données** | Nouveaux produits, nouvelles politiques ou promotions changent le vocabulaire | Surveillance de la distribution des classes et du taux de tri manuel |
| **Trop grande confiance dans l'automatique** | Un agent peut valider sans relire | Affichage du score de confiance, audits aléatoires |
| **Hallucinations (RAG)** | Réponse inventée ou clause mal citée | Citation obligatoire de la source, refus de répondre si aucun passage pertinent, validation humaine avant envoi |
| **Données synthétiques** | Elles peuvent être plus « propres » que la réalité | Présenter les résultats comme **indicatifs** |

---

## 9. Limites et hors périmètre

### Ce que le projet ne couvre pas

- **Pas de réponse envoyée automatiquement** au client : un humain valide toujours.
- **Pas d'intégration** à un vrai CRM ni à un vrai système de commande : les données sont fictives.
- **Langue :** le français uniquement. L'arabe et la darija ne sont pas couverts (extension possible).
- **Pas de décision** de remboursement, de sanction ou de compensation : le système **trie**, il ne **tranche** pas.
- **Pas d'analyse de pièces jointes** (photos, PDF).

### Limites connues

- Un message qui traite de plusieurs sujets n'a qu'**une seule catégorie principale**.
- Les résultats sur données synthétiques peuvent être **plus optimistes** que sur de vraies réclamations.
- Le module RAG est **optionnel** et dépend du temps disponible.

---

## Annexe : répartition du travail proposée

*(à adapter par le groupe)*

| Membre | Rôle proposé |
|---|---|
| **Zainab Belgas** (responsable) | Coordination, architecture et intégration (API, base de données) |
| **Marwa Elomari Alaoui** | Données : collecte, nettoyage, anonymisation, annotation |
| **Amira Zahr** | Modèles : baseline, fine-tuning, évaluation des métriques |
| **Chaimaa Ezzerag** | Assistant RAG, interface Streamlit, documentation et tests |


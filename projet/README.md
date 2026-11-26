# SHOP​EXPRESS AI
## Étude de conception d'une application intelligente de classification des réclamations clients

**Module :** Développement et déploiement d'applications intelligentes – S2  
**Projet :** Sujet n°5 – Classification de réclamations clients  
**Extension optionnelle :** Assistant conversationnel RAG  
**Établissement :** EMSI – École Marocaine des Sciences de l'Ingénieur  
**Année universitaire :** 2026–2027

---

## INFORMATIONS DU DOCUMENT

| Élément | Information |
|---|---|
| Intitulé | Étude de conception – ShopExpress AI |
| Version | Brouillon complet |
| Date | 5 novembre 2026 |
| Type de document | Document de conception technique et fonctionnelle |
| Nombre de sections | 9 |
| Statut | En cours de validation |



---
### Équipe de réalisation

| N° | Membre | Fonction |
|---|---|---|
| 01 | Zainab Belgas | **Responsable de l'équipe** |
| 02 | Marwa Elomari Alaoui | Membre du projet |
| 03 | Amira Zahr | Membre du projet |
| 04 | Chaimaa Ezzerag | Membre du projet |


# SOMMAIRE

1. Contexte et utilisateurs
2. Problème et décision
3. Approche par sous-problème
4. Données
5. Métriques, baseline et critères d'acceptation
6. Architecture prévue
7. Choix technologiques
8. Risques, éthique et confidentialité
9. Limites et hors périmètre

---

# PRÉSENTATION GÉNÉRALE DU PROJET

ShopExpress AI est une application web intelligente destinée à optimiser la gestion des réclamations clients d'une plateforme e-commerce fictive.

Le projet repose sur l'utilisation du Machine Learning et du traitement automatique du langage naturel (NLP) afin d'automatiser deux opérations essentielles : la classification des réclamations selon leur catégorie et la détection de leur niveau de priorité.

L'application permettra également aux responsables du service client de consulter les prédictions, de suivre les réclamations, de corriger les erreurs de classification et de visualiser les indicateurs de performance à travers un tableau de bord.

En complément, une extension basée sur l'approche RAG (Retrieval-Augmented Generation) pourra être développée afin de proposer un assistant conversationnel capable de répondre aux questions en s'appuyant sur une base documentaire composée de FAQ et de conditions générales de vente fictives.

**Objectif principal :** concevoir une solution intelligente, sécurisée, documentée et déployable qui facilite le traitement des réclamations tout en maintenant une validation humaine pour les décisions importantes.

---

# 01. CONTEXTE ET UTILISATEURS

## 1.1. Contexte organisationnel

ShopExpress est une entreprise fictive spécialisée dans la vente en ligne de produits électroniques et d'équipements pour la maison.

Son activité implique la gestion quotidienne de plusieurs types de demandes clients :

- Problèmes liés aux commandes et aux livraisons.
- Produits défectueux ou non conformes.
- Difficultés de paiement et erreurs de facturation.
- Demandes de retour et de remboursement.
- Problèmes d'accès aux comptes clients.
- Demandes générales d'information et d'assistance.

Dans le scénario étudié, l'entreprise reçoit environ 600 réclamations par jour à travers différents canaux : formulaires web, e-mails et chat.

Le traitement manuel de ces messages peut entraîner une surcharge du service client, des retards de traitement et des erreurs d'orientation.

Cette situation justifie la mise en place d'un système intelligent permettant d'assister les employés dans la classification et la priorisation des réclamations.

*Précision : le volume de 600 réclamations quotidiennes est une hypothèse de travail destinée à représenter le contexte de l'entreprise fictive.*

## 1.2. Identification des utilisateurs

| Utilisateur | Rôle | Responsabilités |
|---|---|---|
| Responsable du service client | Utilisateur principal | Superviser les réclamations, contrôler les priorités et consulter les statistiques |
| Conseiller client | Utilisateur secondaire | Consulter les messages, vérifier les prédictions et corriger les classifications |
| Administrateur | Gestionnaire technique | Gérer les comptes, les rôles et les paramètres de l'application |

Les équipes opérationnelles destinataires sont la logistique, le service après-vente, la facturation, les retours et remboursements ainsi que le service client.

## 1.3. Objectifs du système

Le système doit permettre de :

1. Centraliser les réclamations clients.
2. Identifier automatiquement leur catégorie.
3. Déterminer leur niveau de priorité.
4. Proposer une orientation vers le service concerné.
5. Signaler les prédictions incertaines.
6. Permettre la vérification et la correction humaine.
7. Produire des statistiques pour faciliter le suivi de l'activité.

---

# 02. PROBLÈME ET DÉCISION

## 2.1. Problématique

Comment automatiser la classification et la priorisation des réclamations clients afin de réduire le temps de traitement, améliorer leur orientation et garantir une meilleure prise en charge des situations urgentes ?

## 2.2. Décisions prises par le système

Pour chaque réclamation reçue, l'application réalise deux prédictions indépendantes.

### A. Classification des réclamations

Le premier modèle identifie automatiquement la catégorie du message parmi les six classes suivantes :

| Code | Catégorie | Exemple de réclamation |
|---|---|---|
| C1 | Livraison | Ma commande n'est toujours pas arrivée. |
| C2 | Produit défectueux | Le produit reçu ne fonctionne pas. |
| C3 | Facturation et paiement | J'ai été débité deux fois. |
| C4 | Retour et remboursement | Je souhaite retourner mon article. |
| C5 | Compte et service client | Je n'arrive plus à accéder à mon compte. |
| C6 | Autre | Je souhaite obtenir des informations générales. |

### B. Détection du niveau de priorité

Le deuxième modèle détermine le degré d'urgence de la réclamation.

| Niveau | Description | Traitement proposé |
|---|---|---|
| Normale | Demande classique sans risque immédiat identifié | File de traitement habituelle |
| Urgente | Situation nécessitant une attention rapide | Alerte et vérification prioritaire |

## 2.3. Règles de décision

| Résultat obtenu | Décision proposée |
|---|---|
| Catégorie prédite avec confiance élevée | Proposition d'affectation à l'équipe concernée |
| Confiance inférieure au seuil défini | Vérification humaine obligatoire |
| Priorité urgente | Signalement au responsable |
| Catégorie incorrecte | Correction par un conseiller autorisé |

Les seuils de confiance seront déterminés à partir des résultats de validation et non fixés arbitrairement.

## 2.4. Fréquence d'utilisation

| Opération | Fréquence prévue |
|---|---|
| Classification | À chaque nouvelle réclamation |
| Détection des urgences | À chaque nouvelle réclamation |
| Consultation des réclamations | Plusieurs fois par jour |
| Analyse des statistiques | Quotidienne ou hebdomadaire |
| Réévaluation des modèles | Mensuelle ou selon les performances |

## 2.5. Conséquences des erreurs

Deux types d'erreurs doivent être particulièrement surveillés.

**Faux négatif :** une réclamation urgente est classée comme normale.

Conséquences possibles :
- Retard de traitement d'une situation critique.
- Risque financier pour le client.
- Insatisfaction et perte de confiance.
- Dégradation de l'image de l'entreprise.

**Faux positif :** une réclamation normale est classée comme urgente.

Conséquences possibles :
- Mobilisation inutile des conseillers.
- Surcharge de la file prioritaire.
- Retard dans le traitement des autres réclamations.

Le faux négatif est considéré comme l'erreur la plus coûteuse. Le système privilégiera donc un rappel élevé de la classe urgente, tout en contrôlant le nombre de fausses alertes.

---

# 03. APPROCHE PAR SOUS-PROBLÈME

Le projet est décomposé en trois sous-problèmes complémentaires.

## 3.1. Tableau de décomposition

| Sous-problème | Approche retenue | Justification |
|---|---|---|
| Classification des catégories | ML : TF-IDF + régression logistique, puis expérimentation de CamemBERT | Les règles par mots-clés ne prennent pas suffisamment en compte les reformulations et le contexte des messages. |
| Détection de priorité | ML binaire + règles métier | Les règles seules ne couvrent pas tous les cas ; le modèle permet d'apprendre des caractéristiques linguistiques plus variées. |
| Suggestion de réponses (bonus) | RAG + embeddings + LLM | Le RAG permet de produire des réponses fondées sur les documents de référence plutôt que sur les seules connaissances du LLM. |

## 3.2. Sous-problème 1 : classification des catégories

L'objectif est d'identifier automatiquement le type de réclamation.

**Pipeline envisagé :**

1. Réception du texte.
2. Nettoyage et normalisation.
3. Transformation du texte avec TF-IDF.
4. Classification avec une régression logistique.
5. Calcul des scores de confiance.
6. Proposition de catégorie.

Une expérimentation avec CamemBERT ou DistilCamemBERT permettra ensuite de comparer les performances avec la baseline.

## 3.3. Sous-problème 2 : détection des urgences

L'objectif est d'identifier les réclamations nécessitant une intervention rapide.

Le modèle réalisera une classification binaire :

- 0 : normale.
- 1 : urgente.

Des règles métier complémentaires seront utilisées pour signaler certains cas critiques connus.

Le modèle sera évalué en privilégiant le rappel de la classe urgente afin de limiter les situations critiques non détectées.

## 3.4. Sous-problème 3 : assistant RAG optionnel

L'extension RAG permettra aux utilisateurs autorisés de poser des questions concernant les procédures et les conditions de vente de ShopExpress.

**Fonctionnement envisagé :**

1. Importation des documents FAQ et CGV.
2. Extraction et découpage du contenu.
3. Génération des embeddings.
4. Indexation dans une base vectorielle.
5. Recherche des passages pertinents.
6. Génération d'une réponse contextualisée.
7. Affichage des références documentaires.

Les réponses seront proposées sous forme de brouillons et devront être vérifiées par un conseiller.

## 3.5. Synthèse des données par sous-problème

| Sous-problème | Source envisagée | Volume cible | Données personnelles |
|---|---|---:|---|
| Classification | CFPB, sous réserve de validation de la licence, et données synthétiques | 8 000 à 10 000 messages | Possibles dans les données publiques |
| Priorisation | Même corpus, avec annotations de priorité | Même corpus | Possibles dans les données publiques |
| RAG | FAQ et CGV fictives rédigées par le groupe | 30 à 50 pages | Non, si aucune donnée personnelle n'est intégrée |

Les volumes sont des objectifs de collecte et non des volumes déjà disponibles.

---

# 04. DONNÉES

## 4.1. Sources de données

Le projet utilisera deux catégories de données.

**A. Données publiques**

La base CFPB (Consumer Financial Protection Bureau) sera étudiée comme source potentielle de réclamations de consommateurs.

Les conditions de réutilisation, la licence et la pertinence des messages pour le contexte e-commerce devront être vérifiées avant leur exploitation.

**B. Données synthétiques**

Des réclamations fictives seront créées à partir de scénarios représentatifs des six catégories.

Ces données permettront de compléter le corpus et de tester les différentes fonctionnalités de l'application.

Elles seront identifiées séparément afin d'éviter de confondre les données réelles et synthétiques.

**C. Documents destinés au RAG**

- FAQ de ShopExpress.
- Conditions générales de vente fictives.
- Procédures de livraison.
- Procédures de retour.
- Procédures de remboursement.

## 4.2. Volume prévisionnel

| Élément | Volume cible |
|---|---:|
| Réclamations totales | 8 000 à 10 000 |
| Catégories | 6 |
| Minimum souhaité par catégorie | 500 |
| Période représentée | 12 mois |
| Échantillon de double annotation | 300 messages |
| Questions de test RAG | 50 |
| Documents RAG | 30 à 50 pages |

## 4.3. Description des variables

| Variable | Type | Description |
|---|---|---|
| id | Identifiant | Identifiant unique de la réclamation |
| text | Texte | Contenu du message client |
| category | Catégorielle | Catégorie réelle |
| priority | Binaire | Priorité réelle |
| channel | Catégorielle | Formulaire, e-mail ou chat |
| date | Date | Date de réception |
| order_amount | Numérique | Montant de la commande si disponible |
| source | Catégorielle | Source publique ou synthétique |

## 4.4. Prétraitement et préparation

Les opérations de préparation comprendront :

- Suppression des doublons.
- Traitement des valeurs manquantes.
- Nettoyage des textes.
- Normalisation des caractères et des espaces.
- Anonymisation des informations personnelles.
- Vérification des étiquettes.
- Contrôle des déséquilibres entre classes.
- Séparation des jeux d'entraînement, de validation et de test.

## 4.5. Qualité et fiabilité des annotations

Un échantillon de 300 messages sera annoté indépendamment par deux membres du groupe.

La cohérence entre les annotations sera mesurée à l'aide du coefficient Kappa de Cohen.

Les désaccords seront examinés collectivement afin d'obtenir des étiquettes fiables.

---

# 05. MÉTRIQUES, BASELINE ET CRITÈRES D'ACCEPTATION

## 5.1. Modèle de référence (Baseline)

La baseline retenue est :

**TF-IDF + Régression logistique avec pondération des classes.**

Cette méthode constitue un point de comparaison simple, reproductible et adapté à une première classification de textes.

Le modèle sera entraîné sur les données d'apprentissage puis évalué sur un jeu de test indépendant.

**Résultat initial :** à mesurer après le premier entraînement.

L'objectif indicatif est d'obtenir un macro-F1 compris entre 0,70 et 0,75, sans considérer cette estimation comme un résultat acquis.

## 5.2. Métriques d'évaluation

| Métrique | Signification | Utilité |
|---|---|---|
| Accuracy | Proportion de prédictions correctes | Mesurer la performance globale |
| Precision | Proportion de prédictions positives correctes | Limiter les fausses alertes |
| Recall | Proportion de cas positifs correctement détectés | Limiter les cas manqués |
| Macro-F1 | Moyenne des F1-scores des classes | Évaluer équitablement les catégories |
| Matrice de confusion | Répartition des prédictions correctes et incorrectes | Identifier les erreurs |

**Métrique principale pour la classification :** Macro-F1.

**Métrique principale pour la détection des urgences :** Recall de la classe urgente.

## 5.3. Critères d'acceptation

| Indicateur | Objectif visé |
|---|---:|
| Macro-F1 de classification | ≥ 0,82 |
| Recall de la classe urgente | ≥ 90 % |
| Gain par rapport à la baseline | ≥ 8 points de macro-F1 |
| Latence de prédiction | ≤ 200 ms au 95e percentile sur CPU |
| Taux de tri manuel | < 20 % |
| Fidélité des réponses RAG (bonus) | ≥ 90 % sur 50 questions |

Ces valeurs représentent des objectifs à atteindre et devront être validées expérimentalement.

Le gain de macro-F1 sera calculé par rapport à la baseline sur le même jeu de test.

## 5.4. Découpage du dataset

Le découpage prévu est le suivant :

| Partition | Pourcentage | Utilisation |
|---|---:|---|
| Entraînement | 70 % | Apprentissage du modèle |
| Validation | 15 % | Réglage des paramètres |
| Test | 15 % | Évaluation finale |

Un découpage chronologique sera privilégié pour simuler une utilisation réelle. Les données les plus récentes seront conservées pour le test.

Les doublons et les variantes quasi identiques d'un même message devront être regroupés avant le découpage afin d'éviter les fuites de données.

---

# 06. ARCHITECTURE PRÉVUE

## 6.1. Architecture générale

L'architecture de ShopExpress AI repose sur une séparation entre l'interface utilisateur, l'API, les modèles de Machine Learning et la base de données.

```text
                    UTILISATEUR
                         |
                         v
                 INTERFACE WEB
                    STREAMLIT
                         |
                         v
                    API FASTAPI
                         |
                         v
              PRÉTRAITEMENT DU TEXTE
                         |
              +----------+----------+
              |                     |
              v                     v
       MODÈLE CATÉGORIE       MODÈLE PRIORITÉ
              |                     |
              +----------+----------+
                         |
                         v
                 RÉSULTATS ML
                         |
              +----------+----------+
              |                     |
              v                     v
        CONFIANCE ÉLEVÉE      CONFIANCE FAIBLE
              |                     |
              v                     v
       ORIENTATION PROPOSÉE   VÉRIFICATION HUMAINE
              |                     |
              +----------+----------+
                         |
                         v
                  POSTGRESQL
                         |
                         v
                HISTORIQUE ET
                 STATISTIQUES
```

**Composants transversaux :**

- MLflow : suivi des expériences et versions des modèles.
- DVC : versionnement des données et pipelines.
- Pytest : validation du fonctionnement.
- Docker : conteneurisation et déploiement.

**Extension RAG :**

```text
FAQ + CGV
    |
    v
Extraction des documents
    |
    v
Découpage en passages
    |
    v
Génération des embeddings
    |
    v
Base vectorielle
    |
    v
Recherche sémantique
    |
    v
LLM
    |
    v
Réponse avec sources
    |
    v
Validation humaine
```

## 6.2. Description des composants

| Composant | Responsabilité |
|---|---|
| Interface Streamlit | Interaction avec les utilisateurs |
| API FastAPI | Communication entre interface et modèles |
| Prétraitement | Nettoyage et préparation des messages |
| Modèle de classification | Prédiction de la catégorie |
| Modèle de priorité | Détection des urgences |
| PostgreSQL | Stockage des données et corrections |
| MLflow | Suivi des expériences |
| DVC | Versionnement des données |
| Docker | Déploiement reproductible |
| Module RAG | Recherche documentaire et génération de réponses |

## 6.3. Flux de traitement d'une réclamation

1. Le client soumet une réclamation.
2. L'application reçoit le message.
3. L'API vérifie et prépare le texte.
4. Les deux modèles réalisent leurs prédictions.
5. Les scores de confiance sont calculés.
6. Le résultat est enregistré.
7. L'application affiche la catégorie et la priorité.
8. Le conseiller valide ou corrige la prédiction si nécessaire.

---

# 07. CHOIX TECHNOLOGIQUES

Les technologies sont sélectionnées en fonction des besoins fonctionnels, des contraintes de développement et des exigences de déploiement.

| Besoin | Technologie | Justification |
|---|---|---|
| Langage de programmation | Python | Écosystème adapté au ML et au NLP |
| Manipulation des données | Pandas | Nettoyage et transformation |
| Machine Learning | Scikit-learn | Modèles de classification et métriques |
| Deep Learning NLP | Hugging Face Transformers | Expérimentation de CamemBERT |
| API | FastAPI | API documentée et performante |
| Interface | Streamlit | Développement d'une interface interactive |
| Base de données | PostgreSQL | Persistance des réclamations |
| Suivi ML | MLflow | Gestion des expériences et modèles |
| Versionnement des données | DVC | Reproductibilité |
| Tests | Pytest | Tests unitaires et d'intégration |
| Déploiement | Docker | Conteneurisation |
| Assistant RAG | Sentence-Transformers + ChromaDB ou FAISS | Recherche sémantique |
| Génération | LLM | Production de réponses contextualisées |

L'environnement de développement sera basé sur Windows, avec Visual Studio Code comme éditeur principal.

---

# 08. RISQUES, ÉTHIQUE ET CONFIDENTIALITÉ

Cette section répond aux huit questions obligatoires du modèle de conception.

## 8.1. Analyse des huit questions

### 1. Les données contiennent-elles des données personnelles ? Lesquelles ?

Les réclamations réelles peuvent contenir des informations personnelles telles que :

- Nom et prénom.
- Adresse e-mail.
- Numéro de téléphone.
- Adresse de livraison.
- Identifiant de commande.
- Informations relatives à un paiement.

**Mesure de prévention :** identifier et anonymiser les informations personnelles avant toute utilisation pour l'entraînement.

### 2. Peut-on s'en passer ou les anonymiser ?

Oui. Les informations directement identifiantes ne sont pas nécessaires à la classification des réclamations.

Les mesures prévues sont :

- Suppression des noms et coordonnées.
- Remplacement des identifiants par des valeurs fictives.
- Suppression des informations sensibles inutiles.
- Utilisation de données synthétiques lorsque cela est possible.

### 3. Qui peut être lésé par une erreur ?

Les personnes potentiellement affectées sont :

- Le client dont la réclamation est mal classée.
- Le conseiller chargé du traitement.
- Le responsable du service client.
- L'entreprise en cas de perte financière ou de dégradation de son image.

**Mesure de prévention :** maintenir une validation humaine et permettre la correction des prédictions.

### 4. Les données couvrent-elles tous les cas d'usage (lieux, périodes, populations) ?

Non, la représentativité du corpus ne peut pas être garantie.

Les limites possibles concernent :

- La diversité des formulations.
- Les différents profils de clients.
- Les périodes de l'année.
- Les canaux de communication.
- Les réclamations rares.
- Les différences de vocabulaire.

**Mesure de prévention :** diversifier les données et analyser les performances par catégorie et par canal.

### 5. Quelle erreur coûte le plus, et à qui ?

Le faux négatif concernant une réclamation urgente est considéré comme l'erreur la plus coûteuse.

Il peut entraîner un retard de traitement, une perte financière ou une mauvaise prise en charge d'un problème critique.

Le client et l'entreprise sont les principales parties concernées.

**Mesure de prévention :** privilégier le rappel de la classe urgente et déclencher une vérification humaine pour les situations sensibles.

### 6. Qui valide les décisions, et peut les corriger ?

Les conseillers autorisés et le responsable du service client sont chargés de valider les résultats.

Ils peuvent :

- Confirmer une catégorie.
- Modifier la priorité.
- Corriger une prédiction.
- Réorienter une réclamation.

**Mesure de prévention :** conserver un historique des prédictions et des corrections humaines.

### 7. Des données sortent-elles de l'organisation (API externe) ?

Le fonctionnement principal privilégiera un traitement local au sein de l'application.

En cas d'utilisation d'un service externe, notamment pour le LLM du module RAG, les informations transmises seront limitées au strict nécessaire.

**Mesure de prévention :** anonymiser les données, vérifier les conditions de confidentialité et documenter les échanges externes.

### 8. Comment le système pourrait-il être détourné ?

Les principaux scénarios de détournement sont :

- Envoi massif de réclamations artificielles.
- Accès non autorisé à l'interface.
- Manipulation des données d'entraînement.
- Extraction d'informations personnelles.
- Injection de prompt dans le module RAG.
- Utilisation abusive des fonctionnalités de l'API.

**Mesure de prévention :**

- Authentification.
- Gestion des rôles et autorisations.
- Validation des entrées.
- Limitation des requêtes.
- Journalisation des opérations.
- Protection des données.
- Contrôle des documents et réponses du RAG.

## 8.2. Tableau synthétique des risques

| Risque | Gravité | Mesure de maîtrise |
|---|---|---|
| Fuite de données personnelles | Élevée | Anonymisation et contrôle d'accès |
| Biais du modèle | Élevée | Évaluation par classe et par canal |
| Non-détection d'une urgence | Élevée | Rappel élevé et validation humaine |
| Hallucinations du RAG | Élevée | Réponses fondées sur les sources |
| Attaque de l'API | Élevée | Authentification et validation |
| Dérive des données | Moyenne | Surveillance et réentraînement |
| Données synthétiques peu réalistes | Moyenne | Évaluation sur des données indépendantes |
| Erreur humaine | Moyenne | Historique et traçabilité |

Le projet prendra également en compte les exigences applicables de la loi marocaine 09-08 relative à la protection des données personnelles et, lorsque cela est applicable, les principes du RGPD.

---

# 09. LIMITES ET HORS PÉRIMÈTRE

## 9.1. Limites identifiées

La solution proposée présente plusieurs limites :

1. Les performances dépendent directement de la qualité des données d'entraînement.
2. Les messages ambigus peuvent produire des prédictions incorrectes.
3. Les données synthétiques ne représentent pas parfaitement les situations réelles.
4. Le modèle peut être moins performant sur les messages très courts.
5. Les catégories rares peuvent être sous-représentées.
6. Les évolutions du vocabulaire peuvent nécessiter une mise à jour des modèles.
7. Les réponses générées par le RAG peuvent comporter des erreurs si les documents sont incomplets.

## 9.2. Fonctionnalités hors périmètre

La première version ne prendra pas en charge :

- L'envoi automatique des réponses aux clients.
- La gestion complète d'un système e-commerce.
- Le remboursement automatique des commandes.
- L'accès direct aux systèmes bancaires.
- La gestion complète des stocks.
- La prise de décisions commerciales ou financières.
- L'analyse automatique des images et pièces jointes.
- La classification multilingue en arabe et en darija.

## 9.3. Périmètre fonctionnel retenu

Le périmètre principal du projet comprend quatre fonctionnalités :

| Fonctionnalité | Inclusion |
|---|---|
| Réception et consultation des réclamations | Obligatoire |
| Classification en six catégories | Obligatoire |
| Détection de priorité normale ou urgente | Obligatoire |
| Tableau de bord et correction humaine | Obligatoire |
| Assistant conversationnel RAG | Bonus |

L'objectif est de réaliser une application fonctionnelle, testable et déployable, sans dépasser le périmètre défini.

---

# ANNEXE A – ORGANISATION DU TRAVAIL

## Répartition prévisionnelle des responsabilités

| Membre | Responsabilités |
|---|---|
| Zainab Belgas | Coordination, architecture et intégration |
| Marwa Elomari Alaoui | Collecte, nettoyage, anonymisation et préparation des données |
| Amira Zahr | Développement, entraînement et évaluation des modèles ML |
| Chaimaa Ezzerag | Interface utilisateur, tests et documentation |

L'intégration générale, la validation et la préparation de la présentation seront réalisées collectivement.

# ANNEXE B – LIVRABLES ATTENDUS

| N° | Livrable | Contenu |
|---|---|---|
| 01 | Étude de conception | Analyse des besoins et architecture |
| 02 | Dataset | Données nettoyées et annotées |
| 03 | Notebook ML | Exploration et entraînement |
| 04 | Modèles ML | Classification et priorisation |
| 05 | API | API FastAPI documentée et sécurisée |
| 06 | Interface web | Application de gestion des réclamations |
| 07 | Base de données | Stockage des réclamations et corrections |
| 08 | Tests | Tests unitaires et d'intégration |
| 09 | Suivi ML | MLflow et DVC |
| 10 | Déploiement | Docker et documentation |
| 11 | Assistant RAG | Module documentaire optionnel |

---

# CONCLUSION GÉNÉRALE

ShopExpress AI propose une approche intelligente pour améliorer la gestion des réclamations clients dans un environnement e-commerce.

L'utilisation de deux modèles de Machine Learning permet d'automatiser la classification des messages et l'identification des situations urgentes.

L'architecture proposée associe une API documentée, une interface web, une base de données et des outils de suivi et de déploiement.

Une attention particulière est accordée à la qualité des données, à la confidentialité, à l'évaluation des erreurs et à la validation humaine.

Enfin, l'intégration éventuelle d'un assistant RAG permettra d'enrichir la solution avec une assistance documentaire fondée sur des sources vérifiables.

**ShopExpress AI a ainsi pour ambition de proposer une solution cohérente, évolutive et reproductible, répondant aux exigences d'un projet de développement et de déploiement d'applications intelligentes.**

---

*Document de conception – ShopExpress AI | EMSI | Année universitaire 2026–2027*

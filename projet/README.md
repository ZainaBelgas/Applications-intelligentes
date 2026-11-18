# ÉTUDE DE CONCEPTION
## ShopExpress AI – Classification intelligente des réclamations clients

**Module :** Développement et déploiement d'applications intelligentes – S2  
**Sujet choisi :** Sujet n°5 – Classification de réclamations clients  
**Option bonus :** Assistant RAG avec FAQ et conditions générales de vente fictives  
**Version :** Brouillon complet – à valider et compléter au fur et à mesure du projet  
**Date :** 18/11/2026

### Informations du groupe

| Rôle | Nom |
|---|---|
| Responsable du groupe | Zainab Belgas |
| Membre | Marwa Elomari Alaoui |
| Membre | Amira Zahr |
| Membre | Chaimaa Ezzerag |

---

# Résumé du projet

ShopExpress AI est une application intelligente destinée à faciliter la gestion des réclamations clients d'une boutique en ligne fictive appelée ShopExpress.

L'application utilise des techniques de Machine Learning et de traitement automatique du langage naturel (NLP) pour analyser les messages envoyés par les clients, identifier automatiquement leur catégorie et déterminer leur niveau de priorité.

Elle permet également au responsable du service client de consulter les réclamations, de vérifier les prédictions, de corriger les erreurs et de suivre les statistiques à travers un tableau de bord.

Un assistant conversationnel basé sur le RAG (Retrieval-Augmented Generation) pourra être ajouté en option afin de proposer des réponses aux clients à partir d'une FAQ et de conditions générales de vente fictives.

---

# 1. Contexte et utilisateurs

## 1.1. Organisation ou situation

ShopExpress est une entreprise fictive spécialisée dans la vente en ligne de produits électroniques et d'équipements pour la maison.

Elle propose plusieurs services :
- Vente de produits sur une plateforme e-commerce.
- Livraison à domicile.
- Paiement en ligne ou à la livraison.
- Retours et remboursements.
- Assistance et service après-vente.

Dans le scénario étudié, l'entreprise reçoit environ 600 réclamations par jour à travers différents canaux : formulaires web, e-mails et chat.

Actuellement, les réclamations sont consultées et classées manuellement par les employés du service client.

Cette organisation présente plusieurs difficultés :
- Temps important consacré au traitement des messages.
- Retard dans la prise en charge des réclamations.
- Mauvaise orientation de certains messages.
- Difficulté à identifier rapidement les situations urgentes.
- Charge de travail importante pour les conseillers.

Pour répondre à ces difficultés, nous proposons une application intelligente capable d'automatiser la première étape du traitement des réclamations.

*Remarque : les 600 réclamations quotidiennes constituent une hypothèse du scénario fictif et non une donnée observée dans une entreprise réelle.*

## 1.2. Utilisateurs du système

**Utilisateur principal : Responsable du service client**

Il utilise l'application pour :
- Consulter les nouvelles réclamations.
- Visualiser la catégorie prédite.
- Consulter le niveau de priorité.
- Identifier les réclamations urgentes.
- Vérifier les prédictions incertaines.
- Corriger les classifications incorrectes.
- Suivre les statistiques de traitement.

**Utilisateurs secondaires : Conseillers du service client**

Ils peuvent :
- Consulter les réclamations qui leur sont attribuées.
- Lire les messages des clients.
- Vérifier les résultats proposés par le modèle.
- Modifier une catégorie ou une priorité.
- Signaler les erreurs de classification.

**Équipes destinataires :**
- Logistique.
- Service après-vente.
- Facturation.
- Retours et remboursements.
- Service client.

## 1.3. Objectif général

Développer une application web intelligente qui permet de classifier automatiquement les réclamations clients, de détecter les situations urgentes et de faciliter leur orientation vers les équipes concernées.

---

# 2. Problème et décision

## 2.1. Problème à résoudre

Comment automatiser la classification et la priorisation des réclamations clients afin de réduire le temps de traitement, améliorer leur orientation et éviter que les situations urgentes soient ignorées ?

## 2.2. Décision prise par le système

Pour chaque réclamation reçue, le système doit produire deux prédictions :

**1. Classification de la catégorie**

Le modèle doit identifier une catégorie parmi les six suivantes :

| Code | Catégorie | Exemple |
|---|---|---|
| C1 | Livraison | Commande non reçue ou retardée |
| C2 | Produit défectueux ou non conforme | Produit cassé ou incorrect |
| C3 | Facturation et paiement | Double prélèvement ou problème de paiement |
| C4 | Retour et remboursement | Demande de retour ou remboursement |
| C5 | Compte et service client | Problème de connexion ou assistance |
| C6 | Autre | Demande ne correspondant pas aux autres catégories |

**2. Détection de priorité**

Le système doit déterminer si la réclamation est :

- Normale : demande classique pouvant suivre le traitement habituel.
- Urgente : situation nécessitant une intervention rapide, comme une fraude signalée, un produit potentiellement dangereux ou un double prélèvement.

## 2.3. Décisions selon le résultat

| Situation | Action du système |
|---|---|
| Prédiction avec confiance élevée | Proposition d'orientation vers l'équipe concernée |
| Prédiction avec confiance faible | Envoi dans une file de vérification manuelle |
| Réclamation urgente | Déclenchement d'une alerte au responsable |
| Prédiction incorrecte | Correction possible par un conseiller |

La classification automatique reste une aide à la décision. Les situations sensibles et les prédictions incertaines doivent être vérifiées par un humain.

## 2.4. Fréquence d'utilisation

- Classification : à chaque nouvelle réclamation, en temps réel.
- Consultation : plusieurs fois par jour par les responsables et les conseillers.
- Suivi des performances : régulièrement.
- Réentraînement : mensuel ou lorsqu'une dérive des données est détectée.

## 2.5. Conséquences d'une erreur

**Faux négatif :** une réclamation réellement urgente est classée comme normale.

Conséquences :
- Retard dans le traitement d'un problème grave.
- Insatisfaction du client.
- Risque financier ou juridique.
- Dégradation de la réputation de l'entreprise.

**Faux positif :** une réclamation normale est classée comme urgente.

Conséquences :
- Mobilisation inutile des conseillers.
- Surcharge de la file prioritaire.
- Retard dans le traitement des autres demandes.

Le faux négatif représente le risque le plus important. Le projet privilégie donc un rappel élevé pour la classe urgente, même si cela peut entraîner quelques fausses alertes supplémentaires.

---

# 3. Approche par sous-problème

Le projet est divisé en trois sous-problèmes complémentaires.

| Sous-problème | Approche retenue | Pourquoi une approche plus simple ne suffit pas |
|---|---|---|
| 1. Classification des catégories | TF-IDF + régression logistique comme baseline, puis expérimentation de CamemBERT ou DistilCamemBERT | Les règles par mots-clés ne comprennent pas suffisamment les reformulations, les négations et les messages contenant plusieurs informations. |
| 2. Détection de priorité | Classification binaire avec Machine Learning et règles métier complémentaires | Les règles seules ne détectent pas tous les cas urgents. Un modèle seul peut également manquer certains cas critiques connus. |
| 3. Suggestion de réponses (optionnel) | RAG avec embeddings, base vectorielle et LLM | Une recherche classique par mots-clés ne retrouve pas toujours les passages pertinents. Un LLM seul risque de produire des informations incorrectes. |

## 3.1. Classification des catégories

Le premier modèle analyse le texte de la réclamation et prédit une catégorie parmi les six classes définies.

Approche :
- Nettoyage du texte.
- Transformation des messages en représentations numériques avec TF-IDF.
- Entraînement d'une régression logistique.
- Évaluation des résultats.
- Expérimentation avec CamemBERT ou DistilCamemBERT.
- Comparaison des performances.

Le modèle le plus complexe sera retenu uniquement s'il apporte une amélioration mesurable par rapport à la baseline.

## 3.2. Détection de priorité

Le deuxième modèle détermine si une réclamation est normale ou urgente.

Il utilise :
- Le texte du message.
- Les informations complémentaires disponibles.
- Des règles métier pour certains cas critiques.
- Une pondération des classes afin de mieux prendre en compte les réclamations urgentes.

Le système doit particulièrement limiter les faux négatifs.

## 3.3. Assistant conversationnel RAG (optionnel)

Le module RAG permettra au responsable ou au conseiller de poser des questions concernant les conditions de vente et les procédures de l'entreprise.

Fonctionnement :
1. Importation des documents FAQ et conditions générales de vente.
2. Découpage des documents en passages.
3. Transformation des passages en embeddings.
4. Stockage dans une base vectorielle.
5. Recherche des passages pertinents.
6. Génération d'une réponse à partir des informations retrouvées.
7. Affichage des sources utilisées.

L'assistant proposera uniquement des brouillons de réponses qui devront être validés par un conseiller avant tout envoi.

## 3.4. Tableau récapitulatif des sous-problèmes et des données

| Sous-problème | Approche | Jeu de données | Source et licence | Volume prévu | Données personnelles |
|---|---|---|---|---|---|
| Classification des catégories | TF-IDF, régression logistique, CamemBERT | Réclamations textuelles annotées | Corpus public de réclamations de consommateurs, notamment CFPB, sous réserve de vérification des conditions de réutilisation ; compléments synthétiques | 8 000 à 10 000 messages visés | Oui dans certaines sources ; anonymisation nécessaire |
| Détection de priorité | Classification binaire et règles métier | Réclamations annotées urgentes/normales | Même corpus, avec annotations de priorité réalisées par l'équipe | Même corpus ; proportion urgente estimée entre 5 et 8 % | Oui dans certaines sources ; anonymisation nécessaire |
| Assistant RAG (optionnel) | Embeddings, recherche vectorielle, LLM | FAQ et conditions générales de vente fictives | Documents rédigés par l'équipe | Environ 30 à 50 pages | Non, si les documents ne contiennent aucune donnée personnelle |

Les volumes présentés sont des objectifs de constitution du corpus et devront être confirmés après la collecte.

---

# 4. Données

## 4.1. Sources des données

Le projet nécessite un corpus de réclamations clients rédigées en français.

Deux sources principales sont envisagées :

**Source 1 : Données publiques**

Utilisation éventuelle de la base CFPB (Consumer Financial Protection Bureau) contenant des réclamations de consommateurs.

Les messages pertinents seront étudiés, traduits et adaptés au contexte du commerce électronique lorsque cela est justifié.

La licence et les conditions de réutilisation de la source seront vérifiées avant son intégration au projet.

**Source 2 : Données synthétiques**

Création de messages fictifs à partir de scénarios de réclamations clients.

Les messages seront générés, puis vérifiés et annotés manuellement par les membres du groupe.

Les données synthétiques seront identifiées séparément des données publiques.

**Source complémentaire pour le RAG :**

- FAQ fictive de ShopExpress.
- Conditions générales de vente fictives.
- Procédures de livraison.
- Procédures de retour et de remboursement.

Ces documents seront rédigés par le groupe.

## 4.2. Volume prévu

| Élément | Volume prévu |
|---|---:|
| Réclamations totales | 8 000 à 10 000 |
| Catégories | 6 |
| Minimum souhaité par catégorie | 500 |
| Période simulée | 12 mois |
| Échantillon pour double annotation | 300 messages |
| Questions de test RAG | 50 |
| Documents RAG | Environ 30 à 50 pages |

Ces valeurs constituent des objectifs à atteindre, pas des volumes déjà collectés.

## 4.3. Variables utilisées

| Variable | Description | Utilisation |
|---|---|---|
| ID | Identifiant unique | Identification |
| Text | Objet et contenu de la réclamation | Entrée principale du ML |
| Category | Catégorie réelle | Étiquette du modèle 1 |
| Priority | Priorité réelle | Étiquette du modèle 2 |
| Channel | Formulaire, e-mail ou chat | Analyse des biais |
| Date | Date de réception | Découpage temporel |
| Order_amount | Montant de la commande, si disponible | Information complémentaire pour les règles métier |
| Source | Origine publique ou synthétique | Traçabilité |

## 4.4. Préparation des données

Les données subiront plusieurs traitements :

1. Suppression des doublons.
2. Suppression ou traitement des valeurs manquantes.
3. Nettoyage léger des textes.
4. Normalisation des espaces et caractères.
5. Anonymisation des noms, adresses, e-mails et numéros de téléphone.
6. Vérification des catégories et des priorités.
7. Annotation des messages ambigus.
8. Séparation des données d'entraînement, de validation et de test.

Un échantillon de 300 messages sera annoté indépendamment par deux membres du groupe afin d'évaluer la cohérence des annotations avec le kappa de Cohen.

## 4.5. Gestion de la qualité

| Problème | Solution |
|---|---|
| Déséquilibre des classes | Pondération des classes et suivi des métriques par classe |
| Messages ambigus | Double annotation et arbitrage |
| Fautes d'orthographe | Nettoyage léger |
| Doublons | Suppression avant entraînement |
| Données personnelles | Anonymisation |
| Différence entre données réelles et synthétiques | Identification de la source et évaluation séparée |

---

# 5. Métriques, baseline et critères d'acceptation

## 5.1. Baseline

La baseline choisie est :

**TF-IDF + régression logistique avec pondération des classes.**

Cette approche constitue un premier modèle de référence pour mesurer les performances de classification.

Le macro-F1 attendu initialement est estimé entre 0,70 et 0,75. Il s'agit d'une hypothèse de départ qui devra être vérifiée sur le jeu de test.

**Résultat réel de la baseline :** à mesurer après la première phase d'entraînement.

## 5.2. Métriques principales

**Pour la classification des catégories :**

- Accuracy : proportion des prédictions correctes.
- Precision : proportion des prédictions positives correctes.
- Recall : proportion des éléments d'une classe correctement retrouvés.
- Macro-F1 : moyenne des F1-scores des différentes catégories.
- Matrice de confusion : visualisation des erreurs entre les catégories.

La métrique principale sera le macro-F1, car les différentes catégories doivent être évaluées de manière équilibrée.

**Pour la détection des urgences :**

La métrique prioritaire sera le Recall de la classe urgente.

Le système doit éviter de manquer les réclamations qui nécessitent une intervention rapide.

## 5.3. Suivi secondaire

- Precision et Recall par catégorie.
- F1-score de chaque classe.
- Matrice de confusion.
- Taux de réclamations envoyées en tri manuel.
- Temps de réponse de l'API.
- Precision de la classe urgente.
- Pour le RAG : fidélité des réponses aux sources et exactitude des citations.

## 5.4. Critères d'acceptation

| Critère | Objectif |
|---|---|
| Macro-F1 de classification | Au moins 0,82 |
| Recall de la classe urgente | Au moins 90 % |
| Gain par rapport à la baseline | Au moins 8 points de macro-F1 |
| Latence de prédiction | Inférieure à 200 ms au 95e percentile sur CPU, objectif à mesurer |
| Taux de tri manuel | Inférieur à 20 %, objectif à mesurer |
| Fidélité des réponses RAG (bonus) | Au moins 90 % sur 50 questions de test |

Les seuils seront évalués à partir des résultats réels. Si le modèle complexe n'apporte pas d'amélioration suffisante, la baseline sera conservée.

## 5.5. Découpage des données

Le découpage prévu est :

- 70 % pour l'entraînement.
- 15 % pour la validation.
- 15 % pour le test.

Le découpage sera effectué chronologiquement afin de simuler une utilisation réelle : les messages les plus récents seront réservés au test.

La représentation des différentes classes sera contrôlée dans chaque partition. Les données de test ne seront jamais utilisées pendant l'entraînement ou le réglage du modèle.

---

# 6. Architecture prévue

## 6.1. Architecture générale

L'application sera organisée autour de plusieurs composants qui communiquent entre eux.

```text
                 UTILISATEUR
                      |
                      v
          Réclamation client reçue
                      |
                      v
          Prétraitement et anonymisation
                      |
                      v
               API FASTAPI
                      |
             +--------+--------+
             |                 |
             v                 v
       Modèle catégorie   Modèle priorité
             |                 |
             +--------+--------+
                      |
                      v
             Résultats prédits
                      |
             +--------+--------+
             |                 |
             v                 v
       Confiance élevée   Confiance faible
             |                 |
             v                 v
       Orientation        Tri manuel
       proposée           par un humain
             |                 |
             +--------+--------+
                      |
                      v
              BASE POSTGRESQL
                      |
                      v
             INTERFACE STREAMLIT
                      |
           +----------+----------+
           |                     |
           v                     v
       Dashboard            Gestion des
       et alertes           réclamations

                      |
                      v
              SUIVI MLFLOW
                      |
                      v
             Suivi des modèles
             et réentraînement

       MODULE OPTIONNEL RAG
       FAQ + CGV -> Embeddings
                  -> Base vectorielle
                  -> LLM
                  -> Réponse avec source
```

## 6.2. Description des composants

| Composant | Fonction |
|---|---|
| Prétraitement | Nettoyer et anonymiser les messages |
| API FastAPI | Recevoir les messages et exposer les prédictions |
| Modèle catégorie | Identifier la catégorie de la réclamation |
| Modèle priorité | Identifier les réclamations urgentes |
| PostgreSQL | Stocker les réclamations, résultats et corrections |
| Streamlit | Fournir l'interface utilisateur |
| MLflow | Suivre les expériences et les versions des modèles |
| DVC | Versionner les données et les étapes de traitement |
| Docker | Conteneuriser l'application |
| Module RAG | Proposer des réponses à partir des documents de référence |

## 6.3. Fonctionnement de l'application

L'utilisateur accède à l'application à travers une interface web sécurisée.

Il peut :
- Consulter les statistiques générales.
- Ajouter ou consulter une réclamation.
- Lancer une classification.
- Visualiser la catégorie et la priorité.
- Consulter le score de confiance.
- Identifier les réclamations urgentes.
- Corriger les résultats.
- Consulter l'historique des réclamations.

Les corrections validées pourront être conservées pour enrichir les futurs jeux de données d'entraînement.

---

# 7. Choix technologiques

| Besoin | Outil | Justification |
|---|---|---|
| Langage principal | Python | Adapté au Machine Learning et au développement de l'API |
| Manipulation des données | Pandas | Nettoyage et préparation des données |
| Modèle de référence | Scikit-learn | Implémentation de TF-IDF et de la régression logistique |
| NLP avancé | Hugging Face Transformers | Expérimentation de CamemBERT et DistilCamemBERT |
| Exposition du modèle | FastAPI | Création d'une API documentée avec Swagger |
| Interface web | Streamlit | Développement rapide d'une interface interactive |
| Base de données | PostgreSQL | Stockage structuré des réclamations et des corrections |
| Suivi des expériences | MLflow | Comparaison des performances et suivi des versions |
| Versionnement des données | DVC | Reproductibilité des expériences |
| Tests | Pytest | Vérification du fonctionnement des composants |
| Conteneurisation | Docker et Docker Compose | Reproduction du même environnement de développement et de déploiement |
| Assistant RAG | Sentence-Transformers et ChromaDB ou FAISS | Recherche sémantique dans les documents |
| Génération de réponses | LLM | Création de brouillons à partir des passages retrouvés |

Les outils seront intégrés progressivement selon les besoins du projet.

---

# 8. Risques, éthique et confidentialité

Cette section répond aux huit questions demandées par le professeur.

## Question 1 : Les données contiennent-elles des données personnelles ? Lesquelles ?

Oui. Les réclamations réelles peuvent contenir :
- Noms et prénoms.
- Adresses e-mail.
- Numéros de téléphone.
- Adresses de livraison.
- Numéros de commande.
- Informations liées aux paiements.

**Mesure prévue :** anonymiser les données avant l'entraînement et limiter les informations conservées dans la base de données.

## Question 2 : Peut-on s'en passer ou les anonymiser ?

Oui. Les informations permettant d'identifier directement les clients ne sont pas nécessaires à la classification.

Nous prévoyons :
- La suppression des noms et coordonnées.
- Le remplacement des identifiants personnels par des identifiants fictifs.
- La suppression des informations sensibles inutiles.
- L'utilisation de données synthétiques lorsque cela est possible.

## Question 3 : Qui peut être lésé par une erreur ?

Plusieurs personnes peuvent être affectées :

- Le client dont la réclamation est mal classée.
- Le conseiller qui doit traiter une demande mal orientée.
- Le responsable qui organise les priorités.
- L'entreprise qui peut subir une perte financière ou une dégradation de son image.

**Mesure prévue :** permettre la correction humaine des prédictions et conserver un historique des modifications.

## Question 4 : Les données couvrent-elles tous les cas d'usage (lieux, périodes, populations) ?

Pas nécessairement.

Le corpus peut présenter des limites :
- Messages principalement rédigés en français.
- Peu de représentations de certains profils de clients.
- Différences de vocabulaire selon les canaux de communication.
- Évolution des produits et des politiques commerciales.
- Faible représentation de certaines réclamations rares.

**Mesure prévue :** analyser les performances par catégorie et par canal, diversifier les données et surveiller les changements dans les messages.

## Question 5 : Quelle erreur coûte le plus, et à qui ?

Le faux négatif sur la classe urgente représente le coût le plus élevé.

Une réclamation urgente classée comme normale peut entraîner :
- Un retard de prise en charge.
- Un risque financier.
- Une insatisfaction importante.
- Un risque lié à un produit dangereux ou à une fraude non signalée.

Le client et l'entreprise sont les principaux concernés.

**Mesure prévue :** privilégier le rappel de la classe urgente, ajouter des règles métier pour les cas critiques et déclencher une vérification humaine lorsque cela est nécessaire.

## Question 6 : Qui valide les décisions, et peut les corriger ?

Le responsable du service client et les conseillers autorisés valident les classifications.

Ils peuvent :
- Confirmer une prédiction.
- Modifier la catégorie.
- Modifier la priorité.
- Signaler une erreur.
- Transmettre une réclamation à une autre équipe.

Le système ne prend aucune décision définitive concernant les remboursements ou les compensations.

**Mesure prévue :** conserver la prédiction initiale, la correction humaine, la date et l'utilisateur ayant effectué la modification.

## Question 7 : Des données sortent-elles de l'organisation (API externe) ?

Dans le fonctionnement prévu, les données de réclamations sont traitées par l'application et l'API FastAPI.

Le traitement local sera privilégié.

Si un service externe est utilisé, notamment pour un LLM dans le module RAG :
- Les données personnelles seront supprimées avant tout envoi.
- Les documents envoyés seront limités aux informations nécessaires.
- Les conditions de confidentialité du fournisseur seront vérifiées.
- L'utilisation d'une API externe sera documentée.

**Mesure prévue :** limiter les échanges externes et privilégier les traitements locaux lorsque cela est possible.

## Question 8 : Comment le système pourrait-il être détourné ?

Plusieurs risques sont possibles :
- Envoi massif de fausses réclamations pour saturer le système.
- Tentatives d'accès non autorisé à l'interface.
- Manipulation des données d'entraînement.
- Utilisation abusive des informations clients.
- Tentatives d'injection de prompt dans l'assistant RAG.
- Utilisation de l'assistant pour obtenir des informations non autorisées.

**Mesure prévue :**
- Authentification des utilisateurs.
- Gestion des rôles et des autorisations.
- Validation des données reçues par l'API.
- Limitation du nombre de requêtes.
- Protection des informations sensibles.
- Contrôle des documents et des réponses du RAG.
- Journalisation des actions importantes.

## 8.1. Tableau récapitulatif des risques

| Risque | Niveau de vigilance | Mesure de prévention |
|---|---|---|
| Fuite de données personnelles | Élevé | Anonymisation et accès restreint |
| Biais du modèle | Élevé | Évaluation par classe et par canal |
| Faux négatifs urgents | Élevé | Rappel élevé et règles métier |
| Dérive des données | Moyen | Surveillance et réentraînement |
| Hallucinations du RAG | Élevé | Sources obligatoires et validation humaine |
| Attaque de l'API | Élevé | Authentification et validation des entrées |
| Données synthétiques peu réalistes | Moyen | Comparaison avec des données réelles disponibles |
| Erreur humaine | Moyen | Historique et correction contrôlée |

Le projet prendra également en compte les exigences applicables de la loi marocaine 09-08 relative à la protection des données personnelles et les principes pertinents du RGPD lorsque celui-ci est applicable.

---

# 9. Limites et hors périmètre

## 9.1. Limites du projet

Le système présente certaines limites :

- Les performances dépendent de la qualité et de la diversité du dataset.
- Les messages ambigus peuvent être mal classés.
- Les résultats obtenus sur des données synthétiques peuvent être plus optimistes que sur des messages réels.
- Les modèles peuvent être moins performants sur des messages très courts ou contenant des expressions inhabituelles.
- La détection des urgences dépend de la qualité des annotations.
- Le système peut nécessiter un réentraînement lorsque les habitudes des clients évoluent.

## 9.2. Fonctionnalités hors périmètre

Le projet ne prévoit pas :

1. L'envoi automatique de réponses aux clients.
2. L'intégration à un véritable CRM commercial.
3. L'accès à un vrai système de commande ou de paiement.
4. La réalisation automatique des remboursements.
5. La prise de décisions financières ou commerciales.
6. La classification des messages en arabe ou en darija dans la première version.
7. L'analyse automatique des pièces jointes, images et fichiers PDF.
8. La gestion complète de toutes les opérations d'une boutique en ligne.

## 9.3. Périmètre fonctionnel retenu

La première version de ShopExpress AI se concentre sur quatre fonctionnalités principales :

- La réception et la consultation des réclamations.
- La classification automatique en six catégories.
- La détection des priorités urgentes et normales.
- La visualisation des résultats et la correction humaine.

L'assistant RAG constitue une fonctionnalité complémentaire qui sera développée après la réalisation des fonctionnalités obligatoires.

---

# ANNEXE A – Répartition des tâches du groupe

| Membre | Responsabilités principales |
|---|---|
| Zainab Belgas | Coordination du projet, conception de l'architecture, intégration de l'API et de la base de données |
| Marwa Elomari Alaoui | Recherche et préparation du dataset, nettoyage, anonymisation et annotation des données |
| Amira Zahr | Développement des modèles ML, entraînement, évaluation et comparaison des métriques |
| Chaimaa Ezzerag | Développement de l'interface Streamlit, tests, documentation et participation au module RAG |

L'intégration finale, les tests et la préparation de la présentation seront réalisés collectivement.

---

# ANNEXE B – Livrables techniques prévus

| Livrable | Contenu |
|---|---|
| Étude de conception | Présent document |
| Dataset | Corpus nettoyé et annoté |
| Notebook ML | Exploration, préparation et entraînement |
| Modèles ML | Modèle de catégorie et modèle de priorité |
| API | API FastAPI documentée et sécurisée |
| Application web | Interface de gestion des réclamations |
| Base de données | Tables et relations PostgreSQL |
| Tests | Tests unitaires et tests d'intégration |
| Suivi ML | Expériences MLflow et versionnement DVC |
| Déploiement | Docker et procédure de déploiement |
| Documentation | README, architecture et guide d'utilisation |
| Bonus RAG | Assistant documentaire avec citations des sources |

---

# Conclusion

ShopExpress AI vise à améliorer la gestion des réclamations clients en utilisant le Machine Learning et le traitement automatique du langage naturel.

Le projet repose sur deux modèles principaux permettant d'identifier la catégorie d'une réclamation et son niveau de priorité.

L'application fournit une interface permettant aux responsables de consulter les résultats, de corriger les erreurs et de suivre les performances du système.

L'objectif final est de proposer une solution reproductible, sécurisée, documentée et déployable, tout en conservant la validation humaine pour les décisions importantes.

L'ajout d'un assistant RAG permettra d'enrichir la solution en proposant des réponses basées sur des documents de référence, sans remplacer le rôle des conseillers.

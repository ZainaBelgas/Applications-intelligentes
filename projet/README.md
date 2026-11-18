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

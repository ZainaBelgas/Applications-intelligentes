# Applications intelligentes

Dépôt d’équipe du module **Développement et déploiement d’applications intelligentes**, à l’EMSI, année universitaire 2026–2027.

Le dépôt regroupe les travaux pratiques autour de **MaintAI**, une application de maintenance prédictive, et l’étude de conception de **ShopExpress AI**, notre projet de classification des réclamations clients.

## Équipe

| Membre | Rôle dans le projet |
| --- | --- |
| Zainab Belgas | Responsable de l’équipe |
| Marwa Elomari Alaoui | Membre du projet |
| Amira Zahr | Membre du projet |
| Chaimaa Ezzerag | Membre du projet |

## Projet d’équipe — ShopExpress AI

ShopExpress AI vise à aider le service client d’une plateforme e-commerce fictive à traiter ses réclamations. À partir du texte d’un message, l’application doit proposer une catégorie, par exemple livraison, produit défectueux ou remboursement, et estimer si la demande est urgente. Un conseiller peut vérifier les prédictions et corriger le classement avant l’orientation vers le service concerné.

Le dépôt contient l’étude de conception. Elle décrit les utilisateurs, les données, les critères d’évaluation, l’architecture prévue et les règles de validation humaine. Une extension RAG est envisagée pour répondre aux questions à partir d’une FAQ et de conditions générales de vente fictives.

[Consulter l’étude de conception de ShopExpress AI](projet/README.md)

## Travaux pratiques — MaintAI

MaintAI estime le risque de panne d’une machine à partir de quatre mesures simulées. Le modèle utilise la température, la vibration, la charge et les heures de fonctionnement. L’API FastAPI renvoie une probabilité de panne et déclenche une alerte si le seuil configuré est atteint. L’interface Streamlit permet d’explorer les données et de soumettre un relevé.

| TP | Sujet | Dossier |
| --- | --- | --- |
| TP0 | Étude de conception et choix du modèle | [TP0](tp/tp0/) |
| TP1 | API FastAPI de prédiction et validation des relevés | [TP1](tp/tp1/) |
| TP2 | Protection de l’API par clé et utilisation depuis un client web | [TP2](tp/tp2/) |
| TP3 | Exploration des données et prédiction dans Streamlit | [TP3](tp/Tp3/) |
| TP4 | Distribution de MaintAI comme package Python et ajout d’une commande | [TP4](tp/TP4/) |
| TP5 | Suivi des entraînements avec MLflow et versionnement des données avec DVC | [TP5](tp/tp5/) |
| TP6 | Conteneurisation de l’API et de l’interface avec Docker Compose | [TP6](tp/Tp6/) |

Les dossiers des TP regroupent les rendus et les comptes rendus des membres de l’équipe.

### Lancer la démonstration du TP6

Avec Python 3.11 et Docker Desktop démarré, exécuter ces commandes dans PowerShell depuis la racine du dépôt.

```powershell
cd .\tp\Tp6\Zainab\TP6
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m maintai.dataset
.\.venv\Scripts\python.exe -m maintai.train
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Choisir une clé locale dans `.env` en remplaçant la valeur de `MAINTAI_API_KEY`. Garder ce fichier hors de Git. Puis démarrer les services.

```powershell
docker compose up --build -d
```

Ouvrir [l’interface Streamlit](http://localhost:8501), garder `http://api:8000` comme URL de l’API dans la barre latérale, saisir la clé locale et cliquer sur **Prédiction → Prédire**. La documentation interactive est accessible sur [Swagger](http://localhost:8000/docs).

```powershell
.\.venv\Scripts\python.exe -m pytest
docker compose down
```

Le rendu de Zainab documente les **38 tests réussis** et la vérification de la prédiction dans Docker. Le modèle est chargé depuis `models/` au démarrage de l’API, ce qui permet de le mettre à jour sans reconstruire l’image.

- [Compte rendu du TP6](tp/Tp6/Zainab/TP6/COMPTE_RENDU.md)
- [ADR 005 — Décision sur le montage du modèle](tp/Tp6/Zainab/TP6/docs/adr/005-image-docker.md)
- [Version rendue du TP6](https://github.com/ZainaBelgas/Applications-intelligentes/tree/refs/tags/tp6)

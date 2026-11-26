# Actions Git finales pour remise TP6

**À exécuter dans PowerShell depuis la racine du projet TP5-rendu (1)**

---

## 1️⃣ Vérifier l'état du dépôt

```powershell
cd "C:\Users\Sasam\OneDrive\Desktop\TP5-rendu (1)"
git status
```

**Attendu :** Les fichiers suivants doivent apparaître comme `modified` ou `untracked` :
- `TP/TP6/COMPTE_RENDU.md`
- `TP/TP6/docs/adr/005-image-docker.md`
- `TP/TP6/SYNTHESE_AUDIT.md` (optionnel)

**À NE PAS voir :** `.env`, `models/`, `data/`, `TP/TP6/.env.example`

---

## 2️⃣ Ajouter les fichiers (staging)

```powershell
git add TP\TP6\Dockerfile
git add TP\TP6\.dockerignore
git add TP\TP6\compose.yaml
git add TP\TP6\requirements-docker.txt
git add TP\TP6\COMPTE_RENDU.md
git add TP\TP6\docs\adr\005-image-docker.md
git add TP\TP6\tests\test_docker.py
git add TP\TP6\.env.example
```

**Alternative (une seule ligne) :**

```powershell
git add TP\TP6\Dockerfile TP\TP6\.dockerignore TP\TP6\compose.yaml TP\TP6\requirements-docker.txt TP\TP6\COMPTE_RENDU.md TP\TP6\docs\adr\005-image-docker.md TP\TP6\tests\test_docker.py TP\TP6\.env.example
```

---

## 3️⃣ Vérifier le staging

```powershell
git status
```

**Attendu :** Sous la section "Changes to be committed", vous devriez voir les 8 fichiers ajoutés.

**À NE PAS voir :** `.env`, `models/`, `data/`

---

## 4️⃣ Commit

```powershell
git commit -m "TP6 : Conteneuriser MaintAI avec Docker et Docker Compose

- Dockerfile basé sur python:3.11-slim
- requirements-docker.txt avec dépendances figées, scikit-learn 1.8.0
- .dockerignore exclut modèle, données, secrets et caches
- compose.yaml orchestre les services API et UI
- Volumes montés en lecture seule pour modèle et données
- Variables d'environnement injectées via .env
- 38 tests passent, incluant validations Docker
- ADR 005 complétée et signée
- Compte rendu professionnel, 525 lignes"
```

**Résultat attendu :**
```
[main ...] TP6 : Conteneuriser MaintAI avec Docker et Docker Compose
 8 files changed, ...
```

---

## 5️⃣ Pousser vers le dépôt distant

```powershell
git push origin main
```

**Ou si vous travaillez sur une autre branche :**

```powershell
git branch  # Voir la branche actuelle
git push origin <branche-actuelle>
```

**Résultat attendu :**
```
Enumerating objects: ...
Counting objects: ...
Compressing objects: ...
Writing objects: 100% (...), done.
To https://github.com/...
   <hash>..<hash>  <branche> -> <branche>
```

---

## 6️⃣ Créer le tag `tp6`

```powershell
git tag -a tp6 -m "TP6 : Conteneurisation avec Docker et Docker Compose"
```

**Vérifier le tag :**

```powershell
git tag -l tp6
```

**Résultat attendu :** Affiche `tp6`

---

## 7️⃣ Pousser le tag vers le dépôt distant

```powershell
git push origin tp6
```

**Résultat attendu :**
```
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/...
 * [new tag]         tp6 -> tp6
```

---

## 8️⃣ Vérifier l'historique

```powershell
git log --oneline -5
```

**Résultat attendu :** Le dernier commit doit afficher "TP6 : Conteneuriser MaintAI..."

```powershell
git tag -l
```

**Résultat attendu :** Affiche `tp5` (ancien), `tp6` (nouveau), et éventuellement d'autres tags.

---

## Checklist finale

Avant de terminer, vérifier :

- [ ] `git status` montre "nothing to commit" (après le push)
- [ ] Le tag `tp6` est créé localement (`git tag -l tp6`)
- [ ] Le tag `tp6` est poussé sur GitHub
- [ ] Le commit contient tous les 8 fichiers
- [ ] `.env`, `models/`, `data/` ne sont **jamais** commitris
- [ ] Les tests passent toujours : `python -m pytest` → 38 passed
- [ ] Le compte rendu est lisible et complet

---

## 🎯 Résumé des commandes (copie-coller rapide)

```powershell
cd "C:\Users\Sasam\OneDrive\Desktop\TP5-rendu (1)"
git status
git add TP\TP6\Dockerfile TP\TP6\.dockerignore TP\TP6\compose.yaml TP\TP6\requirements-docker.txt TP\TP6\COMPTE_RENDU.md TP\TP6\docs\adr\005-image-docker.md TP\TP6\tests\test_docker.py TP\TP6\.env.example
git status
git commit -m "TP6 : Conteneuriser MaintAI avec Docker et Docker Compose

- Dockerfile basé sur python:3.11-slim
- requirements-docker.txt avec dépendances figées, scikit-learn 1.8.0
- .dockerignore exclut modèle, données, secrets et caches
- compose.yaml orchestre les services API et UI
- Volumes montés en lecture seule pour modèle et données
- Variables d'environnement injectées via .env
- 38 tests passent, incluant validations Docker
- ADR 005 complétée et signée
- Compte rendu professionnel, 525 lignes"
git push origin main
git tag -a tp6 -m "TP6 : Conteneurisation avec Docker et Docker Compose"
git push origin tp6
git log --oneline -5
git tag -l
```

---

## 📌 Notes importantes

1. **Remplacer `main` par votre branche** si elle porte un autre nom (p. ex., `master`, `develop`)
2. **Ne pas pousser `.env` ou `models/`** — ils doivent rester locaux
3. **Le tag `tp6` doit être poussé séparément** avec `git push origin tp6`
4. **Les 38 tests doivent toujours passer** : `python -m pytest`
5. **Vérifier sur GitHub** que le commit et le tag sont visibles

---

**Prêt ? Let's go ! 🚀**

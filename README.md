# OC_DE_P5

Projet d'entraînement: migrer un fichier CSV vers MongoDB en local, étape par étape.

## Prérequis (avant de commencer)
- Docker Desktop (Windows/macOS) ou Docker CE (Linux)
  - Pourquoi ? Pour lancer MongoDB rapidement sans l’installer en dur.
- Git

## Données utilisées
- Fichier CSV: `data/healthcare_dataset.csv`
  - Déjà présent dans le dépôt pour faciliter la reproduction.

## Démarrer MongoDB en local (avec Docker)
Objectif: lancer une base MongoDB locale accessible sur le port 27017.

1) Créer un volume pour conserver les données entre les redémarrages:
```bash
docker volume create mongodb_data
```

2) Lancer le conteneur MongoDB (image officielle 5.0):
```bash
docker run -d --name mongo -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secure_password \
  -v mongodb_data:/data/db \
  --restart unless-stopped \
  mongo:5.0
```

3) Vérifier que la base répond:
```bash
docker exec -it mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.adminCommand({ ping: 1 })"
```
- Si la commande ne marche pas, ouvrez Docker Desktop, attendez qu’il soit “running”, puis réessayez.

## Dépendances Python (étape actuelle)
- requirements.txt minimal: 
  - pymongo==4.7.2

Installer les dépendances:
```bash
pip install -r requirements.txt
```

## Structure du projet (actuelle)
```text
.
├── data/
│   └── healthcare_dataset.csv
├── src/
│   └── __init__.py
├── tests/
├── requirements.txt
├── README.md
└── JOURNAL_DE_BORD.md
```
- Remarque: `tests/` est vide pour l’instant (les tests seront ajoutés plus tard).

## Portée du dépôt
- Ce qui est versionné: scripts du projet, ce README, et le dataset dans `data/`.
- Ce qui n’est pas versionné: documents personnels/ressources pédagogiques (voir `.gitignore`).

## Prochaines étapes (plan de travail)
- Écrire le script de migration CSV → MongoDB
- Ajouter des tests d’intégrité (avant/après migration)

Ce README sera complété au fur et à mesure des étapes (exécution des scripts, schéma MongoDB, tests).

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
- requirements.txt : 
  - pymongo==4.7.2
  - pandas==2.2.2

Installer les dépendances:
```bash
pip install -r requirements.txt
```

## Environnement virtuel Python (recommandé)
Objectif: isoler les dépendances du projet.

1) Créer l'environnement virtuel :
```bash
python -m venv venv
```

2) Activer l'environnement :
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3) Installer les dépendances :
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4) Vérifier l'installation :
```bash
pip list
```

## Structure du projet (actuelle)
```text
.
├── data/
│   └── healthcare_dataset.csv
├── docker/                 # Fichiers de containerisation
│   ├── Dockerfile          # Image service migration
│   ├── .dockerignore       # Exclusions pour le build
│   └── docker-compose.yml  # Orchestration des services
├── src/
│   ├── __init__.py
│   ├── migrate.py          # Script de migration CSV → MongoDB
│   └── crud_demo.py        # Démonstration des opérations CRUD
├── tests/
│   └── test_data_integrity.py  # Validation avant/après migration
├── requirements.txt
├── README.md
└── JOURNAL_DE_BORD.md
```

## Tests d'intégrité réalisés
- Validation complète : **100% de réussite** (3/3 tests)
- 55 500 lignes CSV = 55 500 documents MongoDB
- Structure des données préservée (15 champs)
- Migration validée sans perte de données

## Exécuter la migration CSV → MongoDB
Objectif: charger le CSV dans la base locale.

1) Lancer le script (par défaut, lit `data/healthcare_dataset.csv` et écrit dans `healthcare_db.patient_records`):
```bash
python src/migrate.py
```

2) Variables d’environnement optionnelles (si besoin d’adapter):
```bash
# Exemples
set CSV_PATH=data\healthcare_dataset.csv
set MONGO_HOST=localhost
set MONGO_PORT=27017
set MONGO_USER=admin
set MONGO_PASSWORD=secure_password
set MONGO_AUTH_DB=admin
set MONGO_DB=healthcare_db
set MONGO_COLLECTION=patient_records
```

3) Vérifier rapidement le nombre de documents:
```bash
docker exec -it mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.getSiblingDB('healthcare_db').patient_records.countDocuments({})"
```

## Portée du dépôt
- Ce qui est versionné: scripts du projet, ce README, et le dataset dans `data/`.
- Ce qui n’est pas versionné: documents personnels/ressources pédagogiques (voir `.gitignore`).

## Étapes réalisées
- ✅ **Étape 1** : Migration vers MongoDB
  - Script de migration fonctionnel (55 500 enregistrements)
  - Opérations CRUD démontrées
  - Tests d'intégrité validés (100% de réussite)
- ✅ **Étape 2** : Conteneurisation avec Docker (terminée)
  - Structure Docker créée et organisée (`docker/` dossier)
  - Dockerfile fonctionnel (image `healthcare-migration` optimisée)
  - .dockerignore configuré (build 29s → 1.3s, amélioration 95%)
  - docker-compose.yml opérationnel (MongoDB + Migration orchestrés)
  - Commande de lancement : `docker-compose -f docker/docker-compose.yml up -d`

## Commandes Docker (Étape 2 terminée)

**Lancement complet de l'environnement :**
```bash
# Démarrer MongoDB + Migration
docker-compose -f docker/docker-compose.yml up -d

# Vérifier les services
docker-compose -f docker/docker-compose.yml ps

# Voir les logs
docker-compose -f docker/docker-compose.yml logs

# Arrêter
docker-compose -f docker/docker-compose.yml down
```

## Prochaines étapes (plan de travail)
- 🔄 **Étape 3** : Recherche AWS (analyse comparative)
- **Étape 4** : Support de présentation (slides soutenance)

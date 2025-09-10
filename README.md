# OC_DE_P5

Migration de données CSV vers MongoDB avec conteneurisation Docker.

## Contexte du projet

Ce projet implémente la migration automatisée d'un dataset médical au format CSV vers une base de données MongoDB. L'ensemble de la solution est conteneurisée avec Docker pour assurer la portabilité et la reproductibilité.

Le dataset contient 55 500 enregistrements de données médicales patient qui sont migrés vers une collection MongoDB `patient_records` dans la base `healthcare_db`.

## Installation

### Prérequis
- Docker Desktop (Windows/macOS) ou Docker CE (Linux)
- Python 3.8+ avec pip
- Git

### Étapes d'installation

1. Cloner le repository :
```bash
git clone <repository-url>
cd P5_OC_DE
```

2. Créer l'environnement virtuel :
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Lancer l'environnement Docker :
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Architecture du projet

```
.
├── data/
│   └── healthcare_dataset.csv    # Données source (55 500 enregistrements)
├── docker/
│   ├── docker-compose.yml        # Orchestration des services
│   ├── Dockerfile               # Image du service de migration
│   └── .dockerignore            # Exclusions du build
├── src/
│   ├── migrate.py               # Script principal de migration
│   └── crud_demo.py             # Démonstration des opérations CRUD
├── tests/
│   ├── test_migration_integrity.py  # Tests automatisés
│   └── conftest.py              # Configuration des tests
├── requirements.txt             # Dépendances Python
└── pytest.ini                  # Configuration pytest
```

## Schéma de base de données

Les données sont stockées dans MongoDB selon la structure suivante :

### Base de données : `healthcare_db`
### Collection : `patient_records`

Chaque document représente un enregistrement patient avec la structure :
```javascript
{
  "patient_id": "P001",           // Identifiant unique du patient
  "record_type": "consultation",  // Type d'enregistrement médical
  "date_recorded": "2023-10-15",  // Date d'enregistrement
  "age": "45",                    // Âge du patient
  "name": "John Doe",             // Nom du patient
  "medical_condition": "Hypertension",  // Condition médicale
  "date_of_admission": "2023-10-15",    // Date d'admission
  // ... autres champs du CSV
}
```

## Utilisation

### Migration des données

Le script principal migre automatiquement les données CSV vers MongoDB :

```bash
# Migration automatique via Docker
docker-compose -f docker/docker-compose.yml up -d

# Le service de migration s'exécute automatiquement
# Vérification des logs
docker-compose -f docker/docker-compose.yml logs migration
```

### Connexion à MongoDB

```bash
# Connexion à MongoDB via Docker
docker exec -it healthcare_mongo mongosh -u admin -p secure_password --authenticationDatabase admin

# Vérification des données migrées
use healthcare_db
db.patient_records.countDocuments({})
db.patient_records.findOne()
```

### Opérations CRUD

Le script `crud_demo.py` démontre les opérations de base :

```bash
# Exécution des opérations de démonstration
python src/crud_demo.py
```

Ce script montre :
- Création de nouveaux documents
- Lecture et recherche de données
- Mise à jour d'enregistrements existants
- Suppression de documents

## Logique de migration

### Fonctionnement du script `migrate.py`

Le script de migration suit cette logique :

1. **Connexion à MongoDB**
   - Utilise les variables d'environnement pour la connexion
   - Supporte les environnements Docker et locaux

2. **Lecture du CSV**
   - Utilise la bibliothèque `csv` standard de Python
   - Lecture par lots pour optimiser la mémoire
   - Taille de lot configurable (défaut : 1000 lignes)

3. **Validation et transformation**
   - Vérification de la structure des données
   - Conversion des types si nécessaire
   - Gestion des valeurs manquantes

4. **Insertion dans MongoDB**
   - Utilise `insert_many()` avec `ordered=False`
   - Traitement par lots pour les performances
   - Gestion des erreurs partielles

5. **Rapport final**
   - Nombre total de lignes lues
   - Nombre de documents insérés avec succès
   - Nombre d'erreurs rencontrées

### Gestion des environnements

Le script détecte automatiquement l'environnement d'exécution :

- **Environnement Docker** : Utilise `/data/healthcare_dataset.csv`
- **Environnement local** : Utilise `data/healthcare_dataset.csv`

Cette logique permet d'exécuter le même script dans les deux contextes sans modification.

## Exécution locale

### Préparation de l'environnement

1. **Installer MongoDB localement** (si Docker n'est pas utilisé) :
```bash
# Sur Ubuntu/Debian
sudo apt-get install mongodb

# Sur macOS avec Homebrew
brew install mongodb-community

# Démarrer MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS
```

2. **Créer la base de données** :
```bash
# Connexion à MongoDB
mongosh

# Créer la base et l'utilisateur admin
use healthcare_db
db.createUser({
  user: "admin",
  pwd: "secure_password",
  roles: ["readWrite", "dbAdmin"]
})
```

### Exécution du script de migration

```bash
# Avec variables d'environnement
export MONGO_HOST="localhost"
export MONGO_PORT="27017"
export MONGO_USER="admin"
export MONGO_PASSWORD="secure_password"
export MONGO_DB="healthcare_db"

# Exécution du script
python src/migrate.py
```

### Vérification des résultats

```bash
# Connexion à MongoDB
mongosh -u admin -p secure_password --authenticationDatabase healthcare_db

# Vérifications
use healthcare_db
db.patient_records.countDocuments({})
db.patient_records.findOne()
```

## Choix techniques et justifications

### Choix de MongoDB
- **Justification** : Base de données NoSQL adaptée aux données médicales semi-structurées
- **Avantages** : Flexibilité du schéma, performance sur les données volumineuses
- **Alternative considérée** : SQL traditionnel (rejeté pour la rigidité du schéma)

### Choix de Docker
- **Justification** : Portabilité et reproductibilité de l'environnement
- **Avantages** : Élimination des conflits de dépendances, déploiement simplifié
- **Alternative considérée** : Installation native (rejetée pour les problèmes de compatibilité)

### Choix de Python
- **Justification** : Écosystème riche pour le traitement de données
- **Avantages** : Pandas pour CSV, PyMongo pour MongoDB, tests avec pytest
- **Version choisie** : Python 3.8+ pour la stabilité et les fonctionnalités modernes

### Architecture de migration
- **Traitement par lots** : Optimise l'utilisation mémoire pour les gros volumes
- **Gestion d'erreurs** : `ordered=False` permet la poursuite malgré les erreurs partielles
- **Variables d'environnement** : Flexibilité entre environnements Docker et locaux

## Tests

### Exécution des tests

```bash
# Tests complets
pytest tests/test_migration_integrity.py -v

# Rapport HTML
pytest tests/ --html=reports/test_results.html
```

### Couverture des tests
- Structure et qualité des données CSV
- Connexion et intégrité MongoDB
- Performance des requêtes
- Complétude de la migration

## Configuration Docker

### Services
- **MongoDB** : Base de données principale (port 27017)
- **Migration** : Service de migration des données

### Variables d'environnement
- `MONGO_INITDB_ROOT_USERNAME` : admin
- `MONGO_INITDB_ROOT_PASSWORD` : secure_password
- `MONGO_HOST` : mongo
- `MONGO_PORT` : 27017

### Note sur l'authentification

Ce projet utilise l'authentification de base MongoDB avec un utilisateur administrateur. Pour un environnement de production, il est recommandé d'implémenter un système d'authentification plus avancé avec des rôles utilisateurs spécifiques selon les besoins métier.

## Commandes Docker principales

```bash
# Démarrage complet
docker-compose -f docker/docker-compose.yml up -d

# Vérification des services
docker-compose -f docker/docker-compose.yml ps

# Consultation des logs
docker-compose -f docker/docker-compose.yml logs migration

# Arrêt et nettoyage
docker-compose -f docker/docker-compose.yml down -v
```

## Dépendances

```
pymongo==4.7.2      # Driver MongoDB Python
pandas==2.2.2       # Traitement des données CSV
pytest==8.2.2       # Framework de tests
pytest-html==4.1.1  # Rapports de tests HTML
```

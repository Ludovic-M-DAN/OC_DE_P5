# OC_DE_P5

Projet d'entraînement: migrer un fichier CSV vers MongoDB en local, étape par étape.

## Prérequis
- Docker Desktop (Windows/macOS) ou Docker CE (Linux)
- Python 3.8+ avec pip
- Git

## Données utilisées
- Fichier CSV: `data/healthcare_dataset.csv` (55 500 enregistrements de données médicales)
  - Déjà présent dans le dépôt pour faciliter la reproduction

## Installation rapide

1) **Cloner le projet :**
```bash
git clone <repo-url>
cd P5_OC_DE
```

2) **Créer l'environnement virtuel Python :**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3) **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

4) **Lancer l'environnement complet avec Docker :**
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Structure du projet
```text
.
├── data/
│   └── healthcare_dataset.csv          # Dataset source (55 500 enregistrements)
├── docker/                             # Configuration Docker
│   ├── Dockerfile                      # Image service migration
│   ├── .dockerignore                   # Exclusions pour le build
│   └── docker-compose.yml              # Orchestration MongoDB + Migration
├── src/
│   ├── __init__.py
│   ├── migrate.py                      # Script de migration CSV → MongoDB
│   └── crud_demo.py                    # Démonstration des opérations CRUD
├── tests/
│   ├── conftest.py                     # Configuration pytest
│   ├── test_migration_integrity.py     # Tests automatisés (13 tests)
│   └── test_data_integrity.py          # Script legacy (déprécié)
├── requirements.txt                    # Dépendances Python
├── pytest.ini                         # Configuration pytest
├── README.md
└── JOURNAL_DE_BORD.md                  # Journal de développement
```

## Tests automatisés

**Framework pytest implémenté :**
- ✅ **13 tests PASSED** (100% de réussite)
- ✅ Tests CSV : structure, qualité, colonnes requises
- ✅ Tests MongoDB : connexion, collection, données, structure
- ✅ Tests de performance : temps de réponse, index
- ✅ Tests de complétude : migration complète vérifiée

**Exécuter les tests :**
```bash
# Tous les tests
pytest tests/test_migration_integrity.py -v

# Avec rapport HTML
pytest tests/ --html=reports/test_results.html
```

## Commandes Docker

**Gestion de l'environnement :**
```bash
# Démarrer tous les services (MongoDB + Migration)
docker-compose -f docker/docker-compose.yml up -d

# Vérifier l'état des services
docker-compose -f docker/docker-compose.yml ps

# Voir les logs de migration
docker-compose -f docker/docker-compose.yml logs migration

# Arrêter tous les services
docker-compose -f docker/docker-compose.yml down

# Nettoyer (supprimer les volumes)
docker-compose -f docker/docker-compose.yml down -v
```

**Vérification de la migration :**
```bash
# Compter les documents dans MongoDB
docker exec -it healthcare_mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.getSiblingDB('healthcare_db').patient_records.countDocuments({})"

# Voir un échantillon de données
docker exec -it healthcare_mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.getSiblingDB('healthcare_db').patient_records.findOne()"
```

## État du projet

### ✅ **Étape 1 - Migration vers MongoDB** (TERMINÉE)
- Script de migration fonctionnel (55 500 enregistrements)
- Opérations CRUD démontrées
- Tests d'intégrité automatisés (13/13 tests passent)

### ✅ **Étape 2 - Conteneurisation Docker** (TERMINÉE)
- Docker Compose opérationnel (MongoDB + Migration)
- Migration automatisée au démarrage
- Tests automatisés avec pytest

### 🔄 **Prochaines étapes**
- **Étape 3** : Recherche AWS (analyse comparative)
- **Étape 4** : Support de présentation (slides soutenance)

## Dépendances

**requirements.txt :**
```
pymongo==4.7.2
pandas==2.2.2
pytest==8.2.2
pytest-html==4.1.1
```

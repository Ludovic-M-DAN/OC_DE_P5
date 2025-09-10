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

## 🔐 Authentification et sécurité MongoDB

### Architecture d'authentification

Le système implémente une authentification par rôle utilisateur adaptée aux données médicales sensibles :

- **Principe de moindre privilège** : Chaque utilisateur n'a que les permissions nécessaires
- **Séparation des responsabilités** : Rôles distincts pour migration, analyse, et accès clinique
- **Audit et traçabilité** : Logs d'accès pour toutes les opérations

### Rôles utilisateurs configurés

| Rôle | Utilisateur | Permissions | Usage |
|------|-------------|-------------|-------|
| **Admin** | `admin` | Accès complet | Configuration système |
| **Migration** | `migration_user` | Lecture/Écriture | Migration des données CSV |
| **ReadOnly** | `readonly_user` | Lecture seule | Analyses et rapports |
| **Healthcare** | `healthcare_user` | Lecture limitée | Applications cliniques |

### Configuration automatique

**Au démarrage Docker :**
```bash
# Démarre MongoDB et configure automatiquement les utilisateurs
docker-compose -f docker/docker-compose.yml up -d

# Vérifie que tous les utilisateurs sont créés
docker-compose -f docker/docker-compose.yml logs setup_auth
```

**Configuration manuelle :**
```bash
# Créer tous les utilisateurs et rôles
python src/setup_auth.py

# Tester les permissions de chaque rôle
python src/auth_demo.py
```

### Utilisation des différents rôles

**Pour la migration (recommandé) :**
```bash
# Utilise automatiquement migration_user
docker-compose -f docker/docker-compose.yml up migration
```

**Pour les analyses en lecture seule :**
```bash
# Connexion en lecture seule
docker exec -it healthcare_mongo mongosh -u readonly_user -p readonly_secure_2024 --authenticationDatabase healthcare_db

# Dans MongoDB shell
use healthcare_db
db.patient_records.countDocuments({})
```

**Pour les applications cliniques :**
```bash
# Connexion limitée aux données patient
docker exec -it healthcare_mongo mongosh -u healthcare_user -p healthcare_secure_2024 --authenticationDatabase healthcare_db

# Requêtes cliniques autorisées
db.patient_records.find({"age": {"$gte": "65"}})
db.patient_records.countDocuments({"diagnosis": {"$regex": "diabetes", "$options": "i"}})
```

### Sécurité des mots de passe

- **Hachage automatique** : MongoDB hache tous les mots de passe stockés
- **Communications chiffrées** : Utilisation de connexions sécurisées
- **Variables d'environnement** : Pas de mots de passe en dur dans le code
- **Rotation recommandée** : Changer régulièrement en production

### Test de sécurité

**Vérifier les permissions :**
```bash
# Tester que readonly ne peut pas écrire
docker exec -it healthcare_mongo mongosh -u readonly_user -p readonly_secure_2024 --authenticationDatabase healthcare_db --eval "
  db.patient_records.insertOne({test: 'should_fail'});
  // Devrait échouer avec unauthorized
"

# Tester que migration peut écrire
docker exec -it healthcare_mongo mongosh -u migration_user -p migration_secure_2024 --authenticationDatabase healthcare_db --eval "
  db.patient_records.insertOne({patient_id: 'TEST', diagnosis: 'Test migration'});
  // Devrait réussir
"
```

### Conformité RGPD/HIPAA

- **Accès contrôlé** : Seuls les rôles autorisés peuvent accéder aux données
- **Logs d'audit** : Traçabilité de tous les accès aux données médicales
- **Chiffrement** : Protection des données en transit et au repos
- **Rétention** : Durée de conservation définie pour les données sensibles

## 🔑 Guide pratique d'authentification

### Comment s'authentifier avec MongoDB

#### 1. **Connexion avec l'utilisateur admin (configuration)**
```bash
# Connexion via Docker
docker exec -it healthcare_mongo mongosh -u admin -p secure_password --authenticationDatabase admin

# Dans MongoDB shell
use healthcare_db
db.patient_records.countDocuments({})
```

#### 2. **Connexion avec l'utilisateur migration (migration des données)**
```bash
# Connexion pour migration
docker exec -it healthcare_mongo mongosh -u migration_user -p migration_secure_2024 --authenticationDatabase healthcare_db

# Dans MongoDB shell
use healthcare_db
db.patient_records.insertMany([...])  // Écriture autorisée
db.patient_records.find({...})         // Lecture autorisée
```

#### 3. **Connexion avec l'utilisateur readonly (analyses)**
```bash
# Connexion en lecture seule
docker exec -it healthcare_mongo mongosh -u readonly_user -p readonly_secure_2024 --authenticationDatabase healthcare_db

# Dans MongoDB shell
use healthcare_db
db.patient_records.find({...})         // Lecture autorisée
db.patient_records.countDocuments({})  // Lecture autorisée
// db.patient_records.insertOne({...}) // ÉCRITURE INTERDITE ❌
```

#### 4. **Connexion avec l'utilisateur healthcare (applications cliniques)**
```bash
# Connexion pour applications médicales
docker exec -it healthcare_mongo mongosh -u healthcare_user -p healthcare_secure_2024 --authenticationDatabase healthcare_db

# Dans MongoDB shell
use healthcare_db
db.patient_records.find({"age": {"$gte": 65}})  // Lecture autorisée
db.patient_records.find({"diagnosis": {"$regex": "diabetes", "$options": "i"}})  // Lecture autorisée
```

### Comment changer de rôle utilisateur

#### **Méthode 1 : Nouvelle connexion**
```bash
# Fermer la connexion actuelle (Ctrl+C ou exit)
exit

# Se reconnecter avec un autre utilisateur
docker exec -it healthcare_mongo mongosh -u nouveau_user -p nouveau_password --authenticationDatabase healthcare_db
```

#### **Méthode 2 : Via les variables d'environnement**
```bash
# Définir les variables d'environnement
export MONGO_USER="readonly_user"
export MONGO_PASSWORD="readonly_secure_2024"
export MONGO_AUTH_DB="healthcare_db"

# Utiliser dans les scripts Python
python src/migrate.py  # Utilise automatiquement readonly_user
```

#### **Méthode 3 : Configuration dans docker-compose**
```yaml
# Dans docker-compose.yml, changer les variables d'environnement
environment:
  - MONGO_USER=migration_user        # Change ici
  - MONGO_PASSWORD=migration_secure_2024  # Change ici
  - MONGO_AUTH_DB=healthcare_db
```

### Gestion des rôles et permissions

#### **Vérifier les utilisateurs créés**
```bash
docker exec -it healthcare_mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "
  use healthcare_db
  db.getUsers().users.forEach(u => {
    print('👤 Utilisateur:', u.user)
    print('   Rôles:', u.roles.map(r => r.role).join(', '))
    print('')
  })
"
```

#### **Tester les permissions d'un utilisateur**
```bash
# Test de lecture (devrait réussir pour tous les rôles)
docker exec -it healthcare_mongo mongosh -u readonly_user -p readonly_secure_2024 --authenticationDatabase healthcare_db --eval "
  use healthcare_db
  var count = db.patient_records.countDocuments({})
  print('✅ Lecture OK -', count, 'documents')
"

# Test d'écriture (devrait échouer pour readonly et healthcare)
docker exec -it healthcare_mongo mongosh -u readonly_user -p readonly_secure_2024 --authenticationDatabase healthcare_db --eval "
  use healthcare_db
  try {
    db.patient_records.insertOne({test: 'permission_check'})
    print('❌ ERREUR: Écriture autorisée!')
  } catch(e) {
    print('✅ Sécurité OK: Écriture bloquée')
  }
"
```

### Scénarios d'utilisation courants

#### **Scénario 1 : Migration des données**
```bash
# 1. Démarrer l'environnement
docker-compose -f docker/docker-compose.yml up -d

# 2. Attendre que les utilisateurs soient créés
sleep 30

# 3. Se connecter en tant que migration_user
docker exec -it healthcare_mongo mongosh -u migration_user -p migration_secure_2024 --authenticationDatabase healthcare_db

# 4. Effectuer la migration
use healthcare_db
// Les données CSV sont automatiquement migrées par le service Docker
```

#### **Scénario 2 : Analyse des données**
```bash
# 1. Se connecter en readonly
docker exec -it healthcare_mongo mongosh -u readonly_user -p readonly_secure_2024 --authenticationDatabase healthcare_db

# 2. Effectuer des analyses
use healthcare_db
db.patient_records.find({"age": {"$gte": 65}}).count()
db.patient_records.aggregate([
  {$group: {_id: "$medical_data.diagnosis", count: {$sum: 1}}},
  {$sort: {count: -1}},
  {$limit: 10}
])
```

#### **Scénario 3 : Application clinique**
```bash
# 1. Se connecter en healthcare
docker exec -it healthcare_mongo mongosh -u healthcare_user -p healthcare_secure_2024 --authenticationDatabase healthcare_db

# 2. Requêtes cliniques courantes
use healthcare_db
db.patient_records.find({"patient_info.age": {"$gte": 65}})
db.patient_records.find({"medical_data.diagnosis": {"$regex": "hypertension", "$options": "i"}})
```

### Sécurité et bonnes pratiques

#### **Mots de passe sécurisés**
- **Admin** : `secure_password` (à changer en production)
- **Migration** : `migration_secure_2024`
- **ReadOnly** : `readonly_secure_2024`
- **Healthcare** : `healthcare_secure_2024`

#### **Principe de moindre privilège**
- **Toujours utiliser l'utilisateur** avec les permissions minimales nécessaires
- **Admin** : Réservé à la configuration système
- **Migration** : Seulement pendant les opérations de migration
- **ReadOnly/Healthcare** : Pour les analyses et applications normales

#### **Audit et monitoring**
```bash
# Vérifier les connexions actives
docker exec -it healthcare_mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "
  db.serverStatus().connections
"

# Consulter les logs d'authentification
docker logs healthcare_mongo | grep -i auth
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

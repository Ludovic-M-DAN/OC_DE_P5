# Journal de Bord - Projet P5 OC Data Engineer

## Session 1 - Initialisation du projet (Date: 2025-07-15)

### Objectifs 
- Créer le repository GitHub pour le projet P5
- Initialiser la structure de base du projet
- Mettre en place la gestion des versions avec Git

### Actions réalisées

#### 1. Création du repository GitHub
- **Repository créé** : [OC_DE_P5](https://github.com/Ludovic-M-DAN/OC_DE_P5)
- **Description** : Projet P5 - Migration de données médicales vers MongoDB avec conteneurisation Docker
- **Visibilité** : Public

#### 2. Configuration Git locale
- **Remote ajouté** : `origin` pointant vers le repository GitHub
- **Branche principale** : `main`
- **Synchronisation** : Fetch réussi du contenu distant

#### 3. Premier commit - Structure de base
- **README.md** : Titre "OC_DE_P5" (structure minimale à enrichir)
- **.gitignore** : Exclusion des dossiers personnels et fichiers temporaires
- **Dataset CSV** : `data/healthcare_dataset.csv` (8.4 MB)
  - **Source** : Téléchargé depuis Kaggle
  - **Contenu** : Données médicales anonymisées pour la migration
  - **Taille** : Acceptable pour Git (<100MB recommandé)

#### 4. Installation MongoDB locale via Docker
- Docker Desktop installé et opérationnel
- Image: mongo:5.0
- Port exposé: 27017
- Volume persistant: mongodb_data monté sur /data/db
- Variables d'environnement: MONGO_INITDB_ROOT_USERNAME=admin, MONGO_INITDB_ROOT_PASSWORD=secure_password
- Conteneur: nom "mongo", politique de redémarrage "unless-stopped"

Vérifications effectuées
- docker ps: conteneur "mongo" en cours d'exécution
- docker logs --tail 20 mongo: démarrage sans erreurs bloquantes
- Shell: "use healthcare_db; db.stats();" → changement de contexte OK
- "db.adminCommand({ listDatabases: 1 })": admin, config, local uniquement → normal tant qu'aucune collection n'est créée
- Persistance: arrêt/redémarrage (docker stop/start mongo) → OK

#### 5. Dépendances Python minimales (requirements.txt)
- Création de `requirements.txt` au stade actuel du projet
- Contenu minimal: `pymongo==4.7.2`
- Raison: se limiter aux besoins immédiats de l’étape 1 (connexion MongoDB)

#### 6. Structure du projet (actuelle)
```
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
- `src/` est initialisé comme package Python.
- `tests/` reste vide pour l’instant.

#### 7. Script de migration CSV → MongoDB (minimal)
- Fichier: `src/migrate.py`
- Dépendances: PyMongo uniquement (requirements.txt)
- Lecture CSV: `csv.DictReader` (stdlib), traitement par lots
- Insertion: `insert_many(..., ordered=False)` dans `healthcare_db.patient_records`
- Paramètres: variables d'environnement optionnelles (hôte, port, user, password, db, collection, CSV_PATH)
- Sortie: logs de progression et résumé final (lignes lues, insérées, erreurs), code de sortie 0/1

#### 8. Environnement virtuel Python
- Création: `python -m venv venv`
- Activation: `venv\Scripts\activate` (Windows)
- Installation dépendances: `pip install --upgrade pip && pip install -r requirements.txt`
- Raison: isolation des dépendances du projet, éviter les conflits système

#### 9. Test de la migration CSV → MongoDB
- Commande: `python src/migrate.py`
- **Résultat**: Migration summary: rows_read=55500, inserted=55500, errors=0
- Statut: ✅ SUCCÈS - 100% des lignes du CSV migrées sans erreur
- Base cible: `healthcare_db.patient_records` (55 500 documents)

#### 10. Démonstration des opérations CRUD
- Fichier: `src/crud_demo.py`
- Commande: `python src/crud_demo.py`
- **CREATE**: 3 documents insérés (1 individuel + 2 en lot)
- **READ**: 55 503 documents comptés, recherches et filtres appliqués
- **UPDATE**: 3 documents modifiés (update_one + update_many)
- **DELETE**: 3 documents supprimés, nettoyage complet
- Statut: ✅ SUCCÈS - Toutes les opérations CRUD fonctionnelles

#### 11. Ajout de pandas pour les tests d'intégrité
- requirements.txt mis à jour : pymongo==4.7.2, pandas==2.2.2
- Objectif: analyser le CSV et comparer avec MongoDB pour validation des données

#### 12. Tests d'intégrité des données - SUCCÈS COMPLET
- Fichier: `tests/test_data_integrity.py`
- Commande: `python tests/test_data_integrity.py`
- **Résultats**: 100% de réussite (3/3 tests)
  - Test 1: Nombre d'enregistrements [PASS] - 55500 CSV = 55500 MongoDB
  - Test 2: Présence de données [PASS] - 55500 documents présents
  - Test 3: Structure des documents [PASS] - 15 colonnes = 15 champs
- **Validation**: Migration validée, intégrité des données préservée
- **Note**: 534 doublons détectés dans le CSV original (normal)

---

## ÉTAPE 2 - CONTENEURISATION AVEC DOCKER

### Session 2 - Docker et Compose

#### 13. Vérification environnement Docker 
- **Docker version**: 28.3.3 (build 980b856)
- **Docker Compose version**: v2.39.2-desktop.1
- **Test hello-world**: Exécution réussie
- **Statut**: ✅ Environnement Docker fonctionnel et prêt

#### 14. Organisation structure containerisation
- **Dossier créé**: `docker/` avec 3 fichiers
  - `Dockerfile` : Image custom pour service migration
  - `.dockerignore` : Exclusions pour le build Docker
  - `docker-compose.yml` : Orchestration des services
- **Architecture planifiée**: Service MongoDB + Service Migration + Réseau nommé
- **Statut**: ✅ Structure Docker organisée

#### 15. Création du Dockerfile - Correction erreur de contexte
- **Fichier**: `docker/Dockerfile` avec base Python 3.9-slim
- **Erreur détectée**: Contexte de build dans `./docker/` mais fichiers à la racine
- **Problème**: `COPY requirements.txt .` cherchait `docker/requirements.txt` (inexistant)
- **Solution finale**: Utilisation de `docker build -f docker/Dockerfile -t healthcare-migration .`
  - `-f docker/Dockerfile` : spécifie le Dockerfile
  - `.` : contexte de build à la racine (accès requirements.txt et src/)
  - Chemins standards dans le Dockerfile (sans `../`)

#### 16. Test du build Docker - SUCCÈS
- **Commande**: `docker build -f docker/Dockerfile -t healthcare-migration .`
- **Durée**: 29.1s (téléchargement Python 3.9-slim + installation dépendances)
- **Résultat**: Image `healthcare-migration` créée avec succès
- **Statut**: ✅ Build Docker fonctionnel

#### 17. Configuration .dockerignore - Optimisation majeure
- **Fichier**: `docker/.dockerignore` avec exclusions optimisées
- **Exclusions**: venv/, .git/, __pycache__/, dossiers personnels, documentation
- **Test d'optimisation**: Build re-exécuté après configuration
- **Résultat**: **29.1s → 1.3s** (amélioration de 95% !)
- **Cause**: Cache Docker + contexte minimal (162B vs plusieurs MB)
- **Statut**: ✅ Optimisation Docker réussie

#### 18. Création docker-compose.yml - Orchestration complète
- **Fichier**: `docker/docker-compose.yml` avec services MongoDB + Migration
- **Services**: 
  - `mongo`: Image officielle 5.0, port 27017, auth admin/secure_password
  - `migration`: Build depuis Dockerfile, depends_on mongo (healthy), variables env
- **Infrastructure**: Volume persistant mongodb_data, réseau healthcare_net
- **Health check**: MongoDB ping pour synchronisation des services

#### 19. Test orchestration - Erreur de contexte résolue
- **Problème initial**: `CSV file not found: data/healthcare_dataset.csv`
- **Cause**: Lancement depuis `docker/` → chemins relatifs incorrects
- **Solution**: Lancement depuis racine avec `docker-compose -f docker/docker-compose.yml`
- **Commande corrigée**: `docker-compose -f docker/docker-compose.yml up -d`
- **Résultat**: ✅ Services démarrés, MongoDB healthy, migration OK
- **Statut**: ✅ Orchestration Docker fonctionnelle

#### 20. Conversion en vrais tests pytest - Framework créé
- **Nouveaux fichiers**: 
  - `tests/test_migration_integrity.py` (13 tests automatisés)
  - `tests/conftest.py` (configuration pytest)
  - `pytest.ini` (configuration globale)
- **Dependencies**: pytest==8.2.2, pytest-html==4.1.1 ajoutées à requirements.txt
- **Installation**: `pip install pytest pytest-html` → OK
- **Statut**: ✅ Framework pytest opérationnel

#### 21. Premier test pytest - Erreurs détectées à corriger
- **Commande**: `pytest tests/test_migration_integrity.py -v`
- **Résultats**: 5 passed, 8 failed (38% réussite)
- **Problèmes identifiés**:
  1. **Colonnes CSV**: 'Diagnosis' manquante → vérifier noms exacts
  2. **MongoDB vide**: 0 documents → migration pas lancée récemment
  3. **pytest.warns**: Syntaxe incorrecte pour warnings
- **Action**: Corriger les tests selon la structure réelle des données
- **Statut**: 🔄 Tests à ajuster selon données réelles 

### Configuration technique
- **Git** : Repository local configuré avec remote GitHub
- **Structure** : Dossiers exclus via .gitignore pour maintenir la propreté du repo
- **Premier push** : ok

### Notes importantes
- Le CSV est commité car c'est le dataset officiel du projet P5
- Le .gitignore exclut les ressources pédagogiques et dossiers personnels
- Structure prête pour le développement des scripts de migration

### Prochaines étapes
- [ ] Analyser le contenu du CSV pour comprendre la structure des données
- [ ] Concevoir le schéma MongoDB pour les données médicales
- [ ] Créer les scripts de migration Python
- [ ] Mettre en place l'environnement Docker

---

## Lexique & Annexes

### Commandes utilisées (avec description)
- `docker version`: vérifier l’installation et la version de Docker.
- `docker pull mongo:5.0`: télécharger l’image officielle MongoDB 5.0.
- `docker volume create mongodb_data`: créer un volume persistant pour les données MongoDB.
- `docker run -d --name mongo -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secure_password -v mongodb_data:/data/db --restart unless-stopped mongo:5.0`: lancer MongoDB en conteneur (port 27017, volume, identifiants root).
- `docker ps`: lister les conteneurs en cours d’exécution.
- `docker logs --tail 20 mongo`: afficher les derniers logs du conteneur `mongo`.
- `docker exec -it mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.adminCommand({ ping: 1 })"`: tester la réponse du serveur MongoDB.
- `docker stop mongo` / `docker start mongo`: arrêter/redémarrer le conteneur tout en conservant les données (volume).
- `docker exec -it mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.adminCommand({ listDatabases: 1 })"`: lister les bases de données disponibles.

### Termes techniques (définitions courtes)
- Image Docker: modèle d’exécution immuable à partir duquel on crée des conteneurs.
- Conteneur: instance d’une image qui exécute un processus isolé.
- Volume Docker: stockage persistant monté dans un conteneur pour conserver les données.
- Mapping de port (`-p hôte:conteneur`): expose un port du conteneur sur la machine hôte.
- Identifiants root MongoDB: utilisateur/mot de passe administrateur créés au démarrage du conteneur.
- BSON: format binaire de stockage de MongoDB, proche de JSON.

---

## **2025-09-04 - Conversion vers pytest et résolution des erreurs**

### **Étape : Conversion du script de test en framework pytest**

**Objectif :** Transformer le script `test_data_integrity.py` en vrais tests pytest automatisés.

**Actions réalisées :**
1. **Création du framework pytest :**
   - `tests/test_migration_integrity.py` : 13 tests automatisés
   - `tests/conftest.py` : fixtures partagées (csv_data, mongo_client)
   - `pytest.ini` : configuration globale
   - Mise à jour `requirements.txt` : ajout de `pytest==8.2.2` et `pytest-html==4.1.1`

2. **Premier lancement des tests :**
   - **Résultat :** 8 échecs / 13 tests
   - **Tests réussis :** CSV file exists, CSV not empty, CSV age values, MongoDB connection, MongoDB data types
   - **Tests échoués :** MongoDB collection exists, data count, document structure, migration completeness, query performance, indexes

### **Diagnostic des erreurs identifiées :**

**Erreur 1 : Nom de colonne incorrect**
- **Problème :** Test cherchait 'Diagnosis' mais la vraie colonne est 'Medical Condition'
- **Solution :** Correction dans `test_migration_integrity.py` ligne 41 et 99
- **Commande de vérification :** `python -c "import pandas as pd; df = pd.read_csv('data/healthcare_dataset.csv'); print(df.columns.tolist())"`

**Erreur 2 : Syntaxe pytest.warns incorrecte**
- **Problème :** `pytest.warns(UserWarning, f"Doublons détectés: {duplicate_count}")` - TypeError
- **Solution :** Remplacement par `warnings.warn(f"Doublons détectés: {duplicate_count}", UserWarning)`

**Erreur 3 : MongoDB vide (problème principal)**
- **Symptôme :** "Collection patient_records non trouvée", "Aucun document trouvé"
- **Cause identifiée :** Le conteneur de migration ne trouve pas le fichier CSV
- **Logs d'erreur :** `"CSV file not found: data/healthcare_dataset.csv"`

### **Résolution du problème de montage Docker :**

**Diagnostic approfondi :**
- **Commande :** `docker-compose -f docker/docker-compose.yml logs migration`
- **Résultat :** Erreur répétée "CSV file not found: data/healthcare_dataset.csv"
- **État des conteneurs :** Seul `healthcare_mongo` était UP, `healthcare_migration` avait terminé

**Problème identifié :**
- **Configuration docker-compose.yml :** Volume monté `../data:/data:ro`
- **Script migrate.py :** Cherchait `data/healthcare_dataset.csv` (chemin relatif)
- **Dans le conteneur :** Le fichier est à `/data/healthcare_dataset.csv` (chemin absolu)

**Solution implémentée :**
- **Modification de `src/migrate.py` ligne 114-116 :**
  ```python
  # Chemin CSV : local "data/..." ou Docker "/data/..."
  default_csv = "/data/healthcare_dataset.csv" if get_env("MONGO_HOST") == "mongo" else "data/healthcare_dataset.csv"
  csv_path = argv[1] if len(argv) > 1 else get_env("CSV_PATH", default_csv)
  ```
- **Logique :** Détection automatique de l'environnement (local vs Docker) via la variable `MONGO_HOST`

**Prochaine étape :** Relancer la migration avec `docker-compose -f docker/docker-compose.yml up --build migration`

### **Amélioration des résultats :**
- **Avant correction :** 8 échecs / 13 tests
- **Après correction CSV :** 6 échecs / 13 tests (amélioration de 2 tests)
- **Tests CSV :** Tous réussis ✅
- **Tests MongoDB :** En attente de la migration corrigée

### **Erreur lors du relancement de la migration :**

**Problème identifié :**
- **Erreur :** `TypeError: get_env() missing 1 required positional argument: 'default'`
- **Cause :** Appel de `get_env("MONGO_HOST")` sans argument `default` obligatoire
- **Ligne problématique :** `default_csv = "/data/healthcare_dataset.csv" if get_env("MONGO_HOST") == "mongo" else "data/healthcare_dataset.csv"`

**Solution appliquée :**
- **Correction :** `get_env("MONGO_HOST", "localhost")` avec valeur par défaut
- **Logique :** 
  - Dans Docker : `MONGO_HOST=mongo` → chemin `/data/healthcare_dataset.csv`
  - En local : `MONGO_HOST` non défini → `"localhost"` par défaut → chemin `data/healthcare_dataset.csv`

**Prochaine étape :** Relancer la migration avec la correction appliquée

### **SUCCÈS DE LA MIGRATION DOCKER :**

**Résultat final :**
- ✅ **Migration réussie :** 55 500 lignes lues et insérées
- ✅ **0 erreur** lors de l'insertion
- ✅ **Code de sortie 0** (succès complet)
- ✅ **Chemin CSV corrigé :** `/data/healthcare_dataset.csv` trouvé dans le conteneur
- ✅ **Connexion MongoDB :** Établie avec succès vers le service `mongo`

**Logs de migration :**
```
healthcare_migration  | 2025-09-04 14:31:20,262 - INFO - Starting CSV → MongoDB migration
healthcare_migration  | 2025-09-04 14:31:20,262 - INFO - CSV file: /data/healthcare_dataset.csv
healthcare_migration  | 2025-09-04 14:31:20,262 - INFO - Batch size: 1000
healthcare_migration  | [... traitement par lots de 1000 documents ...]
healthcare_migration  | 2025-09-04 14:31:23,503 - INFO - Migration summary: rows_read=55500, inserted=55500, errors=0
healthcare_migration exited with code 0
```

**Prochaine étape :** Vérifier que tous les tests pytest passent maintenant que MongoDB contient les données

### **SUCCÈS COMPLET DES TESTS PYTEST :**

**Résultat final des tests :**
- ✅ **13 tests PASSED** (100% de réussite)
- ✅ **0 échec**
- ⚠️ **1 warning** (informatif sur 534 doublons détectés dans le CSV - normal)

**Tests réussis :**
1. ✅ CSV file exists
2. ✅ CSV not empty  
3. ✅ CSV required columns
4. ✅ CSV data quality
5. ✅ CSV age values
6. ✅ MongoDB connection
7. ✅ MongoDB collection exists
8. ✅ MongoDB data count
9. ✅ MongoDB document structure
10. ✅ MongoDB data types
11. ✅ Migration completeness
12. ✅ Query response time
13. ✅ Indexes recommended

**Problèmes résolus :**
- ✅ Nom de colonne 'Diagnosis' → 'Medical Condition'
- ✅ Syntaxe pytest.warns corrigée
- ✅ Chemin CSV Docker : `/data/healthcare_dataset.csv`
- ✅ Migration Docker : 55 500 documents insérés avec succès
- ✅ Tous les tests MongoDB passent maintenant

**Étape 1 et 2 du projet : COMPLÈTES ✅**

### **Explication du warning sur les doublons :**

**Warning observé :** `UserWarning: Doublons détectés: 534`

**Pourquoi c'est normal et attendu :**
- **534 doublons sur 55 500 lignes** = **0.96%** (taux très faible et acceptable)
- **Dataset réaliste** : Les données médicales peuvent avoir des doublons légitimes :
  - Même patient avec plusieurs consultations
  - Même diagnostic pour différents patients  
  - Données de test générées automatiquement
- **Comportement du test** : Le warning est informatif seulement, pas bloquant
- **Code responsable** : `warnings.warn(f"Doublons détectés: {duplicate_count}", UserWarning)` dans `test_csv_data_quality()`

**Conclusion :** Ce warning est normal pour un dataset de santé publique et n'indique aucun problème avec la migration ou les tests.



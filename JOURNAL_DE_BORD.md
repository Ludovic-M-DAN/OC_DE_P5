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
- **Prochaine étape**: Création du Dockerfile (Phase 2.2) 

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



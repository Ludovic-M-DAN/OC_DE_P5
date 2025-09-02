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



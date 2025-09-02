# Journal de Bord - Projet P5 OC Data Engineer

## 📅 Session 1 - Initialisation du projet (Date: 2025-01-XX)

### 🎯 Objectifs de la session
- Créer le repository GitHub pour le projet P5
- Initialiser la structure de base du projet
- Mettre en place la gestion des versions avec Git

### ✅ Actions réalisées

#### 1. Création du repository GitHub
- **Repository créé** : [OC_DE_P5](https://github.com/Ludovic-M-DAN/OC_DE_P5)
- **Description** : Projet P5 - Migration de données médicales vers MongoDB avec conteneurisation Docker
- **Visibilité** : Public (conformément aux exigences OC)

#### 2. Configuration Git locale
- **Remote ajouté** : `origin` pointant vers le repository GitHub
- **Branche principale** : `main`
- **Synchronisation** : Fetch réussi du contenu distant

#### 3. Premier commit - Structure de base
- **README.md** : Titre "OC_DE_P5" (structure minimale à enrichir)
- **.gitignore** : Exclusion des dossiers personnels et fichiers temporaires
  - Dossiers exclus : `attendus_du_projet/`, `cours_openclassroom_&_sources_externes/`, `.cursor/`
  - Fichiers exclus : `*.txt`, `__pycache__/`, `*.pyc`, logs, etc.
- **Dataset CSV** : `data/healthcare_dataset.csv` (8.4 MB)
  - **Source** : Téléchargé depuis Kaggle
  - **Contenu** : Données médicales anonymisées pour la migration
  - **Taille** : Acceptable pour Git (<100MB recommandé)

### 🔧 Configuration technique
- **Git** : Repository local configuré avec remote GitHub
- **Structure** : Dossiers exclus via .gitignore pour maintenir la propreté du repo
- **Premier push** : Synchronisation réussie avec `--force-with-lease` (histoires non liées)

### 📝 Notes importantes
- Le CSV est commité car c'est le dataset officiel du projet P5
- Le .gitignore exclut les ressources pédagogiques et dossiers personnels
- Structure prête pour le développement des scripts de migration

### 🎯 Prochaines étapes
- [ ] Analyser le contenu du CSV pour comprendre la structure des données
- [ ] Concevoir le schéma MongoDB pour les données médicales
- [ ] Créer les scripts de migration Python
- [ ] Mettre en place l'environnement Docker

---

*Ce journal de bord sera mis à jour à chaque session de travail pour tracer l'évolution du projet et documenter les décisions prises.*

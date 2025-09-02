# OC_DE_P5

## Prérequis
- Docker Desktop (Windows/macOS) ou Docker CE (Linux)
- Git

## Données
- Dataset: `data/healthcare_dataset.csv` (fourni dans le dépôt)

## Démarrage MongoDB (local, développement)
Lancer une instance MongoDB locale avec Docker:

```bash
docker volume create mongodb_data

docker run -d --name mongo -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secure_password \
  -v mongodb_data:/data/db \
  --restart unless-stopped \
  mongo:5.0
```

Vérifier l’accessibilité:

```bash
docker exec -it mongo mongosh -u admin -p secure_password --authenticationDatabase admin --eval "db.adminCommand({ ping: 1 })"
```

## Portée du dépôt
- Exclusions: `attendus_du_projet/`, `cours_openclassroom_&_sources_externes/`
- Seules les sources du projet et le dataset sont versionnés

## Prochaines étapes
- Ajouter `requirements.txt` (pymongo, pandas, python-dotenv, pytest)
- Implémenter le script de migration CSV → MongoDB
- Ajouter tests d’intégrité pré/post migration

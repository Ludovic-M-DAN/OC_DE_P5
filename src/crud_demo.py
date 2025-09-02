"""
Script de démonstration des opérations CRUD MongoDB.

Objectif: démontrer Create, Read, Update, Delete sur les données migrées.
Utilisation: python src/crud_demo.py
"""

import logging
import os
import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def setup_logging() -> None:
    """Configurer un logging simple pour voir les opérations CRUD."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_env(name: str, default: str) -> str:
    """Lire une variable d'environnement avec une valeur par défaut."""
    value = os.getenv(name)
    return value if value not in (None, "") else default


def get_mongo_client() -> MongoClient:
    """Créer un client MongoDB (mêmes paramètres que migrate.py)."""
    host = get_env("MONGO_HOST", "localhost")
    port = get_env("MONGO_PORT", "27017")
    user = get_env("MONGO_USER", "admin")
    password = get_env("MONGO_PASSWORD", "secure_password")
    auth_db = get_env("MONGO_AUTH_DB", "admin")

    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource={auth_db}"
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def demo_create(collection):
    """Démonstration CREATE : insérer de nouveaux documents."""
    logging.info("=== DÉMONSTRATION CREATE ===")
    
    # Insérer un document simple
    new_patient = {
        "patient_id": "P999999",
        "age": "42",
        "gender": "M",
        "diagnosis": "Démonstration CRUD",
        "date_recorded": "2024-01-15"
    }
    
    result = collection.insert_one(new_patient)
    logging.info("Document inséré avec l'ID: %s", result.inserted_id)
    
    # Insérer plusieurs documents
    new_patients = [
        {
            "patient_id": "P999998",
            "age": "35",
            "gender": "F", 
            "diagnosis": "Test batch insert",
            "date_recorded": "2024-01-16"
        },
        {
            "patient_id": "P999997",
            "age": "28",
            "gender": "M",
            "diagnosis": "Autre test",
            "date_recorded": "2024-01-17"
        }
    ]
    
    result = collection.insert_many(new_patients)
    logging.info("Documents batch insérés, IDs: %s", len(result.inserted_ids))


def demo_read(collection):
    """Démonstration READ : lire et filtrer des documents."""
    logging.info("=== DÉMONSTRATION READ ===")
    
    # Compter tous les documents
    total_count = collection.count_documents({})
    logging.info("Nombre total de documents: %s", total_count)
    
    # Lire un document spécifique
    patient = collection.find_one({"patient_id": "P999999"})
    if patient:
        logging.info("Patient trouvé: %s, âge: %s, diagnostic: %s", 
                    patient["patient_id"], patient["age"], patient["diagnosis"])
    
    # Lire plusieurs documents avec filtre
    young_patients = list(collection.find({"age": {"$lt": "30"}}).limit(3))
    logging.info("Exemples de patients jeunes (âge < 30): %s documents trouvés", len(young_patients))
    for p in young_patients:
        logging.info("  - Patient %s: âge %s, diagnostic: %s", 
                    p.get("patient_id", "N/A"), p.get("age", "N/A"), p.get("diagnosis", "N/A"))
    
    # Projection (ne récupérer que certains champs)
    patients_summary = list(collection.find(
        {"diagnosis": {"$regex": "Diabetes", "$options": "i"}}, 
        {"patient_id": 1, "age": 1, "diagnosis": 1, "_id": 0}
    ).limit(2))
    logging.info("Patients diabétiques (projection): %s documents", len(patients_summary))
    for p in patients_summary:
        logging.info("  - %s", p)


def demo_update(collection):
    """Démonstration UPDATE : modifier des documents existants."""
    logging.info("=== DÉMONSTRATION UPDATE ===")
    
    # Mettre à jour un document
    result = collection.update_one(
        {"patient_id": "P999999"},
        {"$set": {"diagnosis": "Diagnostic mis à jour", "last_modified": "2024-01-20"}}
    )
    logging.info("Documents modifiés (update_one): %s", result.modified_count)
    
    # Vérifier la modification
    updated_patient = collection.find_one({"patient_id": "P999999"})
    if updated_patient:
        logging.info("Après modification: diagnostic = %s", updated_patient["diagnosis"])
    
    # Mettre à jour plusieurs documents
    result = collection.update_many(
        {"patient_id": {"$in": ["P999998", "P999997"]}},
        {"$set": {"status": "Traité", "last_modified": "2024-01-20"}}
    )
    logging.info("Documents modifiés (update_many): %s", result.modified_count)


def demo_delete(collection):
    """Démonstration DELETE : supprimer des documents."""
    logging.info("=== DÉMONSTRATION DELETE ===")
    
    # Compter avant suppression
    count_before = collection.count_documents({"patient_id": {"$regex": "^P99999"}})
    logging.info("Documents de test avant suppression: %s", count_before)
    
    # Supprimer un document
    result = collection.delete_one({"patient_id": "P999999"})
    logging.info("Documents supprimés (delete_one): %s", result.deleted_count)
    
    # Supprimer plusieurs documents
    result = collection.delete_many({"patient_id": {"$in": ["P999998", "P999997"]}})
    logging.info("Documents supprimés (delete_many): %s", result.deleted_count)
    
    # Vérifier après suppression
    count_after = collection.count_documents({"patient_id": {"$regex": "^P99999"}})
    logging.info("Documents de test après suppression: %s", count_after)


def main() -> int:
    """Point d'entrée du script de démonstration CRUD."""
    setup_logging()
    
    logging.info("Démarrage de la démonstration CRUD MongoDB")
    
    # Connexion
    try:
        client = get_mongo_client()
        client.admin.command({"ping": 1})
        logging.info("Connexion MongoDB établie")
    except PyMongoError as e:
        logging.error("Erreur de connexion MongoDB: %s", e)
        return 1
    
    # Collection cible (même que migrate.py)
    db_name = get_env("MONGO_DB", "healthcare_db")
    coll_name = get_env("MONGO_COLLECTION", "patient_records")
    collection = client[db_name][coll_name]
    
    try:
        # Démonstrations dans l'ordre CRUD
        demo_create(collection)
        demo_read(collection)
        demo_update(collection)
        demo_delete(collection)
        
        logging.info("Démonstration CRUD terminée avec succès")
        
    except PyMongoError as e:
        logging.error("Erreur durant les opérations CRUD: %s", e)
        return 1
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

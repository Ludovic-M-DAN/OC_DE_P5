#!/usr/bin/env python3
"""
Script de configuration des rôles et utilisateurs MongoDB pour OC P5.

Ce script configure un système d'authentification approprié pour les données médicales :
- Utilisateur admin (existante via Docker)
- Utilisateur migration (permissions d'écriture pour la migration)
- Utilisateur readonly (permissions de lecture pour les analyses)
- Utilisateur healthcare (accès limité aux données patient)

Utilisation :
    python src/setup_auth.py

Variables d'environnement :
    MONGO_HOST : hôte MongoDB (défaut: localhost)
    MONGO_PORT : port MongoDB (défaut: 27017)
    MONGO_USER : utilisateur admin (défaut: admin)
    MONGO_PASSWORD : mot de passe admin (défaut: secure_password)
"""

import logging
import os
import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError, OperationFailure


def setup_logging() -> None:
    """Configurer le logging pour le script d'authentification."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_env(name: str, default: str) -> str:
    """Lire une variable d'environnement avec valeur par défaut."""
    value = os.getenv(name)
    return value if value not in (None, "") else default


def get_admin_client() -> MongoClient:
    """Créer un client MongoDB avec les credentials admin."""
    host = get_env("MONGO_HOST", "localhost")
    port = get_env("MONGO_PORT", "27017")
    user = get_env("MONGO_USER", "admin")
    password = get_env("MONGO_PASSWORD", "secure_password")

    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def create_migration_user(client: MongoClient) -> bool:
    """
    Créer l'utilisateur 'migration' avec permissions d'écriture.

    Permissions :
    - Lecture/écriture sur healthcare_db.patient_records
    - Permissions de lecture sur healthcare_db (pour les métadonnées)
    """
    try:
        db = client["healthcare_db"]

        # Créer l'utilisateur avec mot de passe sécurisé
        db.command("createUser", "migration_user",
                  pwd="migration_secure_2024",
                  roles=[
                      {"role": "readWrite", "db": "healthcare_db"},
                      {"role": "read", "db": "healthcare_db"}
                  ])
        logging.info("✅ Utilisateur 'migration_user' créé avec succès")
        logging.info("   Rôles: readWrite sur healthcare_db")
        return True

    except OperationFailure as e:
        if "already exists" in str(e):
            logging.warning("⚠️  Utilisateur 'migration_user' existe déjà")
            return True
        else:
            logging.error("❌ Erreur création utilisateur migration: %s", e)
            return False
    except PyMongoError as e:
        logging.error("❌ Erreur MongoDB création migration user: %s", e)
        return False


def create_readonly_user(client: MongoClient) -> bool:
    """
    Créer l'utilisateur 'readonly' avec permissions de lecture uniquement.

    Permissions :
    - Lecture seule sur healthcare_db
    - Idéal pour les analyses et rapports
    """
    try:
        db = client["healthcare_db"]

        db.command("createUser", "readonly_user",
                  pwd="readonly_secure_2024",
                  roles=[{"role": "read", "db": "healthcare_db"}])
        logging.info("✅ Utilisateur 'readonly_user' créé avec succès")
        logging.info("   Rôles: read sur healthcare_db")
        return True

    except OperationFailure as e:
        if "already exists" in str(e):
            logging.warning("⚠️  Utilisateur 'readonly_user' existe déjà")
            return True
        else:
            logging.error("❌ Erreur création utilisateur readonly: %s", e)
            return False
    except PyMongoError as e:
        logging.error("❌ Erreur MongoDB création readonly user: %s", e)
        return False


def create_healthcare_user(client: MongoClient) -> bool:
    """
    Créer l'utilisateur 'healthcare' avec permissions limitées.

    Permissions :
    - Lecture seule sur les données patient (pas les métadonnées sensibles)
    - Idéal pour les applications de soins
    """
    try:
        db = client["healthcare_db"]

        db.command("createUser", "healthcare_user",
                  pwd="healthcare_secure_2024",
                  roles=[{"role": "read", "db": "healthcare_db"}])
        logging.info("✅ Utilisateur 'healthcare_user' créé avec succès")
        logging.info("   Rôles: read sur healthcare_db (usage clinique limité)")
        return True

    except OperationFailure as e:
        if "already exists" in str(e):
            logging.warning("⚠️  Utilisateur 'healthcare_user' existe déjà")
            return True
        else:
            logging.error("❌ Erreur création utilisateur healthcare: %s", e)
            return False
    except PyMongoError as e:
        logging.error("❌ Erreur MongoDB création healthcare user: %s", e)
        return False


def list_users(client: MongoClient) -> None:
    """Lister tous les utilisateurs créés dans healthcare_db."""
    try:
        db = client["healthcare_db"]
        users = db.command("usersInfo")

        logging.info("=== UTILISATEURS CONFIGURÉS ===")
        for user_info in users.get("users", []):
            user = user_info.get("user", "N/A")
            roles = user_info.get("roles", [])
            logging.info("👤 Utilisateur: %s", user)
            logging.info("   Rôles: %s", [role.get("role", "N/A") for role in roles])
            logging.info("")

    except PyMongoError as e:
        logging.error("❌ Erreur lors de la liste des utilisateurs: %s", e)


def test_user_permissions(client: MongoClient) -> None:
    """Tester les permissions de chaque utilisateur créé."""
    logging.info("=== TEST DES PERMISSIONS UTILISATEUR ===")

    # Tester readonly_user
    try:
        readonly_client = MongoClient(
            f"mongodb://readonly_user:readonly_secure_2024@{get_env('MONGO_HOST', 'localhost')}:{get_env('MONGO_PORT', '27017')}/healthcare_db",
            serverSelectionTimeoutMS=5000
        )
        db = readonly_client["healthcare_db"]

        # Test lecture
        count = db.patient_records.count_documents({})
        logging.info("✅ readonly_user: Lecture OK (%d documents)", count)

        # Test écriture (devrait échouer)
        try:
            db.patient_records.insert_one({"test": "should_fail"})
            logging.error("❌ readonly_user: Écriture autorisée (PROBLÈME!)")
        except OperationFailure:
            logging.info("✅ readonly_user: Écriture bloquée (correct)")

        readonly_client.close()

    except PyMongoError as e:
        logging.error("❌ Erreur test readonly_user: %s", e)

    # Tester migration_user
    try:
        migration_client = MongoClient(
            f"mongodb://migration_user:migration_secure_2024@{get_env('MONGO_HOST', 'localhost')}:{get_env('MONGO_PORT', '27017')}/healthcare_db",
            serverSelectionTimeoutMS=5000
        )
        db = migration_client["healthcare_db"]

        # Test lecture
        count = db.patient_records.count_documents({})
        logging.info("✅ migration_user: Lecture OK (%d documents)", count)

        # Test écriture (devrait réussir)
        result = db.test_permissions.insert_one({"test": "migration_write_test"})
        logging.info("✅ migration_user: Écriture OK (ID: %s)", result.inserted_id)

        # Nettoyer
        db.test_permissions.delete_one({"_id": result.inserted_id})

        migration_client.close()

    except PyMongoError as e:
        logging.error("❌ Erreur test migration_user: %s", e)


def main() -> int:
    """Point d'entrée du script de configuration d'authentification."""
    setup_logging()

    logging.info("🚀 Configuration de l'authentification MongoDB pour OC P5")
    logging.info("=" * 60)

    # Connexion admin
    try:
        client = get_admin_client()
        client.admin.command({"ping": 1})
        logging.info("✅ Connexion admin réussie")
    except PyMongoError as e:
        logging.error("❌ Échec connexion admin: %s", e)
        logging.error("Vérifiez MONGO_HOST, MONGO_USER, MONGO_PASSWORD")
        return 1

    success_count = 0

    # Créer les utilisateurs
    if create_migration_user(client):
        success_count += 1

    if create_readonly_user(client):
        success_count += 1

    if create_healthcare_user(client):
        success_count += 1

    # Lister les utilisateurs
    if success_count > 0:
        list_users(client)

        # Tester les permissions
        test_user_permissions(client)

    client.close()

    logging.info("=" * 60)
    if success_count == 3:
        logging.info("🎉 Configuration d'authentification terminée avec succès!")
        logging.info("📋 Récapitulatif des utilisateurs créés:")
        logging.info("   • migration_user : readWrite sur healthcare_db")
        logging.info("   • readonly_user : read sur healthcare_db")
        logging.info("   • healthcare_user : read sur healthcare_db")
        return 0
    else:
        logging.error("❌ Configuration incomplète: %d/3 utilisateurs créés", success_count)
        return 1


if __name__ == "__main__":
    sys.exit(main())

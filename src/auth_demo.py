#!/usr/bin/env python3
"""
Démonstration des différents niveaux d'accès utilisateurs MongoDB pour OC P5.

Ce script montre comment les différents utilisateurs créés par setup_auth.py
peuvent accéder aux données avec leurs permissions respectives :

- admin : accès complet (via Docker env vars)
- migration_user : lecture/écriture pour migration
- readonly_user : lecture seule pour analyses
- healthcare_user : accès limité pour applications cliniques

Utilisation :
    python src/auth_demo.py

Prérequis :
    - MongoDB en cours d'exécution
    - Utilisateurs créés via python src/setup_auth.py
    - Données migrées via python src/migrate.py
"""

import logging
import os
import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError, OperationFailure


def setup_logging() -> None:
    """Configurer le logging pour la démonstration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_env(name: str, default: str) -> str:
    """Lire une variable d'environnement."""
    value = os.getenv(name)
    return value if value not in (None, "") else default


def create_user_client(username: str, password: str) -> MongoClient:
    """Créer un client MongoDB pour un utilisateur spécifique."""
    host = get_env("MONGO_HOST", "localhost")
    port = get_env("MONGO_PORT", "27017")

    uri = f"mongodb://{username}:{password}@{host}:{port}/healthcare_db"
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def demo_admin_access() -> None:
    """Démonstration de l'accès admin (utilise les variables d'environnement Docker)."""
    logging.info("🔐 DÉMONSTRATION - ACCÈS ADMIN")
    logging.info("-" * 50)

    try:
        # Utilise les credentials Docker (admin)
        host = get_env("MONGO_HOST", "localhost")
        port = get_env("MONGO_PORT", "27017")
        user = get_env("MONGO_USER", "admin")
        password = get_env("MONGO_PASSWORD", "secure_password")

        client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin")
        db = client["healthcare_db"]
        collection = db["patient_records"]

        # Test complet des permissions
        count = collection.count_documents({})
        logging.info("✅ ADMIN - Lecture: %d documents trouvés", count)

        # Insertion de test
        test_doc = {"patient_id": "ADMIN_TEST", "test_type": "admin_access", "timestamp": "2024-01-01"}
        result = collection.insert_one(test_doc)
        logging.info("✅ ADMIN - Écriture: Document inséré (ID: %s)", result.inserted_id)

        # Suppression du document de test
        collection.delete_one({"_id": result.inserted_id})
        logging.info("✅ ADMIN - Suppression: Document de test supprimé")

        # Lister les utilisateurs (admin seulement)
        try:
            users = db.command("usersInfo")
            user_count = len(users.get("users", []))
            logging.info("✅ ADMIN - Gestion utilisateurs: %d utilisateurs trouvés", user_count)
        except OperationFailure:
            logging.warning("⚠️  ADMIN - Gestion utilisateurs: Non autorisé sur cette DB")

        client.close()
        logging.info("✅ ADMIN - Toutes les opérations réussies\n")

    except PyMongoError as e:
        logging.error("❌ ADMIN - Erreur: %s\n", e)


def demo_migration_access() -> None:
    """Démonstration de l'accès migration_user (readWrite)."""
    logging.info("🔄 DÉMONSTRATION - ACCÈS MIGRATION")
    logging.info("-" * 50)

    try:
        client = create_user_client("migration_user", "migration_secure_2024")
        db = client["healthcare_db"]
        collection = db["patient_records"]

        # Test lecture
        count = collection.count_documents({})
        logging.info("✅ MIGRATION - Lecture: %d documents trouvés", count)

        # Test écriture (devrait réussir)
        test_doc = {
            "patient_id": "MIGRATION_TEST",
            "age": "99",
            "diagnosis": "Test migration",
            "date_recorded": "2024-01-01"
        }
        result = collection.insert_one(test_doc)
        logging.info("✅ MIGRATION - Écriture: Document inséré (ID: %s)", result.inserted_id)

        # Vérifier l'insertion
        inserted = collection.find_one({"_id": result.inserted_id})
        if inserted:
            logging.info("✅ MIGRATION - Vérification: Document retrouvé avec succès")

        # Nettoyer
        collection.delete_one({"_id": result.inserted_id})
        logging.info("✅ MIGRATION - Nettoyage: Document de test supprimé")

        client.close()
        logging.info("✅ MIGRATION - Opérations readWrite réussies\n")

    except PyMongoError as e:
        logging.error("❌ MIGRATION - Erreur: %s\n", e)


def demo_readonly_access() -> None:
    """Démonstration de l'accès readonly_user (read only)."""
    logging.info("📖 DÉMONSTRATION - ACCÈS READONLY")
    logging.info("-" * 50)

    try:
        client = create_user_client("readonly_user", "readonly_secure_2024")
        db = client["healthcare_db"]
        collection = db["patient_records"]

        # Test lecture (devrait réussir)
        count = collection.count_documents({})
        logging.info("✅ READONLY - Lecture: %d documents trouvés", count)

        # Test requête avec filtre
        sample_docs = list(collection.find().limit(3))
        logging.info("✅ READONLY - Requêtes: %d échantillons récupérés", len(sample_docs))

        # Test statistiques
        stats = db.command("dbStats")
        logging.info("✅ READONLY - Stats DB: %s collections", stats.get("collections", "N/A"))

        # Test écriture (devrait échouer)
        try:
            test_doc = {"patient_id": "READONLY_TEST", "test_type": "should_fail"}
            collection.insert_one(test_doc)
            logging.error("❌ READONLY - SÉCURITÉ: Écriture autorisée (PROBLÈME!)")
        except OperationFailure:
            logging.info("✅ READONLY - Sécurité: Écriture bloquée (correct)")

        # Test suppression (devrait échouer)
        try:
            collection.delete_one({"patient_id": "NONEXISTANT"})
            logging.error("❌ READONLY - SÉCURITÉ: Suppression autorisée (PROBLÈME!)")
        except OperationFailure:
            logging.info("✅ READONLY - Sécurité: Suppression bloquée (correct)")

        client.close()
        logging.info("✅ READONLY - Accès en lecture seule validé\n")

    except PyMongoError as e:
        logging.error("❌ READONLY - Erreur: %s\n", e)


def demo_healthcare_access() -> None:
    """Démonstration de l'accès healthcare_user (read limité)."""
    logging.info("🏥 DÉMONSTRATION - ACCÈS HEALTHCARE")
    logging.info("-" * 50)

    try:
        client = create_user_client("healthcare_user", "healthcare_secure_2024")
        db = client["healthcare_db"]
        collection = db["patient_records"]

        # Test lecture basique
        count = collection.count_documents({})
        logging.info("✅ HEALTHCARE - Lecture: %d documents accessibles", count)

        # Test requêtes cliniques typiques
        # Patients d'un certain âge
        age_query = {"age": {"$gte": "65"}}
        elderly_count = collection.count_documents(age_query)
        logging.info("✅ HEALTHCARE - Requête âge: %d patients ≥65 ans", elderly_count)

        # Recherche par diagnostic
        diabetes_query = {"diagnosis": {"$regex": "diabetes", "$options": "i"}}
        diabetes_count = collection.count_documents(diabetes_query)
        logging.info("✅ HEALTHCARE - Requête diagnostic: %d cas de diabète", diabetes_count)

        # Test écriture (devrait échouer)
        try:
            test_doc = {"patient_id": "HEALTHCARE_TEST", "test_type": "clinical_access"}
            collection.insert_one(test_doc)
            logging.error("❌ HEALTHCARE - SÉCURITÉ: Écriture autorisée (PROBLÈME!)")
        except OperationFailure:
            logging.info("✅ HEALTHCARE - Sécurité: Écriture bloquée (correct)")

        client.close()
        logging.info("✅ HEALTHCARE - Accès clinique en lecture seule validé\n")

    except PyMongoError as e:
        logging.error("❌ HEALTHCARE - Erreur: %s\n", e)


def show_security_summary() -> None:
    """Afficher un résumé des principes de sécurité démontrés."""
    logging.info("🔒 RÉSUMÉ DES PRINCIPES DE SÉCURITÉ")
    logging.info("=" * 60)
    logging.info("✅ Principe de moindre privilège appliqué:")
    logging.info("   • Admin: accès complet (configuration/setup)")
    logging.info("   • Migration: readWrite (migration des données)")
    logging.info("   • ReadOnly: read-only (analyses/rapports)")
    logging.info("   • Healthcare: read-only limité (applications cliniques)")
    logging.info("")
    logging.info("✅ Séparation des responsabilités:")
    logging.info("   • Chaque rôle a un objectif spécifique")
    logging.info("   • Permissions minimales nécessaires")
    logging.info("   • Audit trail via logs d'accès")
    logging.info("")
    logging.info("✅ Sécurité des données médicales:")
    logging.info("   • Accès contrôlé aux données sensibles")
    logging.info("   • Prévention des modifications accidentelles")
    logging.info("   • Traçabilité des opérations")
    logging.info("=" * 60)


def main() -> int:
    """Point d'entrée de la démonstration d'authentification."""
    setup_logging()

    logging.info("🚀 DÉMONSTRATION DES NIVEAUX D'ACCÈS UTILISATEUR - OC P5")
    logging.info("Objectif: Montrer la sécurisation des données médicales")
    logging.info("=" * 80)

    # Vérifier la connectivité
    try:
        admin_client = MongoClient(
            f"mongodb://{get_env('MONGO_USER', 'admin')}:{get_env('MONGO_PASSWORD', 'secure_password')}@{get_env('MONGO_HOST', 'localhost')}:{get_env('MONGO_PORT', '27017')}/?authSource=admin"
        )
        admin_client.admin.command({"ping": 1})
        admin_client.close()
        logging.info("✅ Connectivité MongoDB vérifiée")
    except PyMongoError as e:
        logging.error("❌ Impossible de se connecter à MongoDB: %s", e)
        logging.error("Vérifiez que MongoDB est démarré et que les utilisateurs sont créés")
        logging.error("Exécutez d'abord: python src/setup_auth.py")
        return 1

    # Démonstrations des différents accès
    demo_admin_access()
    demo_migration_access()
    demo_readonly_access()
    demo_healthcare_access()

    # Résumé sécurité
    show_security_summary()

    logging.info("🎯 DÉMONSTRATION TERMINÉE")
    logging.info("📋 Points clés démontrés:")
    logging.info("   • Authentification par rôle utilisateur")
    logging.info("   • Contrôle d'accès basé sur les permissions")
    logging.info("   • Sécurité des données médicales sensibles")
    logging.info("   • Principe de moindre privilège")

    return 0


if __name__ == "__main__":
    sys.exit(main())

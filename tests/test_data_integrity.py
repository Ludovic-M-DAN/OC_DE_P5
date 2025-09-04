"""
Script de test d'intégrité des données - VERSION LEGACY
⚠️  REMPLACÉ PAR test_migration_integrity.py

Ce script reste pour compatibilité mais il est recommandé d'utiliser
les nouveaux tests pytest dans test_migration_integrity.py
"""

import pandas as pd
from pymongo import MongoClient
import logging
import os
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_csv_data():
    """
    Analyse le fichier CSV source et retourne les statistiques
    
    Returns:
        dict: Statistiques du fichier CSV (nombre de lignes, colonnes, etc.)
    """
    logger.info("Analyse du fichier CSV source...")
    
    try:
        # Chargement du CSV
        csv_path = "data/healthcare_dataset.csv"
        df = pd.read_csv(csv_path)
        
        # Collecte des statistiques
        csv_stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "null_values": df.isnull().sum().sum(),
            "duplicates": df.duplicated().sum()
        }
        
        logger.info(f"CSV analysé : {csv_stats['total_rows']} lignes, {csv_stats['total_columns']} colonnes")
        
        return csv_stats
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du CSV : {e}")
        return None

def analyze_mongodb_data():
    """
    Analyse les données dans MongoDB et retourne les statistiques
    
    Returns:
        dict: Statistiques de la base MongoDB
    """
    logger.info("Connexion à MongoDB et analyse des données...")
    
    try:
        # Connexion à MongoDB
        client = MongoClient("mongodb://admin:secure_password@localhost:27017/")
        db = client["healthcare_db"]
        collection = db["patient_records"]
        
        # Collecte des statistiques
        mongo_stats = {
            "total_documents": collection.count_documents({}),
            "sample_document": collection.find_one(),
            "database_name": db.name,
            "collection_name": collection.name
        }
        
        # Analyse d'un échantillon pour vérifier les champs
        sample_docs = list(collection.find().limit(5))
        if sample_docs:
            # Récupère les clés du premier document (hors _id)
            sample_fields = [key for key in sample_docs[0].keys() if key != "_id"]
            mongo_stats["document_fields"] = sample_fields
            mongo_stats["field_count"] = len(sample_fields)
        
        logger.info(f"MongoDB analysé : {mongo_stats['total_documents']} documents")
        
        client.close()
        return mongo_stats
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse MongoDB : {e}")
        return None

def compare_data_integrity(csv_stats, mongo_stats):
    """
    Compare les statistiques CSV et MongoDB pour valider l'intégrité
    
    Args:
        csv_stats (dict): Statistiques du fichier CSV
        mongo_stats (dict): Statistiques de MongoDB
        
    Returns:
        dict: Résultats de la comparaison
    """
    logger.info("Comparaison de l'intégrité des données...")
    
    integrity_results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests_passed": 0,
        "tests_total": 0,
        "details": []
    }
    
    # Test 1: Nombre de lignes/documents
    integrity_results["tests_total"] += 1
    if csv_stats["total_rows"] == mongo_stats["total_documents"]:
        integrity_results["tests_passed"] += 1
        integrity_results["details"].append({
            "test": "Nombre d'enregistrements",
            "status": "PASS",
            "csv_value": csv_stats["total_rows"],
            "mongo_value": mongo_stats["total_documents"]
        })
    else:
        integrity_results["details"].append({
            "test": "Nombre d'enregistrements",
            "status": "FAIL",
            "csv_value": csv_stats["total_rows"],
            "mongo_value": mongo_stats["total_documents"]
        })
    
    # Test 2: Présence de données
    integrity_results["tests_total"] += 1
    if mongo_stats["total_documents"] > 0:
        integrity_results["tests_passed"] += 1
        integrity_results["details"].append({
            "test": "Présence de données dans MongoDB",
            "status": "PASS",
            "csv_value": "N/A",
            "mongo_value": f"{mongo_stats['total_documents']} documents"
        })
    else:
        integrity_results["details"].append({
            "test": "Présence de données dans MongoDB",
            "status": "FAIL",
            "csv_value": "N/A",
            "mongo_value": "0 documents"
        })
    
    # Test 3: Structure des données (approximative)
    integrity_results["tests_total"] += 1
    expected_min_fields = 4  # Au minimum Age, Name, etc.
    if mongo_stats.get("field_count", 0) >= expected_min_fields:
        integrity_results["tests_passed"] += 1
        integrity_results["details"].append({
            "test": "Structure des documents",
            "status": "PASS",
            "csv_value": f"{csv_stats['total_columns']} colonnes",
            "mongo_value": f"{mongo_stats.get('field_count', 0)} champs"
        })
    else:
        integrity_results["details"].append({
            "test": "Structure des documents",
            "status": "FAIL",
            "csv_value": f"{csv_stats['total_columns']} colonnes",
            "mongo_value": f"{mongo_stats.get('field_count', 0)} champs"
        })
    
    return integrity_results

def generate_report(csv_stats, mongo_stats, integrity_results):
    """
    Génère un rapport de test d'intégrité détaillé
    
    Args:
        csv_stats (dict): Statistiques CSV
        mongo_stats (dict): Statistiques MongoDB  
        integrity_results (dict): Résultats des tests
    """
    print("\n" + "="*60)
    print("        RAPPORT DE TEST D'INTÉGRITÉ DES DONNÉES")
    print("="*60)
    
    print(f"\nANALYSE DU FICHIER CSV:")
    print(f"   - Nombre de lignes: {csv_stats['total_rows']}")
    print(f"   - Nombre de colonnes: {csv_stats['total_columns']}")
    print(f"   - Valeurs nulles: {csv_stats['null_values']}")
    print(f"   - Doublons: {csv_stats['duplicates']}")
    
    print(f"\nANALYSE MONGODB:")
    print(f"   - Base de données: {mongo_stats['database_name']}")
    print(f"   - Collection: {mongo_stats['collection_name']}")
    print(f"   - Nombre de documents: {mongo_stats['total_documents']}")
    print(f"   - Champs par document: {mongo_stats.get('field_count', 'N/A')}")
    
    print(f"\nRÉSULTATS DES TESTS D'INTÉGRITÉ:")
    print(f"   - Tests réussis: {integrity_results['tests_passed']}/{integrity_results['tests_total']}")
    print(f"   - Timestamp: {integrity_results['timestamp']}")
    
    print(f"\nDÉTAILS DES TESTS:")
    for detail in integrity_results["details"]:
        print(f"   [{detail['status']}] {detail['test']}")
        print(f"      CSV: {detail['csv_value']} | MongoDB: {detail['mongo_value']}")
    
    # Conclusion
    success_rate = (integrity_results['tests_passed'] / integrity_results['tests_total']) * 100
    print(f"\nCONCLUSION:")
    if success_rate == 100:
        print(f"   [OK] MIGRATION VALIDÉE - Taux de réussite: {success_rate:.0f}%")
        print(f"   [OK] L'intégrité des données est préservée")
    else:
        print(f"   [WARNING] MIGRATION PARTIELLE - Taux de réussite: {success_rate:.0f}%")
        print(f"   [WARNING] Vérifier les tests en échec ci-dessus")
    
    print("="*60)

def main():
    """
    Fonction principale - Execute tous les tests d'intégrité
    """
    logger.info("Démarrage des tests d'intégrité des données")
    
    # Analyse du CSV
    csv_stats = analyze_csv_data()
    if not csv_stats:
        logger.error("Impossible d'analyser le fichier CSV")
        return
    
    # Analyse de MongoDB
    mongo_stats = analyze_mongodb_data()
    if not mongo_stats:
        logger.error("Impossible d'analyser MongoDB")
        return
    
    # Comparaison et tests d'intégrité
    integrity_results = compare_data_integrity(csv_stats, mongo_stats)
    
    # Génération du rapport
    generate_report(csv_stats, mongo_stats, integrity_results)
    
    logger.info("Tests d'intégrité terminés")

if __name__ == "__main__":
    main()

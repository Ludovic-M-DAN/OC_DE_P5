import csv
import logging
import os
import sys
from typing import Generator, List, Dict

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError, PyMongoError


def setup_logging() -> None:
    """Configurer un logging simple pour voir la progression et les erreurs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_env(name: str, default: str) -> str:
    """Lire une variable d'environnement avec une valeur par défaut."""
    value = os.getenv(name)
    return value if value not in (None, "") else default


def get_mongo_client() -> MongoClient:
    """Créer un client MongoDB à partir des variables d'env (valeurs par défaut locales).

    Variables d'environnement prises en compte (optionnelles):
      - MONGO_HOST (par défaut: localhost)
      - MONGO_PORT (par défaut: 27017)
      - MONGO_USER (par défaut: admin)
      - MONGO_PASSWORD (par défaut: secure_password)
      - MONGO_AUTH_DB (par défaut: admin)
    """
    host = get_env("MONGO_HOST", "localhost")
    port = get_env("MONGO_PORT", "27017")
    user = get_env("MONGO_USER", "admin")
    password = get_env("MONGO_PASSWORD", "secure_password")
    auth_db = get_env("MONGO_AUTH_DB", "admin")

    # URI local par défaut (voir README pour le conteneur Docker)
    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource={auth_db}"
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def get_target_collection(client: MongoClient) -> Collection:
    """Récupérer la collection cible en fonction des variables d'env ou des valeurs par défaut.

    Variables d'environnement (optionnelles):
      - MONGO_DB (par défaut: healthcare_db)
      - MONGO_COLLECTION (par défaut: patient_records)
    """
    db_name = get_env("MONGO_DB", "healthcare_db")
    coll_name = get_env("MONGO_COLLECTION", "patient_records")
    return client[db_name][coll_name]


def read_csv_in_batches(csv_path: str, batch_size: int) -> Generator[List[Dict[str, str]], None, None]:
    """Lire le CSV en dictionnaires et produire des lots (batches) de taille fixe.

    - Utilise csv.DictReader (stdlib) pour éviter des dépendances inutiles.
    - Ignore les lignes totalement vides.
    """
    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        batch: List[Dict[str, str]] = []
        for row in reader:
            # Minimal: conserver les valeurs telles quelles (str) ; ignorer lignes vides
            if row is None or all((v is None or str(v).strip() == "") for v in row.values()):
                continue
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch


def insert_batch(collection: Collection, documents: List[Dict[str, str]]) -> Dict[str, int]:
    """Insérer un lot de documents et retourner le nombre de succès/erreurs.

    - ordered=False: continue les insertions même si certaines échouent (meilleure robustesse).
    """
    try:
        result = collection.insert_many(documents, ordered=False)
        return {"success": len(result.inserted_ids), "errors": 0}
    except BulkWriteError as bwe:
        details = bwe.details or {}
        success = details.get("nInserted", 0)
        errors = len(details.get("writeErrors", []))
        logging.error("Bulk write completed with errors: success=%s, errors=%s", success, errors)
        return {"success": success, "errors": errors}
    except PyMongoError as e:
        logging.error("MongoDB error during insert_many: %s", e)
        return {"success": 0, "errors": len(documents)}


def main(argv: List[str]) -> int:
    """Point d'entrée du script de migration.

    Utilisation:
      python src/migrate.py [chemin_du_csv]

    Comportement:
      - Connexion à MongoDB (local par défaut)
      - Lecture du CSV par lots
      - Insertion des lots dans la collection cible
      - Journalisation de la progression et du résumé final
    """
    setup_logging()

    # Paramètres d'entrée (chemin CSV et taille de lot)
    # Chemin CSV : local "data/..." ou Docker "/data/..."
    default_csv = "/data/healthcare_dataset.csv" if get_env("MONGO_HOST", "localhost") == "mongo" else "data/healthcare_dataset.csv"
    csv_path = argv[1] if len(argv) > 1 else get_env("CSV_PATH", default_csv)
    batch_size_str = get_env("MIGRATION_BATCH_SIZE", "1000")
    try:
        batch_size = max(1, int(batch_size_str))
    except ValueError:
        batch_size = 1000

    logging.info("Starting CSV → MongoDB migration")
    logging.info("CSV file: %s", csv_path)
    logging.info("Batch size: %s", batch_size)

    # Connexion et test rapide (ping)
    try:
        client = get_mongo_client()
        client.admin.command({"ping": 1})
    except PyMongoError as e:
        logging.error("Failed to connect/ping MongoDB: %s", e)
        return 1

    collection = get_target_collection(client)

    total_rows = 0
    total_success = 0
    total_errors = 0

    try:
        for batch in read_csv_in_batches(csv_path, batch_size):
            total_rows += len(batch)
            counts = insert_batch(collection, batch)
            total_success += counts["success"]
            total_errors += counts["errors"]
            logging.info(
                "Processed batch: size=%s, success=%s, errors=%s, totals=(rows=%s, success=%s, errors=%s)",
                len(batch), counts["success"], counts["errors"], total_rows, total_success, total_errors,
            )
    except FileNotFoundError:
        logging.error("CSV file not found: %s", csv_path)
        client.close()
        return 1
    except Exception as e:  # Minimal: surface toute erreur inattendue
        logging.error("Unexpected error during migration: %s", e)
        client.close()
        return 1

    client.close()

    logging.info("Migration summary: rows_read=%s, inserted=%s, errors=%s", total_rows, total_success, total_errors)

    # Politique de code de sortie: succès si au moins un document inséré
    return 0 if total_success > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

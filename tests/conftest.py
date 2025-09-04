"""
Configuration pytest pour les tests du projet P5_OC_DE
Fixtures partagées et configuration des tests
"""

import pytest
import pandas as pd
from pymongo import MongoClient
import os


@pytest.fixture(scope="session")
def project_root():
    """Fixture pour obtenir le chemin racine du projet"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def csv_file_path(project_root):
    """Fixture pour le chemin du fichier CSV"""
    return os.path.join(project_root, "data", "healthcare_dataset.csv")


@pytest.fixture(scope="session")
def mongodb_connection_string():
    """Fixture pour la chaîne de connexion MongoDB"""
    return "mongodb://admin:secure_password@localhost:27017/"


@pytest.fixture(scope="session")
def database_name():
    """Fixture pour le nom de la base de données"""
    return "healthcare_db"


@pytest.fixture(scope="session")
def collection_name():
    """Fixture pour le nom de la collection"""
    return "patient_records"


def pytest_configure(config):
    """Configuration globale des tests"""
    # Marqueurs personnalisés
    config.addinivalue_line("markers", "slow: marque les tests lents")
    config.addinivalue_line("markers", "integration: tests d'intégration")
    config.addinivalue_line("markers", "unit: tests unitaires")


def pytest_collection_modifyitems(config, items):
    """Modification des items de collection pour ajouter des marqueurs automatiques"""
    for item in items:
        # Marquer automatiquement les tests selon leur nom
        if "integration" in item.name or "mongodb" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.name or item.parent.name.startswith("test_unit"):
            item.add_marker(pytest.mark.unit)
        elif "performance" in item.name.lower() or "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)

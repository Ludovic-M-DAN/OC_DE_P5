"""
Tests d'intégrité de la migration CSV → MongoDB avec pytest
Tests automatisés pour valider la qualité des données avant/après migration
"""

import pytest
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import os
from datetime import datetime


class TestDataIntegrity:
    """Classe de tests pour l'intégrité des données"""
    
    @pytest.fixture(scope="class")
    def csv_data(self):
        """Fixture pour charger les données CSV"""
        csv_path = "data/healthcare_dataset.csv"
        return pd.read_csv(csv_path)
    
    @pytest.fixture(scope="class")
    def mongo_client(self):
        """Fixture pour la connexion MongoDB"""
        client = MongoClient("mongodb://admin:secure_password@localhost:27017/")
        yield client["healthcare_db"]
        client.close()
    
    def test_csv_file_exists(self):
        """Test 1: Vérifier que le fichier CSV existe"""
        csv_path = "data/healthcare_dataset.csv"
        assert os.path.exists(csv_path), f"Fichier CSV non trouvé: {csv_path}"
    
    def test_csv_not_empty(self, csv_data):
        """Test 2: Vérifier que le CSV n'est pas vide"""
        assert not csv_data.empty, "Le fichier CSV est vide"
        assert len(csv_data) > 0, "Le CSV ne contient aucune ligne de données"
    
    def test_csv_required_columns(self, csv_data):
        """Test 3: Vérifier que les colonnes requises sont présentes"""
        required_columns = ['Age', 'Name', 'Date of Admission', 'Medical Condition']
        missing_columns = [col for col in required_columns if col not in csv_data.columns]
        assert len(missing_columns) == 0, f"Colonnes manquantes: {missing_columns}"
    
    def test_csv_data_quality(self, csv_data):
        """Test 4: Vérifier la qualité des données CSV"""
        # Test des valeurs nulles
        null_count = csv_data.isnull().sum().sum()
        assert null_count == 0, f"Valeurs nulles détectées: {null_count}"
        
        # Test des doublons (informatif, pas bloquant)
        duplicate_count = csv_data.duplicated().sum()
        if duplicate_count > 0:
            # Warning informatif seulement
            import warnings
            warnings.warn(f"Doublons détectés: {duplicate_count}", UserWarning)
    
    def test_csv_age_values(self, csv_data):
        """Test 5: Vérifier les valeurs d'âge"""
        if 'Age' in csv_data.columns:
            # Conversion en numérique si nécessaire
            ages = pd.to_numeric(csv_data['Age'], errors='coerce')
            
            # Test des valeurs valides
            invalid_ages = ages[(ages < 0) | (ages > 120)].count()
            assert invalid_ages == 0, f"Ages invalides détectés: {invalid_ages}"
    
    def test_mongodb_connection(self, mongo_client):
        """Test 6: Vérifier la connexion MongoDB"""
        try:
            # Test de ping
            mongo_client.client.admin.command('ping')
            assert True, "Connexion MongoDB OK"
        except Exception as e:
            pytest.fail(f"Connexion MongoDB échouée: {e}")
    
    def test_mongodb_collection_exists(self, mongo_client):
        """Test 7: Vérifier que la collection existe après migration"""
        collection_names = mongo_client.list_collection_names()
        assert "patient_records" in collection_names, "Collection patient_records non trouvée"
    
    def test_mongodb_data_count(self, csv_data, mongo_client):
        """Test 8: Vérifier que le nombre de documents correspond au CSV"""
        csv_count = len(csv_data)
        mongo_count = mongo_client.patient_records.count_documents({})
        
        assert mongo_count > 0, "Aucun document trouvé dans MongoDB"
        assert csv_count == mongo_count, f"Désaccord de comptage: CSV={csv_count}, MongoDB={mongo_count}"
    
    def test_mongodb_document_structure(self, mongo_client):
        """Test 9: Vérifier la structure des documents MongoDB"""
        sample_doc = mongo_client.patient_records.find_one()
        assert sample_doc is not None, "Aucun document trouvé pour l'analyse"
        
        # Vérifier que _id existe (clé primaire MongoDB)
        assert "_id" in sample_doc, "Champ _id manquant dans le document"
        
        # Vérifier un minimum de champs
        expected_fields = ['Age', 'Name', 'Date of Admission', 'Medical Condition']
        sample_fields = list(sample_doc.keys())
        
        # Au moins quelques champs essentiels doivent être présents
        present_fields = [field for field in expected_fields if field in sample_fields]
        assert len(present_fields) >= 3, f"Structure insuffisante: {present_fields}"
    
    def test_mongodb_data_types(self, mongo_client):
        """Test 10: Vérifier les types de données dans MongoDB"""
        sample_doc = mongo_client.patient_records.find_one()
        
        if sample_doc:
            # Test que Age est numérique si présent
            if 'Age' in sample_doc:
                age_value = sample_doc['Age']
                assert isinstance(age_value, (int, float, str)), "Type Age invalide"
                
                # Si c'est une string, elle doit être convertible en nombre
                if isinstance(age_value, str):
                    try:
                        float(age_value)
                    except ValueError:
                        pytest.fail(f"Age non numérique: {age_value}")
    
    def test_migration_completeness(self, csv_data, mongo_client):
        """Test 11: Test de complétude de la migration"""
        # Comparer quelques échantillons aléatoirement
        csv_sample = csv_data.sample(n=min(10, len(csv_data)))
        
        for _, row in csv_sample.iterrows():
            # Chercher un document correspondant (par exemple par nom)
            if 'Name' in row and pd.notna(row['Name']):
                mongo_doc = mongo_client.patient_records.find_one({"Name": row['Name']})
                assert mongo_doc is not None, f"Document manquant pour: {row['Name']}"


class TestPerformanceBasic:
    """Tests de performance basiques"""
    
    @pytest.fixture(scope="class")
    def mongo_client(self):
        """Fixture pour la connexion MongoDB"""
        client = MongoClient("mongodb://admin:secure_password@localhost:27017/")
        yield client["healthcare_db"]
        client.close()
    
    def test_query_response_time(self, mongo_client):
        """Test 12: Vérifier le temps de réponse des requêtes"""
        import time
        
        start_time = time.time()
        count = mongo_client.patient_records.count_documents({})
        query_time = time.time() - start_time
        
        # Temps de réponse acceptable (ajustable selon les besoins)
        max_time = 2.0  # 2 secondes max
        assert query_time < max_time, f"Requête trop lente: {query_time:.2f}s > {max_time}s"
        assert count > 0, "Aucun document trouvé"
    
    def test_indexes_recommended(self, mongo_client):
        """Test 13: Vérifier la présence d'index recommandés"""
        indexes = mongo_client.patient_records.list_indexes()
        index_names = [idx['name'] for idx in indexes]
        
        # Au minimum l'index par défaut _id_ doit exister
        assert '_id_' in index_names, "Index par défaut _id_ manquant"
        
        # Note: Ce test peut être étendu pour vérifier des index spécifiques
        # selon les besoins de performance du projet


class TestUserAuthentication:
    """Classe de tests pour l'authentification et les rôles utilisateurs"""

    def get_user_client(self, username: str, password: str):
        """Helper pour créer un client avec un utilisateur spécifique"""
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27017")
        uri = f"mongodb://{username}:{password}@{host}:{port}/healthcare_db"
        return MongoClient(uri, serverSelectionTimeoutMS=5000)

    def test_admin_connection(self):
        """Test Auth 1: Vérifier la connexion admin"""
        try:
            client = MongoClient("mongodb://admin:secure_password@localhost:27017/?authSource=admin")
            client.admin.command({"ping": 1})
            client.close()
            assert True, "Connexion admin réussie"
        except Exception as e:
            pytest.fail(f"Échec connexion admin: {e}")

    def test_migration_user_read_access(self):
        """Test Auth 2: Vérifier que migration_user peut lire"""
        client = None
        try:
            client = self.get_user_client("migration_user", "migration_secure_2024")
            db = client["healthcare_db"]
            count = db.patient_records.count_documents({})
            assert count >= 0, "Migration user ne peut pas lire"
        except Exception as e:
            pytest.fail(f"Erreur lecture migration_user: {e}")
        finally:
            if client:
                client.close()

    def test_migration_user_write_access(self):
        """Test Auth 3: Vérifier que migration_user peut écrire"""
        client = None
        try:
            client = self.get_user_client("migration_user", "migration_secure_2024")
            db = client["healthcare_db"]

            # Test d'écriture
            test_doc = {
                "patient_id": "TEST_AUTH_MIGRATION",
                "age": "99",
                "diagnosis": "Test authentification",
                "date_recorded": "2024-01-01"
            }
            result = db.patient_records.insert_one(test_doc)
            assert result.inserted_id is not None, "Migration user ne peut pas écrire"

            # Nettoyer
            db.patient_records.delete_one({"_id": result.inserted_id})

        except Exception as e:
            pytest.fail(f"Erreur écriture migration_user: {e}")
        finally:
            if client:
                client.close()

    def test_readonly_user_read_access(self):
        """Test Auth 4: Vérifier que readonly_user peut lire"""
        client = None
        try:
            client = self.get_user_client("readonly_user", "readonly_secure_2024")
            db = client["healthcare_db"]
            count = db.patient_records.count_documents({})
            assert count >= 0, "Readonly user ne peut pas lire"
        except Exception as e:
            pytest.fail(f"Erreur lecture readonly_user: {e}")
        finally:
            if client:
                client.close()

    def test_readonly_user_write_denied(self):
        """Test Auth 5: Vérifier que readonly_user NE peut PAS écrire"""
        client = None
        try:
            client = self.get_user_client("readonly_user", "readonly_secure_2024")
            db = client["healthcare_db"]

            # Test d'écriture (devrait échouer)
            test_doc = {
                "patient_id": "TEST_AUTH_READONLY",
                "age": "99",
                "diagnosis": "Test authentification",
                "date_recorded": "2024-01-01"
            }

            # Cette opération devrait lever une exception OperationFailure
            with pytest.raises(OperationFailure):
                db.patient_records.insert_one(test_doc)

        except pytest.raises.Exception:
            # C'est le comportement attendu
            pass
        except Exception as e:
            pytest.fail(f"Erreur inattendue readonly_user: {e}")
        finally:
            if client:
                client.close()

    def test_healthcare_user_read_access(self):
        """Test Auth 6: Vérifier que healthcare_user peut lire"""
        client = None
        try:
            client = self.get_user_client("healthcare_user", "healthcare_secure_2024")
            db = client["healthcare_db"]
            count = db.patient_records.count_documents({})
            assert count >= 0, "Healthcare user ne peut pas lire"
        except Exception as e:
            pytest.fail(f"Erreur lecture healthcare_user: {e}")
        finally:
            if client:
                client.close()

    def test_healthcare_user_write_denied(self):
        """Test Auth 7: Vérifier que healthcare_user NE peut PAS écrire"""
        client = None
        try:
            client = self.get_user_client("healthcare_user", "healthcare_secure_2024")
            db = client["healthcare_db"]

            # Test d'écriture (devrait échouer)
            test_doc = {
                "patient_id": "TEST_AUTH_HEALTHCARE",
                "age": "99",
                "diagnosis": "Test authentification",
                "date_recorded": "2024-01-01"
            }

            # Cette opération devrait lever une exception OperationFailure
            with pytest.raises(OperationFailure):
                db.patient_records.insert_one(test_doc)

        except pytest.raises.Exception:
            # C'est le comportement attendu
            pass
        except Exception as e:
            pytest.fail(f"Erreur inattendue healthcare_user: {e}")
        finally:
            if client:
                client.close()

    def test_invalid_credentials_denied(self):
        """Test Auth 8: Vérifier que les credentials invalides sont rejetés"""
        try:
            # Essayer de se connecter avec des credentials invalides
            client = self.get_user_client("invalid_user", "wrong_password")
            db = client["healthcare_db"]
            # Cette ligne devrait lever une exception
            db.patient_records.count_documents({})
            pytest.fail("Connexion avec credentials invalides réussie (PROBLÈME!)")
        except Exception:
            # C'est le comportement attendu
            assert True, "Credentials invalides correctement rejetés"

    def test_user_isolation(self):
        """Test Auth 9: Vérifier l'isolation entre utilisateurs"""
        # Tester que chaque utilisateur ne voit que ses propres permissions
        # et pas celles des autres utilisateurs

        # Test migration_user ne peut pas faire des opérations admin
        client = None
        try:
            client = self.get_user_client("migration_user", "migration_secure_2024")
            db = client["healthcare_db"]

            # Tester une opération d'administration (devrait échouer)
            try:
                db.command("createUser", {"user": "test", "pwd": "test", "roles": []})
                pytest.fail("Migration user peut créer des utilisateurs (PROBLÈME!)")
            except OperationFailure:
                # C'est le comportement attendu
                assert True, "Migration user ne peut pas créer d'utilisateurs"

        except Exception as e:
            pytest.fail(f"Erreur isolation migration_user: {e}")
        finally:
            if client:
                client.close()

    def test_secure_password_storage(self):
        """Test Auth 10: Vérifier que l'authentification fonctionne de manière sécurisée"""
        # Ce test vérifie que l'authentification fonctionne sans exposer les détails de sécurité
        # (les détails de hachage ne sont pas accessibles via l'API normale pour des raisons de sécurité)
        try:
            # Vérifier que tous les utilisateurs peuvent se connecter avec leurs credentials
            test_users = [
                ("migration_user", "migration_secure_2024"),
                ("readonly_user", "readonly_secure_2024"),
                ("healthcare_user", "healthcare_secure_2024")
            ]

            for username, password in test_users:
                client = self.get_user_client(username, password)
                db = client["healthcare_db"]

                # Test simple de connexion et lecture
                count = db.patient_records.count_documents({})
                assert count >= 0, f"Connexion échouée pour {username}"

                client.close()

            # Vérifier que des credentials invalides sont rejetés
            try:
                invalid_client = self.get_user_client("invalid_user", "wrong_password")
                db = invalid_client["healthcare_db"]
                db.patient_records.count_documents({})  # Cette ligne devrait échouer
                pytest.fail("Connexion avec credentials invalides réussie (PROBLÈME!)")
            except Exception:
                # C'est le comportement attendu
                pass

            assert True, "Authentification sécurisée validée"

        except Exception as e:
            pytest.fail(f"Erreur authentification sécurisée: {e}")


if __name__ == "__main__":
    # Permettre l'exécution directe pour debug
    pytest.main([__file__, "-v"])

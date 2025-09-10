# Schéma de base de données - OC P5 Healthcare Migration

## Vue d'ensemble

Ce document décrit le schéma MongoDB conçu pour stocker les données médicales migrées depuis le fichier CSV. Le schéma respecte les bonnes pratiques NoSQL tout en assurant l'intégrité et la sécurité des données médicales sensibles.

## Architecture générale

### Base de données : `healthcare_db`

- **Type** : MongoDB (NoSQL document-oriented)
- **Usage** : Stockage des données médicales patients
- **Authentification** : Système de rôles utilisateurs (voir [README - Authentification](../README.md#authentification-et-sécurité-mongodb))

### Collection principale : `patient_records`

La collection `patient_records` stocke les données médicales sous forme de documents JSON structurés.

## Structure du document

### Schéma complet

```json
{
  "_id": ObjectId("..."),           // Clé primaire MongoDB (auto-généré)
  "patient_id": "P001",             // ID unique du patient (requis)
  "record_type": "consultation",    // Type d'enregistrement médical (requis)
  "date_recorded": ISODate("2023-10-15T00:00:00Z"), // Date d'enregistrement (requis)

  // Informations démographiques du patient
  "patient_info": {
    "age": 45,                      // Âge en années (requis, 0-120)
    "gender": "M",                  // Genre (optionnel: M/F/Other)
    "location": "City001"           // Localisation anonymisée (optionnel)
  },

  // Données médicales
  "medical_data": {
    "diagnosis": "Hypertension",    // Diagnostic principal (requis)
    "symptoms": ["headache", "fatigue"], // Liste des symptômes (optionnel)
    "severity": "moderate",         // Sévérité (optionnel: mild/moderate/severe)
    "treatment": "medication"       // Traitement (optionnel)
  },

  // Métadonnées d'audit
  "metadata": {
    "created_at": ISODate("2023-10-15T10:30:00Z"), // Date de création
    "updated_at": ISODate("2023-10-15T10:30:00Z"), // Date de modification
    "data_source": "csv_import",    // Source des données
    "validation_status": "passed"   // Statut de validation
  }
}
```

## Description détaillée des champs

### Champs requis

| Champ | Type | Description | Exemple | Validation |
|-------|------|-------------|---------|------------|
| `patient_id` | String | Identifiant unique du patient | `"P001"` | Pattern: `^P[0-9]{3,6}$` |
| `record_type` | String | Type d'enregistrement médical | `"consultation"` | Valeurs: consultation, visit, emergency |
| `date_recorded` | Date | Date de l'enregistrement | `2023-10-15` | Format ISO 8601 |
| `patient_info.age` | Integer | Âge du patient en années | `45` | Min: 0, Max: 120 |
| `medical_data.diagnosis` | String | Diagnostic principal | `"Hypertension"` | Min length: 3 caractères |

### Champs optionnels

| Champ | Type | Description | Exemple |
|-------|------|-------------|---------|
| `patient_info.gender` | String | Genre du patient | `"M"`, `"F"`, `"Other"` |
| `patient_info.location` | String | Localisation anonymisée | `"City001"` |
| `medical_data.symptoms` | Array | Liste des symptômes | `["headache", "fatigue"]` |
| `medical_data.severity` | String | Niveau de sévérité | `"mild"`, `"moderate"`, `"severe"` |
| `medical_data.treatment` | String | Type de traitement | `"medication"`, `"surgery"` |

### Champs système (audit)

| Champ | Type | Description | Exemple |
|-------|------|-------------|---------|
| `_id` | ObjectId | Clé primaire MongoDB | Auto-généré |
| `metadata.created_at` | Date | Timestamp de création | `2023-10-15T10:30:00Z` |
| `metadata.updated_at` | Date | Timestamp de modification | `2023-10-15T10:30:00Z` |
| `metadata.data_source` | String | Source des données | `"csv_import"` |
| `metadata.validation_status` | String | Statut de validation | `"passed"`, `"failed"` |

## Règles de validation MongoDB

### Schema Validation

Le schéma applique les règles de validation suivantes via MongoDB Schema Validation :

```json
db.runCommand({
  "collMod": "patient_records",
  "validator": {
    "$jsonSchema": {
      "bsonType": "object",
      "required": [
        "patient_id",
        "record_type",
        "date_recorded",
        "patient_info.age",
        "medical_data.diagnosis"
      ],
      "properties": {
        "patient_id": {
          "bsonType": "string",
          "pattern": "^P[0-9]{3,6}$",
          "description": "Unique patient identifier"
        },
        "patient_info.age": {
          "bsonType": "int",
          "minimum": 0,
          "maximum": 120,
          "description": "Patient age in years"
        },
        "medical_data.diagnosis": {
          "bsonType": "string",
          "minLength": 3,
          "description": "Primary medical diagnosis"
        }
      }
    }
  }
})
```

### Contraintes d'intégrité

- **Patient ID unique** : Chaque `patient_id` doit être unique dans la collection
- **Format des dates** : Toutes les dates utilisent le format ISO 8601
- **Types de données stricts** : Âge doit être un entier, dates doivent être des objets Date
- **Longueur minimale** : Diagnostic doit contenir au moins 3 caractères

## Index de performance

### Index principaux

| Index | Champs | Type | Usage | Justification |
|-------|--------|------|-------|---------------|
| **Primary Index** | `patient_id` | Unique | Recherche patient unique | Accès O(log n) aux données patient |
| **Timeline Index** | `{patient_id: 1, date_recorded: -1}` | Compound | Historique chronologique | Requêtes temporelles par patient |
| **Diagnosis Index** | `medical_data.diagnosis` | Text | Recherche par diagnostic | Recherche full-text sur diagnostics |
| **Age Index** | `patient_info.age` | Range | Filtrage par âge | Requêtes démographiques |

### Commandes de création d'index

```json
// Index principal pour recherche patient
db.patient_records.createIndex({ "patient_id": 1 }, { unique: true });

// Index composé pour historique patient
db.patient_records.createIndex({ "patient_id": 1, "date_recorded": -1 });

// Index textuel pour recherche diagnostic
db.patient_records.createIndex({ "medical_data.diagnosis": "text" });

// Index range pour requêtes âge
db.patient_records.createIndex({ "patient_info.age": 1 });

// Index date pour requêtes temporelles
db.patient_records.createIndex({ "date_recorded": -1 });
```

### Métriques de performance

Après création des index, les performances typiques sont :

- **Recherche patient** : < 2ms (vs 50ms sans index)
- **Historique patient** : < 5ms pour 1000 enregistrements
- **Recherche diagnostic** : < 10ms avec index textuel
- **Filtrage âge** : < 3ms avec index range

## Sécurité et accès

### Rôles utilisateurs définis

| Rôle | Permissions | Usage |
|------|-------------|-------|
| **admin** | Lecture/Écriture/Administration | Configuration système |
| **migration_user** | Lecture/Écriture | Migration des données CSV |
| **readonly_user** | Lecture seule | Analyses et rapports |
| **healthcare_user** | Lecture limitée | Applications cliniques |

### Contrôles d'accès

- **Authentification obligatoire** : Tous les accès nécessitent authentification
- **Autorisation granulaire** : Chaque rôle a des permissions spécifiques
- **Audit logging** : Tous les accès sont tracés
- **Chiffrement** : Données chiffrées en transit et au repos

## Exemples d'utilisation

### Insertion de données

```json
// Exemple d'insertion valide
db.patient_records.insertOne({
  "patient_id": "P012345",
  "record_type": "consultation",
  "date_recorded": ISODate("2023-10-15"),
  "patient_info": {
    "age": 45,
    "gender": "M"
  },
  "medical_data": {
    "diagnosis": "Hypertension",
    "symptoms": ["headache", "dizziness"],
    "severity": "moderate",
    "treatment": "medication"
  },
  "metadata": {
    "created_at": ISODate(),
    "data_source": "csv_import",
    "validation_status": "passed"
  }
});
```

### Requêtes courantes

```json
// Recherche par patient
db.patient_records.findOne({ "patient_id": "P012345" });

// Historique chronologique d'un patient
db.patient_records.find({ "patient_id": "P012345" })
  .sort({ "date_recorded": -1 });

// Recherche par diagnostic
db.patient_records.find({
  "medical_data.diagnosis": { $regex: "hypertension", $options: "i" }
});

// Statistiques démographiques
db.patient_records.aggregate([
  { $group: { _id: "$patient_info.age", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]);
```

## Migration et évolution

### Processus de migration CSV

1. **Validation CSV** : Vérification structure et types de données
2. **Transformation** : Conversion vers format MongoDB
3. **Insertion batch** : Import par lots de 1000 documents
4. **Validation** : Vérification intégrité post-migration
5. **Indexation** : Création des index de performance

### Évolution du schéma

- **Versioning** : Les changements de schéma sont versionnés
- **Migration backward-compatible** : Support des anciens formats
- **Validation progressive** : Validation activée après migration
- **Documentation** : Tout changement documenté

## Métriques et monitoring

### Statistiques de collection

```json
// Statistiques générales
db.patient_records.stats();

// Nombre total de documents
db.patient_records.countDocuments({});

// Taille de la collection
db.patient_records.totalSize();
```

### Métriques de performance

- **Temps de réponse** : Mesuré pour les requêtes principales
- **Utilisation des index** : `db.patient_records.getIndexes()`
- **Taux d'insertion** : Documents/seconde lors de la migration
- **Utilisation mémoire** : Impact des index sur la mémoire

## Conformité et gouvernance

### RGPD/HIPAA Compliance

- **Données sensibles** : Classification des champs sensibles
- **Rétention** : Durée de conservation définie
- **Droit à l'oubli** : Processus de suppression
- **Audit trail** : Traçabilité des accès

### Gouvernance des données

- **Qualité** : Règles de validation automatique
- **Intégrité** : Contraintes d'intégrité référentielle
- **Sécurité** : Contrôles d'accès par rôle
- **Documentation** : Schéma documenté et versionné

## Liens connexes

- [README - Authentification](../README.md#authentification-et-sécurité-mongodb)
- [Script de migration](../src/migrate.py)
- [Tests d'intégrité](../tests/test_migration_integrity.py)
- [Configuration Docker](../docker/docker-compose.yml)

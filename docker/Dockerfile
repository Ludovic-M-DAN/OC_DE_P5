# Image de base Python 3.9 slim
FROM python:3.9-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les scripts Python
COPY src/ ./src/

# Point d'entrée par défaut : script de migration
CMD ["python", "src/migrate.py"]

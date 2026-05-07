FROM python:3.11-slim

WORKDIR /app

# Installer cron + dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY etl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code ETL (pas le .env — les variables viennent du docker-compose)
COPY etl/ ./etl/

# Créer les dossiers de données
RUN mkdir -p data/raw data/transformed

# Configurer le cron
COPY etl/crontab /etc/cron.d/etl-cron
RUN chmod 0644 /etc/cron.d/etl-cron && crontab /etc/cron.d/etl-cron

# Lancer cron en avant-plan avec logs visibles
CMD ["cron", "-f"]

FROM python:3.11-slim

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python en premier (cache Docker)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'API
COPY api/ .

# Utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

# Pas de --reload en production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

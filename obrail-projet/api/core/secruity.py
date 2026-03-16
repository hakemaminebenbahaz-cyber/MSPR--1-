from fastapi import Header, HTTPException, status
from typing import Optional
from core.config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Vérifie que l'header X-API-Key est présent et valide."""
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante ou invalide. Fournissez l'header X-API-Key.",
        )
    return x_api_key

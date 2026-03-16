from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} avec l'ID {entity_id} non trouvé(e)"
        )

class GareNotFoundException(NotFoundException):
    def __init__(self, gare_id: int):
        super().__init__("Gare", gare_id)

class LigneNotFoundException(NotFoundException):
    def __init__(self, ligne_id: int):
        super().__init__("Ligne", ligne_id)

class HoraireNotFoundException(NotFoundException):
    def __init__(self, horaire_id: int):
        super().__init__("Horaire", horaire_id)

class TrajetNotFoundException(NotFoundException):
    def __init__(self, trajet_id: int):
        super().__init__("Trajet", trajet_id)

class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Erreur de base de données"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
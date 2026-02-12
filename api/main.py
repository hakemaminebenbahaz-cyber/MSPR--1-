from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import gares, lignes, operateurs, trajets, horaires, comparisons
from core.config import settings

app = FastAPI(
    title="ObRail Europe API",
    description="API REST pour l'accès aux données ferroviaires européennes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(gares.router, prefix="/api/v1/gares", tags=["Gares"])
app.include_router(lignes.router, prefix="/api/v1/lignes", tags=["Lignes"])
app.include_router(operateurs.router, prefix="/api/v1/operateurs", tags=["Opérateurs"])
app.include_router(trajets.router, prefix="/api/v1/trajets", tags=["Trajets"])
app.include_router(horaires.router, prefix="/api/v1/horaires", tags=["Horaires"])
app.include_router(comparisons.router, prefix="/api/v1/comparisons", tags=["Analyses & Comparaisons"])

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API ObRail Europe",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "gares": "/api/v1/gares",
            "lignes": "/api/v1/lignes",
            "operateurs": "/api/v1/operateurs",
            "trajets": "/api/v1/trajets",
            "horaires": "/api/v1/horaires",
            "comparisons": "/api/v1/comparisons"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ObRail API",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
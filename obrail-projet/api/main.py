from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from routers import gares, operateurs, dessertes, comparisons
from core.config import settings

app = FastAPI(
    title="ObRail Europe API",
    description="API REST pour l'accès aux données ferroviaires européennes (GTFS SNCF + DB Germany)\n\n"
                "**Authentification** : Tous les endpoints `/api/v1/` nécessitent l'header `X-API-Key`.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "ApiKeyHeader": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"ApiKeyHeader": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    if request.url.path.startswith("/api/v1/"):
        key = request.headers.get("x-api-key")
        if key != settings.API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Clé API manquante ou invalide. Fournissez l'header X-API-Key."},
            )
    return await call_next(request)


app.include_router(operateurs.router,  prefix="/api/v1/operateurs",  tags=["Opérateurs"])
app.include_router(gares.router,       prefix="/api/v1/gares",       tags=["Gares"])
app.include_router(dessertes.router,   prefix="/api/v1/dessertes",   tags=["Dessertes"])
app.include_router(comparisons.router, prefix="/api/v1/comparisons", tags=["Analyses & Comparaisons"])


@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API ObRail Europe",
        "version": "1.0.0",
        "documentation": "/docs",
        "auth": "Header X-API-Key requis sur /api/v1/*",
        "endpoints": {
            "operateurs":  "/api/v1/operateurs",
            "gares":       "/api/v1/gares",
            "dessertes":   "/api/v1/dessertes",
            "comparisons": "/api/v1/comparisons",
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ObRail API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

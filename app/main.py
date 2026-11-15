"""
Punto de entrada de la aplicación FastAPI.

Actividad 10: se monta la carpeta uploads/ como archivos estáticos
bajo el prefijo /static, para servir las imágenes de productos.
"""
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.dependencies import get_db
from app.core.config import settings
from app.routers import productos, auth, pedidos, usuarios

# Creamos las tablas en la base de datos al arrancar
Base.metadata.create_all(bind=engine)

# Instanciamos la app con el título del .env
app = FastAPI(title=settings.PROJECT_NAME)

# ── Middlewares (CORS y Compresión Clase 12) ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ── Archivos estáticos con caché (Clase 10, 11 y 12) ──────────────────────────
class StaticConCache(StaticFiles):
    async def get_response(self, path, scope):
        respuesta = await super().get_response(path, scope)
        if respuesta.status_code == 200:
            respuesta.headers["Cache-Control"] = "public, max-age=2592000, immutable"
        return respuesta


Path("uploads/productos").mkdir(parents=True, exist_ok=True)
Path("app/static/demo").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticConCache(directory="uploads"), name="static")
app.mount("/demo", StaticConCache(directory="app/static/demo"), name="demo")


# ── Endpoint de Salud (Clase 11) ──────────────────────────────────────────────
@app.get("/salud", tags=["Salud"])
def salud(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"estado": "ok", "base": "ok"}


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(productos.router)   # Parte 3 + Actividad 10
app.include_router(auth.router)        # Clase 7: autenticación
app.include_router(pedidos.router)     # Clase 8: pedidos y checkout
app.include_router(usuarios.router)    # Clase 9: gestión de usuarios
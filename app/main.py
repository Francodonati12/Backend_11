"""
Punto de entrada de la aplicación FastAPI.

Actividad 10: se monta la carpeta uploads/ como archivos estáticos
bajo el prefijo /static, para servir las imágenes de productos.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.core.config import settings
from app.routers import productos, auth, pedidos, usuarios

# Creamos las tablas en la base de datos al arrancar
Base.metadata.create_all(bind=engine)

# Instanciamos la app con el título del .env
app = FastAPI(title=settings.PROJECT_NAME)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Archivos estáticos (Actividad 10) ─────────────────────────────────────────
# Creamos la carpeta si no existe para que StaticFiles no lance error en primer arranque
Path("uploads").mkdir(exist_ok=True)
Path("uploads/productos").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="uploads"), name="static")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(productos.router)   # Parte 3 + Actividad 10
app.include_router(auth.router)        # Clase 7: autenticación
app.include_router(pedidos.router)     # Clase 8: pedidos y checkout
app.include_router(usuarios.router)    # Clase 9: gestión de usuarios
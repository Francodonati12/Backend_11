"""
Router de Productos — Actividad 10: subida segura de imágenes.
"""
import os
import secrets
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models import Producto, Usuario
from app import schemas
from app.services import productos as productos_service
from app.utils.archivos import parece_imagen

router = APIRouter(prefix="/productos", tags=["productos"])

# ── Directorio donde se guardan las imágenes ─────────────────────────────────
UPLOAD_DIR = Path("uploads/productos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Extensiones permitidas
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
TAMANO_MAXIMO = 2 * 1024 * 1024  # 2 MB


# ── CRUD básico ───────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    return productos_service.crear_producto(db=db, producto=producto)


@router.get("/", response_model=List[schemas.ProductoOut])
def obtener_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    nombre: Optional[str] = None,
    precio_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    return productos_service.listar_productos(
        db=db, skip=skip, limit=limit, nombre=nombre, precio_max=precio_max
    )


@router.delete("/{producto_id}", status_code=status.HTTP_200_OK)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    exito = productos_service.eliminar_producto(db=db, producto_id=producto_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado exitosamente", "id": producto_id}


# ── Actividad 10: Subida segura de imagen ─────────────────────────────────────

@router.post(
    "/{producto_id}/imagen",
    response_model=schemas.ProductoOut,
    status_code=status.HTTP_200_OK,
    summary="Subir imagen de producto (solo admin)",
    description=(
        "Sube una imagen al producto indicado. "
        "Valida extensión, tamaño (≤ 2 MB) y firma de bytes real. "
        "No confía en el nombre ni en el Content-Type declarado por el cliente."
    ),
)
async def subir_imagen_producto(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    # ── Buscar el producto ────────────────────────────────────────────────────
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    # ── Validación 1: Extensión (barato, antes de leer el fichero) ───────────
    nombre_original = archivo.filename or ""
    ext = os.path.splitext(nombre_original)[1].lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Formato no permitido. Extensiones válidas: {', '.join(EXTENSIONES_PERMITIDAS)}",
        )

    # ── Leer contenido ───────────────────────────────────────────────────────
    contenido = await archivo.read()

    # ── Validación 2: Tamaño ─────────────────────────────────────────────────
    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el límite de 2 MB.",
        )

    # ── Validación 3: Firma de bytes real ────────────────────────────────────
    if not parece_imagen(contenido):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El contenido del archivo no corresponde a una imagen válida (firma inválida).",
        )

    # ── Nombre de archivo seguro (nunca se usa archivo.filename en disco) ────
    nombre_seguro = f"{producto_id}-{secrets.token_hex(8)}{ext}"
    ruta_disco = UPLOAD_DIR / nombre_seguro

    # ── Guardar en disco ─────────────────────────────────────────────────────
    with open(ruta_disco, "wb") as f:
        f.write(contenido)

    # ── Persistir URL relativa en la BD ──────────────────────────────────────
    producto.imagen_url = f"/static/productos/{nombre_seguro}"
    db.commit()
    db.refresh(producto)

    return producto

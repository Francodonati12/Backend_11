from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

# Importamos get_db y require_admin desde dependencies
from app.dependencies import get_db, require_admin
from app.models import Usuario
from app import schemas
from app.services import productos as productos_service

router = APIRouter(prefix="/productos", tags=["productos"])

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
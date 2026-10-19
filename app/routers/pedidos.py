from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Pedido, Usuario
from app.schemas import PedidoCreate, PedidoOut
from app.services.pedidos import crear_pedido, revocar_pedido_service, revocar_pedido_sin_auth

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def checkout(
    datos: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return crear_pedido(db, current_user, datos)


# IMPORTANTE: declara /mios antes que /{pedido_id}
@router.get("/mios", response_model=List[PedidoOut])
def obtener_mis_pedidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Pedido).filter(
        Pedido.usuario_id == current_user.id
    ).order_by(Pedido.creado_en.desc()).all()


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido_por_id(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    
    if not pedido or (pedido.usuario_id != current_user.id and current_user.rol != "admin"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    return pedido


@router.post(
    "/{pedido_id}/revocacion",
    status_code=status.HTTP_201_CREATED,
    summary="Revocar pedido (derecho de arrepentimiento)",
    description=(
        "Disposición 954/2025: el consumidor puede ejercer su derecho de "
        "arrepentimiento sin necesidad de estar autenticado. "
        "Solo se requiere el ID del pedido."
    ),
)
def revocar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
):
    """
    No requiere token. Cualquier persona con el ID del pedido puede solicitar
    la revocación dentro de los 10 días de realizada la compra.
    """
    solicitud = revocar_pedido_sin_auth(db, pedido_id)
    return {
        "codigo": solicitud.codigo,
        "pedido_id": solicitud.pedido_id,
        "creada_en": solicitud.creada_en,
    }
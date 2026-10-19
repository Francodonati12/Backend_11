import json
import secrets
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Usuario, Pedido, SolicitudRevocacion

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def construir_datos_usuario(db: Session, usuario: Usuario) -> Dict[str, Any]:
    # Obtener pedidos con sus ítems
    pedidos_db = db.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()
    pedidos_lista = []
    for p in pedidos_db:
        pedidos_lista.append({
            "id": p.id,
            "total": p.total,
            "estado": p.estado,
            "creado_en": p.creado_en,
            "items": [
                {
                    "producto_id": item.producto_id,
                    "cantidad": item.cantidad,
                    "precio_unitario": item.precio_unitario
                } for item in p.items
            ]
        })

    # Obtener solicitudes de revocación
    revocaciones_db = db.query(SolicitudRevocacion).filter(SolicitudRevocacion.usuario_id == usuario.id).all()
    revocaciones_lista = [
        {
            "codigo": r.codigo,
            "pedido_id": r.pedido_id,
            "creada_en": r.creada_en
        } for r in revocaciones_db
    ]

    return {
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
            "activo": usuario.activo,
            "creado_en": getattr(usuario, "creado_en", getattr(usuario, "created_at", "2026-01-01"))
        },
        "pedidos": pedidos_lista,
        "solicitudes_revocacion": revocaciones_lista
    }


# Parte 3: Ver todos los datos
@router.get("/me/datos")
def obtener_mis_datos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return construir_datos_usuario(db, current_user)


# Parte 3: Descargar archivo JSON
@router.get("/me/exportar")
def exportar_mis_datos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    datos = construir_datos_usuario(db, current_user)
    
    # default=str convierte objetos Decimal y datetime a texto sin romper
    contenido_json = json.dumps(datos, indent=4, default=str)
    
    return Response(
        content=contenido_json,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=mis_datos_usuario_{current_user.id}.json"}
    )


# Parte 4: Baja y anonimización de cuenta

@router.delete("/me", status_code=status.HTTP_200_OK)
def dar_de_baja_cuenta(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        fecha_actual = datetime.now()

        # 1. Re-asociar el usuario a la sesión actual de la BD
        current_user = db.merge(current_user)

        # 2. Desactivar y guardar fecha
        current_user.activo = False
        if hasattr(current_user, "fecha_baja"):
            current_user.fecha_baja = fecha_actual

        # 3. Anonimizar datos personales
        token = secrets.token_hex(4)
        current_user.nombre = f"Usuario Anónimo {token}"
        current_user.email = f"baja_{token}_{current_user.id}@eliminado.com"
        current_user.password_hash = "CUENTA_DESACTIVADA"

        # 4. Guardar cambios en la base de datos
        db.commit()

        return {
            "mensaje": "Cuenta dada de baja y datos anonimizados exitosamente.",
            "id": current_user.id,
            "fecha_baja": getattr(current_user, "fecha_baja", fecha_actual)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la baja: {str(e)}"
        )
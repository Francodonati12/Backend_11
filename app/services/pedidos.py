import secrets
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import ItemPedido, Pedido, Producto, SolicitudRevocacion, Usuario
from app.schemas import PedidoCreate


def crear_pedido(db: Session, usuario: Usuario, datos: PedidoCreate) -> Pedido:
    total_pedido = 0
    items_a_crear = []

    try:
        # 1. Crear cabecera del pedido (se asigna ID antes del commit definitivo)
        nuevo_pedido = Pedido(usuario_id=usuario.id, total=0)
        db.add(nuevo_pedido)
        db.flush()

        # 2. Recorrer ítems
        for item in datos.items:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()

            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El producto con ID {item.producto_id} no existe"
                )

            if producto.stock < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Sin stock suficiente para '{producto.nombre}'. Disponibles: {producto.stock}"
                )

            # Descontar stock y acumular total en servidor usando precio_final
            producto.stock -= item.cantidad
            subtotal = producto.precio_final * item.cantidad
            total_pedido += subtotal

            # Guardar el precio actual congelado del producto
            item_db = ItemPedido(
                pedido_id=nuevo_pedido.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio_final
            )
            items_a_crear.append(item_db)

        nuevo_pedido.total = total_pedido
        db.add_all(items_a_crear)

        db.commit()
        db.refresh(nuevo_pedido)
        return nuevo_pedido

    except HTTPException:
        # Rollback y re-lanza el error HTTP (404 o 409) limpiamente
        db.rollback()
        raise
    except Exception as e:
        # Rollback para cualquier otro fallo inesperado de la BD
        db.rollback()
        raise e


def generar_codigo() -> str:
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"ARR-{fecha}-{secrets.token_hex(3).upper()}"


def revocar_pedido_service(db: Session, usuario: Usuario, pedido_id: int) -> SolicitudRevocacion:
    # 1. Buscar el pedido y verificar que le pertenezca al usuario
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id, Pedido.usuario_id == usuario.id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El pedido no existe o no te pertenece."
        )

    # 2. Verificar que no esté previamente cancelado
    if pedido.estado == "cancelado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El pedido ya se encuentra cancelado."
        )

    # 3. Verificar plazo legal de 10 días
    ahora = datetime.now(timezone.utc)
    creado_en = pedido.creado_en
    if creado_en.tzinfo is None:
        creado_en = creado_en.replace(tzinfo=timezone.utc)

    if (ahora - creado_en).days > 10:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El plazo de 10 días para revocar la compra ha expirado."
        )

    # 4. Transacción: restaurar stock, cambiar estado y registrar la solicitud
    try:
        for item in pedido.items:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if producto:
                producto.stock += item.cantidad

        pedido.estado = "cancelado"

        solicitud = SolicitudRevocacion(
            codigo=generar_codigo(),
            pedido_id=pedido.id,
            usuario_id=usuario.id
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la revocación."
        )
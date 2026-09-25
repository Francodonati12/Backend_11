from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio_final = Column(Float)  # O Numeric(12, 2)
    cuotas_cantidad = Column(Integer)
    cuotas_valor = Column(Float)
    garantia_meses = Column(Integer)
    stock = Column(Integer)

    # Relación con items de pedido
    items_pedido = relationship("ItemPedido", back_populates="producto")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, default="customer")

    # Campos de Clase 7 (Consentimiento)
    acepto_tratamiento = Column(Boolean, nullable=False, default=True)
    fecha_consentimiento = Column(DateTime, default=datetime.utcnow)

    # Campos de Clase 9 (Baja y Anonimización)
    activo = Column(Boolean, default=True, server_default="true", nullable=False)
    fecha_baja = Column(DateTime(timezone=True), nullable=True)

    # Relación con pedidos
    pedidos = relationship("Pedido", back_populates="usuario")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(String, default="pendiente", nullable=False)
    total = Column(Numeric(12, 2), nullable=False)  # Exigido en Numeric por la Clase 8
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relaciones (con cascade para delete-orphan)
    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    __tablename__ = "item_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)  # Exigido en Numeric por la Clase 8

    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto", back_populates="items_pedido")


class SolicitudRevocacion(Base):
    __tablename__ = "solicitudes_revocacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creada_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relaciones
    pedido = relationship("Pedido")
    usuario = relationship("Usuario")
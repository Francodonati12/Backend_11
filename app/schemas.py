from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# Esquemas de Productos
class ProductoCreate(BaseModel):
    nombre: str
    precio_final: float
    cuotas_cantidad: Optional[int] = None
    cuotas_valor: Optional[float] = None
    garantia_meses: Optional[int] = None
    stock: Optional[int] = 0


class ProductoOut(ProductoCreate):
    id: int
    imagen_url: Optional[str] = None  # Actividad 10: URL de la imagen del producto

    class Config:
        from_attributes = True


# Esquemas para la Clase 7 (Autenticación y Usuarios)
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    acepto_tratamiento: bool

    @field_validator("acepto_tratamiento")
    def debe_aceptar_tratamiento(cls, v):
        if not v:
            raise ValueError(
                "Debes aceptar el tratamiento de datos para registrarte."
            )
        return v


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Esquemas para la Clase 8 (Pedidos y Checkout)
class ItemIn(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a 0")


class PedidoCreate(BaseModel):
    items: List[ItemIn] = Field(..., min_length=1)


class ItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float

    class Config:
        from_attributes = True


class PedidoOut(BaseModel):
    id: int
    estado: str
    total: float
    creado_en: datetime
    items: List[ItemOut]

    class Config:
        from_attributes = True
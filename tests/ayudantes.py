"""
Ayudantes para la suite de tests.
"""
from typing import Any, Dict, List, Optional


class TokenStr(str):
    """String que representa un access_token y facilita su uso como cabecera HTTP."""
    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self}"}

    def as_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self}"}


def registrar(
    client,
    email: str = "usuario_test@ecommerce.com",
    password: str = "Password123!",
    nombre: str = "Usuario de Prueba",
    acepto_tratamiento: bool = True,
):
    """
    Envía una petición POST a /auth/register con los datos proporcionados
    y retorna la respuesta del cliente de prueba.
    """
    payload = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "acepto_tratamiento": acepto_tratamiento,
    }
    return client.post("/auth/register", json=payload)


def token_de(client, email: str, password: str) -> TokenStr:
    """
    Realiza login en /auth/login y devuelve el access_token obtenido.
    """
    respuesta = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    if respuesta.status_code == 200:
        token = respuesta.json().get("access_token", "")
        return TokenStr(token)
    return TokenStr("")


def cuerpo_pedido(
    producto_id: int = 1,
    cantidad: int = 1,
    items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Construye el payload para la creación de un pedido (checkout).
    """
    if items is not None:
        return {"items": items}
    return {
        "items": [
            {
                "producto_id": producto_id,
                "cantidad": cantidad,
            }
        ]
    }

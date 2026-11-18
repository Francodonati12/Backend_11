from tests.ayudantes import cuerpo_pedido


def test_compra_descuenta_stock(client, cliente, producto):
    # Compra 1 unidad (hay 2 en stock) -> 201
    respuesta = client.post(
        "/pedidos/",
        json=cuerpo_pedido(producto["id"], 1),
        headers=cliente["headers"],
    )
    assert respuesta.status_code == 201

    # Verificamos que el stock del producto bajó de 2 a 1
    res_productos = client.get("/productos/")
    assert res_productos.status_code == 200
    prod = next(p for p in res_productos.json() if p["id"] == producto["id"])
    assert prod["stock"] == 1


def test_sin_stock_da_409_y_no_toca_nada(client, cliente, producto):
    # Intenta comprar 3 unidades (hay 2 en stock) -> 409
    respuesta = client.post(
        "/pedidos/",
        json=cuerpo_pedido(producto["id"], 3),
        headers=cliente["headers"],
    )
    assert respuesta.status_code == 409

    # El stock del producto sigue en 2
    res_productos = client.get("/productos/")
    assert res_productos.status_code == 200
    prod = next(p for p in res_productos.json() if p["id"] == producto["id"])
    assert prod["stock"] == 2

    # GET /pedidos/mios sigue vacío []
    res_pedidos = client.get("/pedidos/mios", headers=cliente["headers"])
    assert res_pedidos.status_code == 200
    assert res_pedidos.json() == []


def test_precio_congelado(client, cliente, admin, producto):
    precio_original = float(producto["precio_final"])

    # 1. El cliente compra el producto al precio original
    respuesta_compra = client.post(
        "/pedidos/",
        json=cuerpo_pedido(producto["id"], 1),
        headers=cliente["headers"],
    )
    assert respuesta_compra.status_code == 201
    pedido_id = respuesta_compra.json()["id"]

    # 2. El admin le cambia el precio al producto
    nuevo_precio = precio_original + 1000.0
    payload_update = {
        "nombre": producto["nombre"],
        "precio_final": nuevo_precio,
        "cuotas_cantidad": producto.get("cuotas_cantidad", 3),
        "cuotas_valor": nuevo_precio / 3,
        "garantia_meses": producto.get("garantia_meses", 12),
        "stock": 1,
    }
    res_update = client.put(
        f"/productos/{producto['id']}",
        json=payload_update,
        headers=admin["headers"],
    )
    assert res_update.status_code == 200
    assert float(res_update.json()["precio_final"]) == nuevo_precio

    # 3. Al consultar el pedido se conserva el precio viejo (congelado)
    res_pedido = client.get(f"/pedidos/{pedido_id}", headers=cliente["headers"])
    assert res_pedido.status_code == 200
    datos_pedido = res_pedido.json()
    assert float(datos_pedido["total"]) == precio_original
    assert float(datos_pedido["items"][0]["precio_unitario"]) == precio_original


def test_comprar_sin_sesion_da_401(client, producto):
    # POST /pedidos sin headers -> 401
    respuesta = client.post(
        "/pedidos",
        json=cuerpo_pedido(producto["id"], 1),
    )
    assert respuesta.status_code == 401

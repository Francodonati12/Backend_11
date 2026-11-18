from tests.ayudantes import cuerpo_pedido


def test_arrepentimiento_sin_sesion(client, cliente, producto):
    # 1. El cliente realiza una compra de 1 unidad (stock inicial = 2, pasa a 1)
    res_compra = client.post(
        "/pedidos/",
        json=cuerpo_pedido(producto["id"], 1),
        headers=cliente["headers"],
    )
    assert res_compra.status_code == 201
    pedido_id = res_compra.json()["id"]

    # Verificamos que el stock se descontó a 1
    res_prod = client.get("/productos/")
    assert res_prod.status_code == 200
    prod = next(p for p in res_prod.json() if p["id"] == producto["id"])
    assert prod["stock"] == 1

    # 2. Derecho de arrepentimiento sin headers (sin sesión) -> 201 con código
    res_revocacion = client.post(f"/pedidos/{pedido_id}/revocacion")
    assert res_revocacion.status_code == 201
    datos = res_revocacion.json()
    assert "codigo" in datos
    assert datos["codigo"] != ""

    # 3. El stock vuelve a sumarse (vuelve a 2)
    res_prod_post = client.get("/productos/")
    assert res_prod_post.status_code == 200
    prod_post = next(p for p in res_prod_post.json() if p["id"] == producto["id"])
    assert prod_post["stock"] == 2


def test_arrepentimiento_no_revela(client):
    # Pedido inexistente sin headers -> 201 igual con código (no debe arrojar 404 para no filtrar existencia)
    respuesta = client.post("/pedidos/99999/revocacion")
    assert respuesta.status_code == 201
    assert respuesta.status_code != 404
    datos = respuesta.json()
    assert "codigo" in datos
    assert datos["codigo"] != ""

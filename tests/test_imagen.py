def test_archivo_trampa_da_415(client, admin, producto):
    # Sube un archivo con nombre/tipo de imagen pero contenido de texto falso con token de admin -> 415
    archivo_trampa = ("foto.png", b"esto es texto con nombre de imagen", "image/png")
    respuesta = client.post(
        f"/productos/{producto['id']}/imagen",
        files={"archivo": archivo_trampa},
        headers=admin["headers"],
    )
    assert respuesta.status_code == 415


def test_cliente_no_puede_subir_imagen(client, cliente, producto):
    # Mismo archivo con token de cliente regular -> 403 Forbidden
    archivo_trampa = ("foto.png", b"esto es texto con nombre de imagen", "image/png")
    respuesta = client.post(
        f"/productos/{producto['id']}/imagen",
        files={"archivo": archivo_trampa},
        headers=cliente["headers"],
    )
    assert respuesta.status_code == 403


def test_sin_sesion_no_puede_subir_imagen(client, producto):
    # Sin headers de sesión -> 401 Unauthorized
    archivo_trampa = ("foto.png", b"esto es texto con nombre de imagen", "image/png")
    respuesta = client.post(
        f"/productos/{producto['id']}/imagen",
        files={"archivo": archivo_trampa},
    )
    assert respuesta.status_code == 401

from tests.ayudantes import registrar, token_de


def test_registro_sin_consentimiento_se_rechaza(client):
    respuesta = registrar(
        client,
        email="sin_consentimiento@test.com",
        password="Password123!",
        nombre="Usuario Sin Consentimiento",
        acepto_tratamiento=False,
    )
    assert respuesta.status_code == 422


def test_registro_con_consentimiento_y_login(client):
    email = "usuario_valido@test.com"
    password = "Password123!"
    nombre = "Usuario Válido"

    # 1. Registro exitoso
    respuesta_reg = registrar(
        client,
        email=email,
        password=password,
        nombre=nombre,
        acepto_tratamiento=True,
    )
    assert respuesta_reg.status_code == 201
    datos_reg = respuesta_reg.json()

    # Verificamos que no se exponga la contraseña
    assert "password" not in datos_reg
    assert "password_hash" not in datos_reg
    assert datos_reg["email"] == email

    # 2. Login exitoso posterior
    token = token_de(client, email, password)
    assert token != ""

    respuesta_login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert respuesta_login.status_code == 200
    assert "access_token" in respuesta_login.json()


def test_login_con_clave_incorrecta(client, cliente):
    respuesta = client.post(
        "/auth/login",
        data={"username": cliente["email"], "password": "PasswordTotalmenteErroneo123!"},
    )
    assert respuesta.status_code == 401

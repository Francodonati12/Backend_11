# E-Commerce Backend API

API RESTful inicial desarrollada en Python utilizando FastAPI para una plataforma de comercio electrónico en la República Argentina.

## 📋 Descripción del Proyecto

Este proyecto constituye la infraestructura de backend base para una plataforma de e-commerce. Está organizado siguiendo patrones de arquitectura en capas (*Layered Architecture*) para permitir un desarrollo limpio, modular y escalable.

En esta etapa inicial, el proyecto incluye la estructura base de directorios (`routers`, `models`, `schemas`, `services`, `core`) y un endpoint raíz (`GET /`) de verificación e información.

## ⚖️ Marco Legal y Cumplimiento Normativo (Argentina)

Las operaciones y arquitectura de esta API están orientadas al cumplimiento de la legislación aplicable al comercio electrónico en la República Argentina:

- **Ley N° 24.240 (Defensa del Consumidor)**: Normativa marco que rige los derechos de los consumidores e imponen obligaciones de transparencia en transacciones comerciales y contrataciones a distancia.
- **Resolución 424/2020 (Secretaría de Comercio Interior)**: Establece los requerimientos de implementación del **Botón de Arrepentimiento** accesible y destacado para la revocación directa de compras en plataformas de e-commerce.
- **Ley N° 25.326 (Protección de Datos Personales)**: Regula el tratamiento, privacidad y almacenamiento seguro de los datos personales (Habeas Data) procesados por la plataforma.

## 📁 Estructura del Proyecto

```text
mi-ecommerce/
├── .gitignore
├── README.md
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py
    ├── routers/
    ├── models/
    ├── schemas/
    ├── services/
    └── core/
```

## 🚀 Requisitos Previos e Instalación

### Requisitos
- Python 3.10 o superior
- Git

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd mi-ecomerce
   ```

2. **Crear y activar un entorno virtual:**
   - En Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - En Linux / macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Ejecución de la API

Para iniciar el servidor de desarrollo con recarga automática:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

### Documentación de la API (OpenAPI)
FastAPI genera automáticamente la documentación interactiva:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## Tests

La suite completa de tests automatizados corre sobre una base de datos SQLite en memoria (`StaticPool`), garantizando aislamiento total, rapidez y sin tocar la base de datos externa Neon/PostgreSQL.

### Ejecución de los tests

Con el entorno virtual activado, ejecutar:

```bash
pytest -v
```

### Tabla de Tests de la Defensa

| Archivo | Test | Descripción / Verificación | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| `tests/test_salud.py` | `test_salud_responde_con_la_base` | GET `/salud` responde con estado de la base de datos | 200 OK y `{"estado": "ok", "base": "ok"}` |
| `tests/test_registro.py` | `test_registro_sin_consentimiento_se_rechaza` | Registro con `acepto_tratamiento: False` | 422 Unprocessable Entity |
| `tests/test_registro.py` | `test_registro_con_consentimiento_y_login` | Registro válido sin password en JSON de respuesta y posterior login | 201 Created (sin password) y 200 OK |
| `tests/test_registro.py` | `test_login_con_clave_incorrecta` | Intento de login con credenciales erróneas | 401 Unauthorized |
| `tests/test_pedidos.py` | `test_compra_descuenta_stock` | Compra de 1 unidad con stock=2 | 201 Created y stock desciende a 1 |
| `tests/test_pedidos.py` | `test_sin_stock_da_409_y_no_toca_nada` | Intento de compra de 3 unidades con stock=2 | 409 Conflict, stock se mantiene en 2 y `/pedidos/mios` vacío `[]` |
| `tests/test_pedidos.py` | `test_precio_congelado` | Compra de producto, modificación posterior del precio por admin y consulta del pedido | 201 Created, conserva el precio unitario histórico congelado |
| `tests/test_pedidos.py` | `test_comprar_sin_sesion_da_401` | POST `/pedidos` sin cabeceras de autorización | 401 Unauthorized |
| `tests/test_arrepentimiento.py` | `test_arrepentimiento_sin_sesion` | Derecho de arrepentimiento sin sesión (Disp. 954/2025) | 201 Created con código de revocación y stock repuesto |
| `tests/test_arrepentimiento.py` | `test_arrepentimiento_no_revela` | Solicitud de arrepentimiento sobre pedido inexistente (ej. 99999) | 201 Created con código (no revela 404 para evitar filtrado) |
| `tests/test_imagen.py` | `test_archivo_trampa_da_415` | Subida de archivo con extensión de imagen y contenido de texto falso (validación de magic numbers) | 415 Unsupported Media Type |
| `tests/test_imagen.py` | `test_cliente_no_puede_subir_imagen` | Intento de subida de imagen con token de cliente regular | 403 Forbidden |
| `tests/test_imagen.py` | `test_sin_sesion_no_puede_subir_imagen` | Intento de subida de imagen sin cabeceras de sesión | 401 Unauthorized |


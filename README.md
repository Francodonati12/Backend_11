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

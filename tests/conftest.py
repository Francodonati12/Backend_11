import os
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Aseguramos que la URL por defecto en variables de entorno sea SQLite en memoria
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models import Producto, Usuario
from app.core.security import hash_password, crear_token

# Configuración del motor SQLite en memoria usando StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FixtureDict(dict):
    """Permite el acceso a los valores tanto por clave como por atributo."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)


@pytest.fixture(scope="function")
def client():
    """
    Fixture del cliente de prueba.
    Crea las tablas en la base de datos en memoria antes de cada test,
    inyecta la sesión de base de datos correspondiente,
    y destruye las tablas (drop_all) al finalizar.
    """
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def cliente(client):
    """
    Fixture que crea y devuelve un usuario con rol 'customer'
    junto con sus tokens y cabeceras de autorización.
    """
    db = TestingSessionLocal()
    user = Usuario(
        nombre="Cliente Test",
        email="cliente@test.com",
        password_hash=hash_password("Cliente123!"),
        rol="customer",
        acepto_tratamiento=True,
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = crear_token(
        data={"sub": user.email, "rol": user.rol, "tipo": "access"},
        expires_delta=timedelta(minutes=60),
    )
    headers = {"Authorization": f"Bearer {token}"}

    user_data = FixtureDict(
        id=user.id,
        nombre=user.nombre,
        email=user.email,
        password="Cliente123!",
        rol=user.rol,
        token=token,
        headers=headers,
        Authorization=f"Bearer {token}",
    )
    db.close()
    return user_data


@pytest.fixture(scope="function")
def admin(client):
    """
    Fixture que crea y devuelve un usuario con rol 'admin'
    junto con sus tokens y cabeceras de autorización.
    """
    db = TestingSessionLocal()
    user = Usuario(
        nombre="Admin Test",
        email="admin@test.com",
        password_hash=hash_password("Admin123!"),
        rol="admin",
        acepto_tratamiento=True,
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = crear_token(
        data={"sub": user.email, "rol": user.rol, "tipo": "access"},
        expires_delta=timedelta(minutes=60),
    )
    headers = {"Authorization": f"Bearer {token}"}

    user_data = FixtureDict(
        id=user.id,
        nombre=user.nombre,
        email=user.email,
        password="Admin123!",
        rol=user.rol,
        token=token,
        headers=headers,
        Authorization=f"Bearer {token}",
    )
    db.close()
    return user_data


@pytest.fixture(scope="function")
def producto(client):
    """
    Fixture que crea y devuelve un producto con stock=2.
    """
    db = TestingSessionLocal()
    prod = Producto(
        nombre="Teclado Gamer Mecánico",
        precio_final=150.0,
        cuotas_cantidad=3,
        cuotas_valor=50.0,
        garantia_meses=12,
        stock=2,
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)

    prod_data = FixtureDict(
        id=prod.id,
        nombre=prod.nombre,
        precio_final=float(prod.precio_final),
        stock=prod.stock,
        cuotas_cantidad=prod.cuotas_cantidad,
        cuotas_valor=prod.cuotas_valor,
        garantia_meses=prod.garantia_meses,
    )
    db.close()
    return prod_data

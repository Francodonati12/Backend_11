"""
Script de Seed para inicializar la base de datos con datos de demostración (Clase 11).

Puebla la base de datos de producción de manera idempotente (sin duplicar registros):
- Verifica si el usuario administrador existe (según SEED_ADMIN_EMAIL); si no, lo crea con SEED_ADMIN_PASSWORD.
- Verifica si ya existen productos en la base de datos; si la tabla está vacía,
  inserta productos iniciales con su correspondiente imagen_url apuntando a '/demo/<nombre_imagen>'.
"""
import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path al ejecutar directamente
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models import Producto, Usuario


def seed_database():
    """
    Puebla la base de datos sin duplicar registros.
    """
    admin_email = getattr(settings, "SEED_ADMIN_EMAIL", os.getenv("SEED_ADMIN_EMAIL", "admin@ecommerce.com"))
    admin_password = getattr(settings, "SEED_ADMIN_PASSWORD", os.getenv("SEED_ADMIN_PASSWORD", "Admin1234!"))

    db = SessionLocal()
    try:
        # 1. Verificar y crear usuario administrador
        admin = db.query(Usuario).filter(Usuario.email == admin_email).first()
        if not admin:
            nuevo_admin = Usuario(
                nombre="Administrador",
                email=admin_email,
                password_hash=hash_password(admin_password),
                rol="admin",
                acepto_tratamiento=True,
                activo=True,
            )
            db.add(nuevo_admin)
            db.commit()
            print(f"[SEED] Usuario administrador creado exitosamente: {admin_email}")
        else:
            print(f"[SEED] Usuario administrador ya existente ({admin_email}). Omitiendo creación.")

        # 2. Verificar y crear productos iniciales de demo
        hay_productos = db.query(Producto).first()
        if not hay_productos:
            productos_demo = [
                Producto(
                    nombre="Auriculares Bluetooth Pro",
                    precio_final=45999.0,
                    cuotas_cantidad=6,
                    cuotas_valor=7666.5,
                    garantia_meses=12,
                    stock=25,
                    imagen_url="/demo/auriculares.png",
                ),
                Producto(
                    nombre="Teclado Mecánico RGB",
                    precio_final=68500.0,
                    cuotas_cantidad=12,
                    cuotas_valor=5708.33,
                    garantia_meses=24,
                    stock=15,
                    imagen_url="/demo/teclado.png",
                ),
                Producto(
                    nombre="Mouse Gamer Ergonómico",
                    precio_final=29990.0,
                    cuotas_cantidad=3,
                    cuotas_valor=9996.66,
                    garantia_meses=12,
                    stock=40,
                    imagen_url="/demo/mouse.png",
                ),
                Producto(
                    nombre="Monitor Gamer 24'' 144Hz",
                    precio_final=185000.0,
                    cuotas_cantidad=12,
                    cuotas_valor=15416.66,
                    garantia_meses=36,
                    stock=10,
                    imagen_url="/demo/monitor.png",
                ),
            ]
            db.add_all(productos_demo)
            db.commit()
            print(f"[SEED] Se insertaron {len(productos_demo)} productos de demostración exitosamente.")
        else:
            total_prod = db.query(Producto).count()
            print(f"[SEED] Ya existen {total_prod} productos en la base de datos. Omitiendo inserción demo.")

    except Exception as e:
        db.rollback()
        print(f"[SEED ERROR] Error al ejecutar el seed: {e}")
        raise
    finally:
        db.close()


def seed():
    """Alias para invocar la función seed_database()"""
    seed_database()


if __name__ == "__main__":
    seed_database()

from dotenv import load_dotenv
load_dotenv()

import sys

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Agregar la raíz del proyecto al path de Python para que encuentre la carpeta app
sys.path.append(".")

from app.core.config import settings
from app.database import Base
from app.models import Usuario, Pedido, ItemPedido, Producto

# Configuración de Alembic desde el archivo .ini
config = context.config

# Configurar la URL de la base de datos desde settings (Clase 11)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

# Configuración del sistema de logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Asignar la metadata de SQLAlchemy a Alembic para que detecte las tablas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline' (sin conexión directa)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online' (conectado a PostgreSQL)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
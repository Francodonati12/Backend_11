from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración existente (Clase 6)
    PROJECT_NAME: str = "API E-Commerce IRESM"
    DATABASE_URL: str
    CORS_ORIGINS: str

    # Configuración nueva de Seguridad y JWT (Clase 7)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_MIN: int = 30
    REFRESH_MIN: int = 10080

    # Configuración de Seed (Clase 11)
    SEED_ADMIN_EMAIL: str = "admin@ecommerce.com"
    SEED_ADMIN_PASSWORD: str = "Admin1234!"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sistema de Información API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 5

    # Recuperación de contraseña
    frontend_url: str = "http://localhost:5173"
    password_reset_expire_minutes: int = 30

    # Correo (SMTP). Si smtp_host está vacío, el enlace de recuperación
    # se muestra en la consola del backend (modo desarrollo).
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "SIHS <no-reply@sihs.local>"
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()

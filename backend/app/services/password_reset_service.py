from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictException, ValidationException
from app.core.security import generate_reset_token, hash_password, hash_reset_token
from app.models.password_reset_token import PasswordResetToken
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.user_repository import UserRepository


INVALID_TOKEN_MESSAGE = (
    "El enlace de recuperación no es válido o ya expiró. Solicita uno nuevo."
)

# Tiempo mínimo entre dos correos de recuperación para el mismo usuario
RESEND_COOLDOWN = timedelta(seconds=60)


@dataclass(frozen=True)
class PasswordResetEmail:
    """Correo listo para enviar (lo envía la ruta en segundo plano)."""

    to: str
    subject: str
    text: str
    html: str


class PasswordResetService:
    """
    Recuperación de contraseña en dos pasos:
      1. request_reset: genera un token de un solo uso con vencimiento y
         prepara el correo con el enlace. Si el correo no existe o el
         usuario está inactivo no hace nada, pero la API responde igual,
         para no revelar qué correos están registrados.
      2. reset_password: valida el token y cambia la contraseña.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = PasswordResetRepository(db)
        self.user_repository = UserRepository(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # 1. Solicitar el enlace
    # ------------------------------------------------------------------
    def request_reset(self, email: str) -> PasswordResetEmail | None:
        user = self.user_repository.get_by_email(email)

        if not user or not user.is_active:
            return None

        now = self._now()

        # Evita enviar varios correos seguidos con el mismo botón
        latest = self.repository.get_latest_pending(user.id)

        if (
            latest
            and latest.expires_at > now
            and latest.created_at > now - RESEND_COOLDOWN
        ):
            return None

        # Solo el último enlace solicitado sirve
        self.repository.invalidate_pending(user.id, now)

        token, token_hash = generate_reset_token()

        self.repository.create(
            PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=now + timedelta(minutes=settings.password_reset_expire_minutes),
            )
        )

        self._commit("No fue posible generar el enlace de recuperación.")

        link = f"{settings.frontend_url.rstrip('/')}/reset-password?token={token}"

        return self._build_email(user.name, user.email, link)

    # ------------------------------------------------------------------
    # 2. Validar el enlace y cambiar la contraseña
    # ------------------------------------------------------------------
    def validate_token(self, token: str) -> PasswordResetToken:
        reset = self.repository.get_by_hash(hash_reset_token(token))

        if (
            not reset
            or reset.used_at is not None
            or reset.expires_at <= self._now()
            or not reset.user.is_active
        ):
            raise ValidationException(INVALID_TOKEN_MESSAGE)

        return reset

    def reset_password(self, token: str, new_password: str) -> None:
        reset = self.validate_token(token)
        now = self._now()

        reset.user.password_hash = hash_password(new_password)

        # El enlace usado y cualquier otro pendiente dejan de servir
        reset.used_at = now
        self.repository.invalidate_pending(reset.user_id, now)

        self._commit("No fue posible actualizar la contraseña.")

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _commit(self, message: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictException(message)

    @staticmethod
    def _build_email(name: str, email: str, link: str) -> PasswordResetEmail:
        minutos = settings.password_reset_expire_minutes

        text = (
            f"Hola, {name}.\n\n"
            "Recibimos una solicitud para restablecer tu contraseña en SIHS.\n"
            f"Abre este enlace para crear una nueva (vence en {minutos} minutos):\n\n"
            f"{link}\n\n"
            "Si no fuiste tú, ignora este correo: tu contraseña no cambiará."
        )

        html = f"""\
<p>Hola, {name}.</p>
<p>Recibimos una solicitud para restablecer tu contraseña en <strong>SIHS</strong>.</p>
<p><a href="{link}">Crear una nueva contraseña</a></p>
<p>El enlace vence en {minutos} minutos y solo funciona una vez.</p>
<p>Si no fuiste tú, ignora este correo: tu contraseña no cambiará.</p>
"""

        return PasswordResetEmail(
            to=email,
            subject="Recupera tu contraseña de SIHS",
            text=text,
            html=html,
        )

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, token: PasswordResetToken) -> PasswordResetToken:
        self.db.add(token)

        return token

    def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )

        return self.db.scalar(statement)

    def get_latest_pending(self, user_id: int) -> PasswordResetToken | None:
        """Última solicitud sin usar del usuario (para limitar reenvíos)."""

        statement = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .order_by(PasswordResetToken.created_at.desc())
            .limit(1)
        )

        return self.db.scalar(statement)

    def invalidate_pending(self, user_id: int, now: datetime) -> None:
        """Marca como usadas las solicitudes pendientes del usuario."""

        self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )

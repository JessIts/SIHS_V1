from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.roles import UserRole

if TYPE_CHECKING:
    from app.models.coordinacion import Coordinacion

class User(BaseModel):

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    document_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    )
    
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        default=UserRole.USER,
        server_default=UserRole.USER.value,
    )

    # Solo aplica a los coordinadores: la coordinación que gestionan.
    coordinacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("coordinaciones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    coordinacion: Mapped["Coordinacion | None"] = relationship(
        lazy="joined",
    )

"""normalizar correos en minusculas

Corrige el defecto de correos que distinguían mayúsculas: pasa a minúsculas
los correos existentes. Si dos cuentas solo se diferencian por mayúsculas,
no se tocan (habría choque con la restricción UNIQUE) y quedan para revisión
manual del administrador.

Revision ID: d8f3b61e9a42
Revises: c5e2a8f41b37
Create Date: 2026-11-24 10:30:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d8f3b61e9a42"
down_revision: Union[str, Sequence[str], None] = "c5e2a8f41b37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        """
        UPDATE users u
        SET email = lower(trim(u.email))
        WHERE u.email <> lower(trim(u.email))
          AND NOT EXISTS (
              SELECT 1
              FROM users o
              WHERE o.id <> u.id
                AND lower(trim(o.email)) = lower(trim(u.email))
          )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    # No se puede saber cómo estaba escrito cada correo: no hay vuelta atrás.
    pass

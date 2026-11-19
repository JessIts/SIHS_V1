"""coordinacion en usuarios y ambientes

- users.coordinacion_id: la coordinación que gestiona un coordinador.
- ambientes.coordinacion_id: la coordinación dueña del ambiente
  (solo ella puede programar clases en él).
- fn_validar_horario ahora también exige que el ambiente de una casilla
  no pertenezca a otra coordinación distinta a la de la ficha.

Revision ID: a7c3e91d5b20
Revises: 0656244fbcc0
Create Date: 2026-11-18 19:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7c3e91d5b20"
down_revision: Union[str, Sequence[str], None] = "0656244fbcc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION fn_validar_horario() RETURNS trigger AS $$
BEGIN
    -- El instructor debe tener rol instructor
    IF NOT EXISTS (
        SELECT 1 FROM users u
        WHERE u.id = NEW.instructor_id AND u.role = 'instructor'
    ) THEN
        RAISE EXCEPTION 'El usuario % no tiene rol instructor', NEW.instructor_id
            USING ERRCODE = 'check_violation';
    END IF;

    -- La temática debe pertenecer al programa de la ficha
    IF NOT EXISTS (
        SELECT 1
        FROM fichas_trimestre ft
        JOIN fichas f                 ON f.id = ft.ficha_id
        JOIN competencias c           ON c.programa_id = f.programa_id
        JOIN resultados_aprendizaje r ON r.competencia_id = c.id
        WHERE ft.id = NEW.ficha_trimestre_id
          AND r.id = NEW.resultado_id
    ) THEN
        RAISE EXCEPTION 'El resultado % no pertenece al programa de la ficha', NEW.resultado_id
            USING ERRCODE = 'check_violation';
    END IF;

    -- El ambiente no puede ser de otra coordinación (NULL = sin asignar)
    IF NEW.ambiente_id IS NOT NULL AND EXISTS (
        SELECT 1
        FROM ambientes a
        JOIN fichas_trimestre ft ON ft.id = NEW.ficha_trimestre_id
        JOIN fichas f            ON f.id = ft.ficha_id
        JOIN programas p         ON p.id = f.programa_id
        WHERE a.id = NEW.ambiente_id
          AND a.coordinacion_id IS NOT NULL
          AND a.coordinacion_id <> p.coordinacion_id
    ) THEN
        RAISE EXCEPTION 'El ambiente % pertenece a otra coordinación', NEW.ambiente_id
            USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END $$ LANGUAGE plpgsql;
"""

# Versión anterior de la función (la de 0656244fbcc0), para el downgrade
TRIGGER_SQL_ANTERIOR = """
CREATE OR REPLACE FUNCTION fn_validar_horario() RETURNS trigger AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM users u
        WHERE u.id = NEW.instructor_id AND u.role = 'instructor'
    ) THEN
        RAISE EXCEPTION 'El usuario % no tiene rol instructor', NEW.instructor_id
            USING ERRCODE = 'check_violation';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM fichas_trimestre ft
        JOIN fichas f                 ON f.id = ft.ficha_id
        JOIN competencias c           ON c.programa_id = f.programa_id
        JOIN resultados_aprendizaje r ON r.competencia_id = c.id
        WHERE ft.id = NEW.ficha_trimestre_id
          AND r.id = NEW.resultado_id
    ) THEN
        RAISE EXCEPTION 'El resultado % no pertenece al programa de la ficha', NEW.resultado_id
            USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END $$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column("coordinacion_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_coordinacion",
        "users",
        "coordinaciones",
        ["coordinacion_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_users_coordinacion_id"),
        "users",
        ["coordinacion_id"],
        unique=False,
    )

    op.add_column(
        "ambientes",
        sa.Column("coordinacion_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ambientes_coordinacion",
        "ambientes",
        "coordinaciones",
        ["coordinacion_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_ambientes_coordinacion_id"),
        "ambientes",
        ["coordinacion_id"],
        unique=False,
    )

    op.execute(TRIGGER_SQL)


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(TRIGGER_SQL_ANTERIOR)

    op.drop_index(op.f("ix_ambientes_coordinacion_id"), table_name="ambientes")
    op.drop_constraint("fk_ambientes_coordinacion", "ambientes", type_="foreignkey")
    op.drop_column("ambientes", "coordinacion_id")

    op.drop_index(op.f("ix_users_coordinacion_id"), table_name="users")
    op.drop_constraint("fk_users_coordinacion", "users", type_="foreignkey")
    op.drop_column("users", "coordinacion_id")

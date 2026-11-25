from uuid import UUID

import jwt
from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from app.core.scope import UNRESTRICTED, AccessScope
from app.core.security import decode_access_token
from app.models.roles import UserRole
from app.repositories.user_repository import UserRepository

ACCESS_TOKEN_COOKIE = "access_token"


def get_current_user(
    access_token: str | None = Cookie(
        default=None,
        alias=ACCESS_TOKEN_COOKIE,
    ),
    db: Session = Depends(get_db),
):
    if not access_token:
        raise UnauthorizedException(
            "No autenticado."
        )

    try:
        payload = decode_access_token(
            access_token
        )

        user_uuid = UUID(
            payload["sub"]
        )

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError,
    ) as error:
        raise UnauthorizedException(
            "Token inválido."
        ) from error

    repository = UserRepository(db)

    user = repository.get_by_uuid(
        user_uuid=user_uuid,
        include_inactive=False,
    )

    if not user:
        raise UnauthorizedException(
            "Usuario no encontrado o inactivo."
        )

    return user


def get_current_admin(
    user=Depends(get_current_user),
):
    if user.role != UserRole.ADMIN:
        raise ForbiddenException(
            "Permisos insuficientes."
        )

    return user


MANAGER_ROLES = (
    UserRole.ADMIN,
    UserRole.COORDINADOR,
)


def get_current_manager(
    user=Depends(get_current_user),
):
    """Admin o coordinador. El coordinador solo consulta y programa horarios."""

    if user.role not in MANAGER_ROLES:
        raise ForbiddenException(
            "Permisos insuficientes."
        )

    return user


def get_access_scope(
    user=Depends(get_current_manager),
) -> AccessScope:
    if user.role == UserRole.ADMIN:
        return UNRESTRICTED

    if user.coordinacion_id is None:
        raise ForbiddenException(
            "Tu usuario de coordinador no tiene una coordinación asignada. "
            "Pide a un administrador que te asigne una."
        )

    return AccessScope(coordinacion_id=user.coordinacion_id)

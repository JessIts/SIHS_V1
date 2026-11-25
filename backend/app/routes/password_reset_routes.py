from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.common.responses import ApiResponse
from app.controllers.password_reset_controller import PasswordResetController
from app.core.database import get_db
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ResetTokenStatus,
)
from app.services.password_reset_service import PasswordResetService

router = APIRouter(
    prefix="/auth/password",
    tags=["Password recovery"],
)


FORGOT_MESSAGE = (
    "Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña."
)


def get_password_reset_controller(
    db: Session = Depends(get_db),
) -> PasswordResetController:
    service = PasswordResetService(db)
    return PasswordResetController(service)


@router.post(
    "/forgot",
    response_model=ApiResponse[None],
    summary="Solicita el enlace de recuperación (responde igual exista o no el correo).",
)
def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    controller: PasswordResetController = Depends(
        get_password_reset_controller
    ),
):
    controller.forgot_password(data, background_tasks)

    return ApiResponse(
        message=FORGOT_MESSAGE,
    )


@router.get(
    "/reset/validate",
    response_model=ApiResponse[ResetTokenStatus],
    summary="Verifica que el enlace siga vigente antes de mostrar el formulario.",
)
def validate_reset_token(
    token: str = Query(min_length=20, max_length=200),
    controller: PasswordResetController = Depends(
        get_password_reset_controller
    ),
):
    status = controller.validate_token(token)

    return ApiResponse(
        message="Enlace válido.",
        data=status,
    )


@router.post(
    "/reset",
    response_model=ApiResponse[None],
    summary="Define la nueva contraseña con el token del enlace.",
)
def reset_password(
    data: ResetPasswordRequest,
    controller: PasswordResetController = Depends(
        get_password_reset_controller
    ),
):
    controller.reset_password(data)

    return ApiResponse(
        message="Contraseña actualizada correctamente. Ya puedes iniciar sesión.",
    )

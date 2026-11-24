from fastapi import BackgroundTasks

from app.core import email as email_sender
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ResetTokenStatus,
)
from app.services.password_reset_service import PasswordResetService


class PasswordResetController:

    def __init__(self, service: PasswordResetService):
        self.service = service

    def forgot_password(
        self,
        data: ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
    ) -> None:
        mail = self.service.request_reset(data.email)

        # El correo se envía después de responder, para no hacer esperar
        # al usuario (ni delatar con el tiempo de respuesta si el correo existe).
        if mail:
            background_tasks.add_task(
                email_sender.send_email,
                mail.to,
                mail.subject,
                mail.text,
                mail.html,
            )

    def validate_token(self, token: str) -> ResetTokenStatus:
        reset = self.service.validate_token(token)

        return ResetTokenStatus(
            valid=True,
            email=self._mask_email(reset.user.email),
        )

    def reset_password(self, data: ResetPasswordRequest) -> None:
        self.service.reset_password(data.token, data.password)

    @staticmethod
    def _mask_email(email: str) -> str:
        """'angel.gomez@gmail.com' -> 'an*******@gmail.com'"""

        local, _, domain = email.partition("@")
        visible = local[:2]

        return f"{visible}{'*' * max(len(local) - len(visible), 1)}@{domain}"

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings


logger = logging.getLogger("sihs.email")


def send_email(
    to: str,
    subject: str,
    text: str,
    html: str | None = None,
) -> None:
    """
    Envía un correo por SMTP con la configuración del .env.

    Sin SMTP_HOST configurado (desarrollo) no envía nada: escribe el
    correo en la consola del backend para poder copiar el enlace.
    """

    if not settings.smtp_host:
        logger.warning(
            "SMTP no configurado. Correo para %s\nAsunto: %s\n\n%s",
            to,
            subject,
            text,
        )
        print(f"\n===== CORREO (SMTP no configurado) =====\nPara: {to}\nAsunto: {subject}\n\n{text}\n========================================\n")
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text)

    if html:
        message.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()

            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password or "")

            smtp.send_message(message)

    except (smtplib.SMTPException, OSError):
        # El usuario ya recibió la respuesta genérica: solo se registra el fallo.
        logger.exception("No fue posible enviar el correo a %s", to)

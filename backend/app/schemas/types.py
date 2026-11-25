from typing import Annotated

from pydantic import AfterValidator, EmailStr


def _normalize_email(value: str) -> str:
    return value.strip().lower()


# Correo normalizado (sin espacios y en minúsculas): así "Ana@Example.com" y
# "ana@example.com" son la misma cuenta en registro, login y recuperación.
NormalizedEmail = Annotated[EmailStr, AfterValidator(_normalize_email)]

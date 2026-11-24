"""
Recuperación de contraseña: solicitar enlace -> validar -> cambiar contraseña.
El envío de correo se reemplaza por una lista para leer el enlace.
"""
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.core import email as email_sender
from app.core.security import hash_password
from app.models.password_reset_token import PasswordResetToken
from app.models.roles import UserRole
from app.models.user import User


API = "/api/v1"
PASSWORD = "Password123!"
NEW_PASSWORD = "NuevaClave456!"


@pytest.fixture
def outbox(monkeypatch) -> list[dict]:
    sent: list[dict] = []

    def fake_send(to, subject, text, html=None):
        sent.append({"to": to, "subject": subject, "text": text, "html": html})

    monkeypatch.setattr(email_sender, "send_email", fake_send)

    return sent


@pytest.fixture
def usuario(db) -> User:
    suffix = uuid4().hex[:8]

    user = User(
        name=f"Aprendiz {suffix}",
        email=f"reset-{suffix}@example.com",
        phone="3001234567",
        document_number=f"R-{suffix}",
        password_hash=hash_password(PASSWORD),
        role=UserRole.APRENDIZ,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def _token(mail: dict) -> str:
    match = re.search(r"token=([\w-]+)", mail["text"])

    assert match, mail["text"]

    return match.group(1)


def _forgot(client, email: str):
    return client.post(f"{API}/auth/password/forgot", json={"email": email})


def _login(client, email: str, password: str):
    return client.post(f"{API}/auth/login", json={"email": email, "password": password})


def test_flujo_completo_de_recuperacion(client, usuario, outbox):
    r = _forgot(client, usuario.email)
    assert r.status_code == 200
    assert len(outbox) == 1
    assert outbox[0]["to"] == usuario.email

    token = _token(outbox[0])

    # El frontend valida el enlace antes de mostrar el formulario
    r = client.get(f"{API}/auth/password/reset/validate", params={"token": token})
    assert r.status_code == 200, r.json()
    assert r.json()["data"]["valid"] is True
    assert "*" in r.json()["data"]["email"]

    r = client.post(f"{API}/auth/password/reset", json={"token": token, "password": NEW_PASSWORD})
    assert r.status_code == 200, r.json()

    # La contraseña nueva funciona y la anterior ya no
    assert _login(client, usuario.email, NEW_PASSWORD).status_code == 200
    assert _login(client, usuario.email, PASSWORD).status_code == 401

    # El enlace solo sirve una vez
    r = client.post(f"{API}/auth/password/reset", json={"token": token, "password": "OtraClave789!"})
    assert r.status_code == 422
    assert "no es válido o ya expiró" in r.json()["message"]


def test_correo_inexistente_responde_igual_y_no_envia_nada(client, usuario, outbox):
    registrado = _forgot(client, usuario.email)
    inexistente = _forgot(client, f"nadie-{uuid4().hex[:6]}@example.com")

    assert inexistente.status_code == 200
    assert inexistente.json()["message"] == registrado.json()["message"]
    assert len(outbox) == 1


def test_usuario_inactivo_no_recibe_enlace(client, db, usuario, outbox):
    usuario.is_active = False
    db.commit()

    assert _forgot(client, usuario.email).status_code == 200
    assert outbox == []


def test_token_invalido_o_vencido(client, db, usuario, outbox):
    r = client.get(f"{API}/auth/password/reset/validate", params={"token": "x" * 43})
    assert r.status_code == 422

    _forgot(client, usuario.email)
    token = _token(outbox[0])

    # Se vence el enlace
    reset = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == usuario.id).one()
    reset.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()

    r = client.post(f"{API}/auth/password/reset", json={"token": token, "password": NEW_PASSWORD})
    assert r.status_code == 422


def test_solo_el_ultimo_enlace_sirve_y_no_se_reenvia_de_inmediato(client, db, usuario, outbox):
    _forgot(client, usuario.email)

    # Un segundo clic inmediato no envía otro correo
    _forgot(client, usuario.email)
    assert len(outbox) == 1

    primer_token = _token(outbox[0])

    # Pasado el tiempo de espera sí se envía uno nuevo...
    pendiente = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == usuario.id).one()
    pendiente.created_at = datetime.now(timezone.utc) - timedelta(minutes=2)
    db.commit()

    _forgot(client, usuario.email)
    assert len(outbox) == 2

    # ...y el enlace anterior deja de servir
    r = client.get(f"{API}/auth/password/reset/validate", params={"token": primer_token})
    assert r.status_code == 422

    r = client.get(f"{API}/auth/password/reset/validate", params={"token": _token(outbox[1])})
    assert r.status_code == 200


def test_contrasena_nueva_debe_cumplir_longitud(client, usuario, outbox):
    _forgot(client, usuario.email)

    r = client.post(f"{API}/auth/password/reset", json={"token": _token(outbox[0]), "password": "corta"})
    assert r.status_code == 422

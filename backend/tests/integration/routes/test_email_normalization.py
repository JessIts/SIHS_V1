"""
Defecto: el correo distinguía mayúsculas y minúsculas.
'Ana.Prueba@example.com' y 'ana.prueba@example.com' creaban dos cuentas,
y el login / la recuperación solo funcionaban con la escritura exacta.
"""
from uuid import uuid4

from app.core import email as email_sender

API = "/api/v1"
PASSWORD = "Password123!"


def _registrar(client, email: str):
    return client.post(f"{API}/auth/register", json={
        "name": "Ana Prueba",
        "email": email,
        "phone": "3001234567",
        "document_number": f"EM-{uuid4().hex[:8]}",
        "password": PASSWORD,
    })


def test_el_correo_se_guarda_en_minusculas(client):
    local = f"Ana.Prueba.{uuid4().hex[:6]}"

    r = _registrar(client, f"{local}@Example.COM")

    assert r.status_code == 201, r.json()
    assert r.json()["data"]["email"] == f"{local.lower()}@example.com"


def test_no_permite_duplicar_correo_cambiando_mayusculas(client):
    local = f"duplicado.{uuid4().hex[:6]}"

    assert _registrar(client, f"{local}@example.com").status_code == 201

    r = _registrar(client, f"{local.upper()}@example.com")
    assert r.status_code == 409


def test_login_sin_importar_mayusculas(client):
    local = f"login.{uuid4().hex[:6]}"
    _registrar(client, f"{local}@example.com")

    r = client.post(f"{API}/auth/login", json={"email": f"{local.upper()}@EXAMPLE.com", "password": PASSWORD})
    assert r.status_code == 200


def test_recuperacion_sin_importar_mayusculas(client, monkeypatch):
    enviados = []
    monkeypatch.setattr(email_sender, "send_email", lambda *args, **kwargs: enviados.append(args))

    local = f"reset.{uuid4().hex[:6]}"
    _registrar(client, f"{local}@example.com")

    r = client.post(f"{API}/auth/password/forgot", json={"email": f"{local.title()}@Example.com"})
    assert r.status_code == 200
    assert len(enviados) == 1

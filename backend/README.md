# SISTEMA SIHS — Backend API

API REST del Sistema de Información de Horarios (SIHS). Gestiona la programación de clases de las fichas de formación por trimestre, día y franja. Impide choques de ficha, instructor y ambiente, y controla el acceso por rol y por coordinación.

Es el backend que acompañó todo el programa: se desarrolló de forma continua, siempre con la misma arquitectura por capas. Su evolución está en `../_docs/cierre/reflexion-backend.md`.

---

## Contenido

1. [Estado actual](#estado-actual)
2. [Tecnologías](#tecnologías)
3. [Arquitectura](#arquitectura)
4. [Instalación desde cero](#instalación-desde-cero)
5. [Ejecutar con Docker](#ejecutar-con-docker)
6. [Autenticación y roles](#autenticación-y-roles)
7. [Documentación de la API](#documentación-de-la-api)
8. [Pruebas](#pruebas)
9. [Calidad de código](#calidad-de-código)
10. [Estructura de carpetas](#estructura-de-carpetas)

---

## Estado actual

| Módulo | Estado |
|---|---|
| Registro, login y logout con JWT en cookie httponly | ✅ |
| Recuperación de contraseña con enlace de un solo uso | ✅ |
| Roles: admin, coordinador, instructor, aprendiz, user | ✅ |
| Ambientes repartidos por coordinación | ✅ |
| CRUD de sedes, ambientes, coordinaciones, programas, competencias, resultados y actividades | ✅ |
| Catálogos de calendario: jornadas, franjas, días y trimestres | ✅ |
| Fichas, aprendices por ficha y programación por trimestre | ✅ |
| Horarios con reglas anti-choque (API + trigger en la BD) y grilla por ficha | ✅ |
| Paneles personales (`/mi/*`) y resumen para dashboards | ✅ |
| Carga masiva de horarios por archivo | ⏳ Pasa a T7 (hoy existe como prototipo SQL en `../db_horarios`) |

---

## Tecnologías

| Uso | Herramienta | Versión |
|---|---|---|
| Lenguaje | Python | 3.12 o superior |
| Framework web | FastAPI · Starlette | 0.141 · 1.6 |
| Servidor | Uvicorn | 0.52 |
| ORM | SQLAlchemy | 2.0 |
| Migraciones | Alembic | 1.19 |
| Base de datos | PostgreSQL · driver psycopg 3 | 16 · 3.3 |
| Validación y configuración | Pydantic v2 · pydantic-settings · email-validator | 2.13 · 2.15 · 2.3 |
| Autenticación | PyJWT (HS256) en cookie `httponly` | 2.13 |
| Contraseñas | Argon2 (`argon2-cffi`) | 25.1 |
| Pruebas | pytest · TestClient (httpx) · pytest-cov | 9.1 · 0.28 · 7.0 |
| Linter | ruff | 0.16 |

Las versiones exactas están en `requirements.txt` (producción) y `requirements-dev.txt` (pruebas y linter).

---

## Arquitectura

Arquitectura por capas. Cada capa solo conoce a la de abajo:

```text
HTTP Request
     │
     ▼
   Routes        → definen el endpoint, sus dependencias (sesión, rol) y el schema de respuesta
     │
     ▼
 Controllers     → coordinan la operación y convierten resultados a schemas
     │
     ▼
  Services       → lógica de negocio: reglas de horarios, permisos por coordinación, recuperación…
     │
     ▼
 Repositories    → consultas a la base de datos (sin lógica de negocio)
     │
     ▼
SQLAlchemy Models
     │
     ▼
 PostgreSQL      → constraints y trigger fn_validar_horario como última barrera
```

**Piezas transversales:**
- **`BaseService` / `BaseRepository`:** CRUD genérico con UUID público, paginación, filtros y borrado lógico (`is_active`).
- **`AccessScope` (`app/core/scope.py`):** alcance de los datos según el usuario. El admin ve todo; el coordinador solo su coordinación.
- **`ApiResponse[T]`:** formato único de respuesta, `{ success, message, data }`.
- **Excepciones de dominio:** `NotFound`, `Conflict`, `Forbidden`, `Unauthorized` y `Validation`, traducidas a 404, 409, 403, 401 y 422.

El diagrama completo del sistema está en `../_docs/arquitectura/arquitectura.md`.

---

## Instalación desde cero

### Requisitos

- **Python 3.12 o superior.** Compruébalo con `python --version`.
- **PostgreSQL 16**, con un usuario que pueda crear bases de datos (pgAdmin sirve para gestionarlo).
- **Git.** En Windows se recomienda usar **Git Bash** como terminal.

### Pasos

Todos los comandos se ejecutan dentro de la carpeta `backend`.

**1. Crear y activar el entorno virtual**

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash)
# .\.venv\Scripts\Activate.ps1       # Windows (PowerShell)
# source .venv/bin/activate          # Linux / macOS
```

Sabrás que está activo porque la terminal muestra `(.venv)` al inicio de la línea. Actívalo cada vez que abras una terminal nueva.

**2. Instalar las dependencias**

```bash
pip install -r requirements-dev.txt
```

`requirements-dev.txt` incluye las dependencias de `requirements.txt` más las de pruebas y el linter. En producción basta con `requirements.txt`.

**3. Configurar las variables de entorno**

```bash
cp .env.example .env
```

Abre `.env` y completa por lo menos:
- `DATABASE_URL`, por ejemplo `postgresql+psycopg://postgres:tu_clave@localhost:5432/sihs`.
- `JWT_SECRET_KEY`, de al menos 32 caracteres. Para generar una: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

**4. Crear la base de datos y aplicar las migraciones**

```bash
createdb -U postgres sihs            # o créala desde pgAdmin
alembic upgrade head
```

Las migraciones crean las tablas, los constraints y el trigger `fn_validar_horario`.

**5. Cargar datos de prueba (opcional)**

```bash
python -m scripts.seed_horarios
```

Carga 30 registros por entidad y un coordinador. Se puede ejecutar varias veces sin duplicar datos.

**6. Crear un administrador**

El script no crea usuarios: promueve uno que ya existe.
1. Registra un usuario desde la pantalla `/register` del frontend o con `POST /api/v1/auth/register`.
2. Promuévelo:
   ```bash
   python -m scripts.create_admin tu_correo@example.com
   ```

**7. Ejecutar la API**

```bash
uvicorn app.main:app --reload
```

Queda lista cuando la consola muestra `Uvicorn running on http://127.0.0.1:8000`. La documentación interactiva (Swagger) está en `http://localhost:8000/docs`.

### Problemas comunes

| Síntoma | Solución |
|---|---|
| PowerShell no deja activar el entorno ("la ejecución de scripts está deshabilitada") | Ejecuta `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, o usa Git Bash |
| `pip install` falla leyendo `requirements.txt` | El archivo debe estar en UTF-8. En PowerShell no lo regeneres con `pip freeze > requirements.txt`, porque lo guarda en UTF-16 |
| `connection refused` al migrar o al iniciar | PostgreSQL no está corriendo, o `DATABASE_URL` tiene mal el puerto, el usuario o la clave |
| El login funciona en Swagger pero no en el frontend | Abre el frontend en `http://localhost:5173`, no en `127.0.0.1`: la cookie y CORS dependen del nombre del host |

**Variables de entorno** (detalle en `.env.example`):

| Variable | Obligatoria | Uso |
|---|---|---|
| `DATABASE_URL` | Sí | Conexión a PostgreSQL |
| `JWT_SECRET_KEY` | Sí | Firma de los tokens |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No (5) | Duración de la sesión |
| `FRONTEND_URL` | No | Base del enlace de recuperación de contraseña |
| `PASSWORD_RESET_EXPIRE_MINUTES` | No (30) | Vigencia del enlace |
| `SMTP_*` | No | Envío de correos. Sin `SMTP_HOST`, el correo se muestra en la consola |

**Cuentas del seed:**

| Rol | Correo | Contraseña |
|---|---|---|
| Coordinador | `coordinacion.mercadeo@example.com` | `Coordinador123*` |
| Instructor | `carlos.perez@example.com` (y 29 más) | `Instructor123*` |
| Aprendiz | `sofia.martinez@example.com` (y 29 más) | `Aprendiz123*` |

---

## Ejecutar con Docker

El proyecto trae un `docker-compose.yml` en la raíz con tres servicios. Requisito: **Docker Desktop** instalado y abierto.

| Servicio | Contenedor | Puerto en tu PC | Para qué |
|---|---|---|---|
| `db` | `sihs-db` | 5434 | PostgreSQL de desarrollo (base `sihs`). Los datos persisten en el volumen `sihs_pgdata` |
| `db-test` | `sihs-db-test` | 5435 | PostgreSQL de pruebas (base `sihs_test`). Guarda los datos en memoria y se borra al apagarlo |
| `backend` | `sihs-backend` | 8000 | La API. Al arrancar aplica las migraciones (`alembic upgrade head`) |

Se usan los puertos 5434 y 5435 para no chocar con un PostgreSQL instalado localmente (por ejemplo, en el 5432 o el 5433).

### Opción A: todo en Docker

Desde la raíz del proyecto:

```bash
docker compose up --build -d                                        # construye y levanta todo
docker compose ps                                                   # db debe aparecer "healthy"
docker compose exec backend python -m scripts.seed_horarios        # datos de ejemplo
docker compose exec backend python -m scripts.create_admin tu_correo@example.com
```

La API queda en `http://localhost:8000/docs`, y el frontend se ejecuta como siempre con `pnpm dev`.

- El contenedor del backend toma `JWT_SECRET_KEY`, el SMTP y el resto de variables de `backend/.env`.
- `DATABASE_URL` la define el compose: apunta a `db:5432`, que es el nombre del servicio dentro de la red de Docker.
- No tiene `--reload`. Después de cambiar código, reconstrúyelo con `docker compose up --build -d backend`.

### Opción B: base de datos en Docker y backend local (recomendada para desarrollar)

```bash
docker compose up -d db
```

En `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://sihs:sihs_password@localhost:5434/sihs
```

Luego sigue los pasos 4 a 7 de la instalación (migraciones, seed, admin y `uvicorn --reload`). Así no necesitas PostgreSQL instalado y conservas la recarga automática.

### Pruebas contra la base de Docker

```bash
docker compose up -d db-test
```

Define la variable en la terminal y ejecuta pytest:

```powershell
# PowerShell
$env:TEST_DATABASE_URL = "postgresql+psycopg://sihs:sihs_password@localhost:5435/sihs_test"
pytest
```

```bash
# Git Bash
export TEST_DATABASE_URL="postgresql+psycopg://sihs:sihs_password@localhost:5435/sihs_test"
pytest
```

Sin la variable, pytest usa el valor por defecto de `tests/conftest.py`.

### Comandos útiles

| Quiero… | Comando |
|---|---|
| Ver el estado | `docker compose ps` |
| Ver los logs del backend | `docker compose logs -f backend` |
| Entrar a PostgreSQL | `docker compose exec db psql -U sihs -d sihs` |
| Apagar sin perder datos | `docker compose down` |
| Apagar y **borrar** los datos de desarrollo | `docker compose down -v` |

### Problemas comunes con Docker

| Síntoma | Solución |
|---|---|
| `port is already allocated` | Otro programa usa ese puerto: cambia el número de la izquierda en `ports` |
| El backend no conecta con la BD | Dentro de Docker el host es `db`, no `localhost` |
| El backend arranca antes que la BD | No debería pasar: el compose espera el `healthcheck` de `db`. Revisa `docker compose logs db` |

> La contraseña `sihs_password` del compose es solo para desarrollo local. Para un servidor debe venir de variables de entorno (deuda técnica DT-12).

---

## Autenticación y roles

**Sesión:**
1. `POST /auth/login` valida las credenciales y entrega el JWT en una **cookie httponly** `access_token`. JavaScript no puede leerla, y el navegador la envía sola en cada petición.
2. `get_current_user` lee la cookie y valida firma, algoritmo, expiración, `sub` (UUID) y que el usuario esté activo.
3. `POST /auth/logout` borra la cookie.

**Correos:** se guardan en minúsculas, así que el mismo correo escrito con otras mayúsculas es la misma cuenta.

**Recuperación de contraseña:**
1. `POST /auth/password/forgot` responde igual exista o no el correo.
2. Se genera un token aleatorio que vence en 30 minutos, sirve una sola vez y se guarda en la BD solo como hash SHA-256.
3. `POST /auth/password/reset` define la nueva contraseña.

**Roles:**

| Rol | Puede |
|---|---|
| `admin` | Todo: usuarios, catálogos, fichas, ambientes (y su reparto entre coordinaciones) y horarios |
| `coordinador` | Registrar, editar y eliminar **horarios** de las fichas de su coordinación, usando solo los ambientes asignados a ella. Consulta sus fichas, programaciones, ambientes, catálogos e instructores |
| `instructor` | Consultar su agenda, sus fichas y sus programas (`/mi/*`) y editar sus datos básicos |
| `aprendiz` | Consultar su ficha, su horario y su programa (`/mi/*`) y editar sus datos básicos |
| `user` | Rol inicial del registro público hasta que el admin le asigne uno |

**Reglas de horarios** (validadas en el servicio y otra vez en la BD):
- Sin choques: una ficha, un instructor o un ambiente no pueden tener dos clases en el mismo trimestre, día y franja.
- Una clase presencial requiere ambiente; una sincrónica no lleva ambiente.
- El resultado de aprendizaje debe ser del programa de la ficha, y el instructor debe tener rol instructor.
- Ningún usuario, ni el admin, puede usar el ambiente de otra coordinación.
- Un ambiente con clases no se puede reasignar a otra coordinación.

---

## Documentación de la API

Con el backend corriendo:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Colección de Postman con tests:** `../_docs/pruebas/postman/`

Todas las rutas usan el prefijo `/api/v1`.

**Recursos CRUD.** Todos siguen el mismo patrón:
- `GET` para listar (paginado y con filtros) y `GET /{uuid}` para consultar uno.
- `POST`, `PUT /{uuid}` y `DELETE /{uuid}` (borrado lógico).
- `GET /inactive` y `PATCH /{uuid}/activate`.

| Recurso | Ruta | Leer | Escribir |
|---|---|---|---|
| Sedes | `/sedes` | admin, coordinador | admin |
| Ambientes | `/ambientes` (filtros: sede, coordinación, sin coordinación) | admin · coordinador (solo los suyos) | admin |
| Coordinaciones | `/coordinaciones` (+ `/{uuid}/sedes/{sede}`) | admin, coordinador | admin |
| Programas | `/programas` | admin, coordinador | admin |
| Competencias | `/competencias` | admin, coordinador | admin |
| Resultados de aprendizaje | `/resultados-aprendizaje` | admin, coordinador | admin |
| Actividades de aprendizaje | `/actividades-aprendizaje` | admin, coordinador | admin |
| Jornadas · Franjas · Días | `/jornadas` · `/franjas-horarias` · `/dias-semana` | admin, coordinador | admin |
| Trimestres | `/trimestres` | admin, coordinador | admin |
| Fichas | `/fichas` (+ `/{uuid}/aprendices`) | admin · coordinador (solo las suyas) | admin |
| Fichas por trimestre | `/fichas-trimestre` | admin · coordinador (solo las suyas) | admin |
| **Horarios** | `/horarios` | admin · coordinador (solo los suyos) | **admin, coordinador** |

**Otros endpoints:**

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/auth/register` | público | Registro (rol `user`) |
| POST | `/auth/login` · `/auth/logout` | público | Inicia o cierra la sesión (cookie) |
| POST | `/auth/password/forgot` | público | Pide el enlace de recuperación |
| GET | `/auth/password/reset/validate?token=` | público | Verifica el enlace |
| POST | `/auth/password/reset` | público | Define la nueva contraseña |
| GET · PUT | `/users/me` | autenticado | Ver y editar mis datos básicos |
| GET | `/users` · `/users/{uuid}` | admin · coordinador (solo instructores) | Listar y consultar usuarios |
| POST · PUT · DELETE | `/users` · `/users/{uuid}` | admin | Gestión de cuentas |
| PATCH | `/users/{uuid}/role` | admin | Cambia el rol (y la coordinación de un coordinador) |
| GET | `/horarios/grilla/{ficha_trimestre_uuid}` | admin, coordinador | Horario de la ficha en formato franjas × días |
| GET | `/dashboard/resumen` | admin, coordinador | Conteos y programaciones (por coordinación para el coordinador) |
| GET | `/mi/fichas` · `/mi/programas` · `/mi/agenda` · `/mi/horarios/{ft}` | autenticado | Información personal de aprendices e instructores |
| GET | `/health` | público | Estado del servicio |

**Respuestas:**

```json
{ "success": true, "message": "Casilla de horario creada correctamente.", "data": { "...": "..." } }
{ "success": false, "message": "El instructor ya tiene clase en ese día y franja." }
```

| Código | Cuándo |
|---|---|
| 200 / 201 / 204 | Éxito |
| 401 | Sin sesión, token inválido o vencido, credenciales incorrectas |
| 403 | El rol o la coordinación no permiten la operación |
| 404 | No existe, o está fuera del alcance del usuario |
| 409 | Choque o duplicado: horario, correo, código de ficha |
| 422 | Datos inválidos o regla de negocio incumplida |

---

## Pruebas

El plan, la matriz de casos, el reporte y los defectos están en `../_docs/pruebas/`.

```bash
pytest                                 # 129 pruebas
pytest --cov --cov-report=term         # con cobertura
pytest --cov --cov-report=html         # reporte navegable en htmlcov/
```

| Nivel | Cantidad | Ubicación |
|---|---|---|
| Unitarias | 54 | `tests/unit/` |
| Integración (API + PostgreSQL) | 75 | `tests/integration/` |
| API (Postman) | 29 peticiones / 48 tests | `../_docs/pruebas/postman/` |
| E2E (Playwright) | 2 | `../frontend/E2E/` |

**Último resultado:** 129/129, estable en 10 ejecuciones seguidas.

**Cobertura:** 87 % en total; 90 % en el servicio de horarios (módulo crítico) y 97 % en sus rutas.

**Ambiente de pruebas separado:** se usa la base `sihs_test`, configurable con `TEST_DATABASE_URL`. Las tablas se crean al iniciar la sesión de pruebas y se eliminan al terminar. También puede ser el contenedor `db-test` (ver [Ejecutar con Docker](#ejecutar-con-docker)).

---

## Calidad de código

```bash
ruff check .          # 0 errores
ruff check . --fix    # corrige lo automático
```

Reglas activas (`ruff.toml`):
- `E` y `W`: PEP 8.
- `F`: pyflakes.
- `I`: orden de imports.
- `B`: bugbear.
- `UP`: sintaxis moderna.

`B008` se ignora porque FastAPI usa `Depends()` y `Query()` como valores por defecto a propósito.

---

## Estructura de carpetas

```text
backend/
├── alembic/versions/      Migraciones (incluye el trigger fn_validar_horario)
├── app/
│   ├── common/            ApiResponse y paginación
│   ├── controllers/
│   ├── core/              config, BD, seguridad, dependencias, alcance, correo, excepciones
│   ├── models/
│   ├── repositories/
│   ├── routes/            un archivo por recurso + router.py
│   ├── schemas/
│   └── services/
├── scripts/               create_admin.py · seed_horarios.py
├── tests/
│   ├── unit/
│   └── integration/
├── .dockerignore          lo que no se copia a la imagen (.env, .venv, tests…)
├── .env.example
├── Dockerfile             imagen de la API (Python 3.12 slim)
├── pyproject.toml         configuración de pytest y cobertura
├── ruff.toml              configuración del linter
├── requirements.txt
└── requirements-dev.txt
```

# SISTEMA SIHS — Backend API

API REST del Sistema de Información de Horarios (SIHS). Gestiona la programación de clases de las fichas de formación por trimestre, día y franja. Impide choques de ficha, instructor y ambiente, y controla el acceso por rol y por coordinación.

Es el **4.° backend del programa** y el primero construido en Python. La comparación con los anteriores está en `../_docs/cierre/reflexion-backends.md`.

---

## Contenido

1. [Estado actual](#estado-actual)
2. [Tecnologías](#tecnologías)
3. [Arquitectura](#arquitectura)
4. [Instalación desde cero](#instalación-desde-cero)
5. [Autenticación y roles](#autenticación-y-roles)
6. [Documentación de la API](#documentación-de-la-api)
7. [Pruebas](#pruebas)
8. [Calidad de código](#calidad-de-código)
9. [Estructura de carpetas](#estructura-de-carpetas)

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

| Uso | Herramienta |
|---|---|
| Framework web | FastAPI 0.141 |
| ORM y migraciones | SQLAlchemy 2.0 · Alembic |
| Base de datos | PostgreSQL 16 (psycopg 3) |
| Validación | Pydantic v2 · pydantic-settings |
| Seguridad | PyJWT (HS256) · Argon2 |
| Pruebas | pytest · TestClient · pytest-cov |
| Linter | ruff (PEP 8 y errores lógicos) |

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

Requisitos: Python 3.12+ y PostgreSQL 16.

```bash
cd backend

# 1. Entorno virtual
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash)
# .\.venv\Scripts\Activate.ps1     # Windows (PowerShell)
# source .venv/bin/activate        # Linux / macOS

# 2. Dependencias (requirements-dev.txt incluye las de pruebas y el linter)
pip install -r requirements-dev.txt

# 3. Variables de entorno
cp .env.example .env               # completar DATABASE_URL y JWT_SECRET_KEY

# 4. Base de datos
createdb sihs                      # o desde pgAdmin
alembic upgrade head

# 5. Datos de prueba (opcional; idempotente)
python -m scripts.seed_horarios

# 6. Administrador: registra un usuario (pantalla /register o POST /auth/register)
#    y luego promuévelo
python -m scripts.create_admin tu_correo@example.com

# 7. Ejecutar
uvicorn app.main:app --reload
```

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

**Ambiente de pruebas separado:** se usa la base `sihs_test`, configurable con `TEST_DATABASE_URL`. Las tablas se crean al iniciar la sesión de pruebas y se eliminan al terminar.

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
├── .env.example
├── pyproject.toml         configuración de pytest y cobertura
├── ruff.toml              configuración del linter
├── requirements.txt
└── requirements-dev.txt
```

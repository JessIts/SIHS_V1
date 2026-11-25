# Plan de pruebas — SIHS

Sistema de Información de Horarios (SIHS) · Backend FastAPI + Frontend React · Trimestre T6

## 1. Objetivo

Verificar que SIHS cumple sus reglas de negocio principales y que no hay regresiones:

- autenticación por cookie;
- permisos por rol y por coordinación;
- programación de horarios sin choques;
- recuperación de contraseña.

Además, registrar los defectos encontrados con un ciclo reproducible: detectar → corregir → verificar.

## 2. Alcance

| Incluido | Excluido (pasa a T7) |
|---|---|
| Autenticación: login, logout, sesión por cookie httponly, JWT | Pruebas de carga y rendimiento |
| Registro público y gestión de usuarios | Pruebas de seguridad avanzadas (pentesting) |
| Roles: admin, coordinador, instructor, aprendiz | Carga masiva de horarios por archivo (aún no construida) |
| Ambientes por coordinación | Envío real de correos por SMTP (se valida con un sustituto) |
| Horarios: creación, choques, grilla y reglas de modalidad | Compatibilidad con varios navegadores (solo Chrome) |
| Recuperación de contraseña | |
| Paneles personales (`/mi/*`) y dashboard | |
| Registro de fichas desde la interfaz (E2E) | |

**Módulo crítico:** horarios (`horario_service`, `horario_routes`). Ahí están las reglas que el sistema no puede romper: sin choques de ficha, instructor ni ambiente, y solo los ambientes de la coordinación.

## 3. Niveles y tipos de prueba

| Nivel | Qué valida | Herramienta | Dónde está | Cantidad |
|---|---|---|---|---|
| Unitarias | Funciones aisladas con dependencias simuladas (mocks): seguridad, dependencias, servicios, repositorios | pytest + unittest.mock | `backend/tests/unit/` | 54 |
| Integración | Endpoints reales contra PostgreSQL: API → servicio → repositorio → BD | pytest + TestClient | `backend/tests/integration/` | 75 |
| API (caja negra) | Contrato HTTP del sistema en ejecución: códigos, formato y permisos | Postman (Collection Runner) | `_docs/pruebas/postman/` | 29 peticiones, 48 tests |
| Extremo a extremo (E2E) | Flujo completo desde el navegador: React → API → BD | Playwright (Google Chrome) | `frontend/E2E/` | 2 |
| Estático | Estilo PEP 8 y errores lógicos detectables sin ejecutar | ruff (backend), ESLint (frontend) | `backend/ruff.toml`, `frontend/eslint.config.js` | — |

Todas las pruebas automatizadas siguen el patrón **AAA** (Arrange, Act, Assert).

Se incluyen **casos positivos** (lo que debe funcionar) y **negativos** (lo que el sistema debe rechazar): permisos, datos inválidos, choques y tokens vencidos.

## 4. Ambientes

El ambiente de pruebas está **separado** del de desarrollo: las pruebas nunca tocan los datos con los que se trabaja.

| | Desarrollo | Pruebas automatizadas (pytest) | Pruebas de API y E2E |
|---|---|---|---|
| Base de datos | `SISTEMA_SIHS` (definida en `.env`) | `sihs_test` (variable `TEST_DATABASE_URL`) | `sihs_test` o una copia con el seed |
| Datos | Los del equipo | Se crean en cada prueba y se borran al terminar la sesión | `python -m scripts.seed_horarios` (idempotente) |
| Esquema | `alembic upgrade head` | `Base.metadata.create_all` (conftest) | `alembic upgrade head` |
| Correo | Consola (sin SMTP) | Sustituto que guarda los correos en una lista | Consola |

Cómo apuntar el backend a la base de pruebas sin tocar el `.env`:

```bash
export DATABASE_URL="postgresql+psycopg://usuario:password@localhost:5432/sihs_test"
alembic upgrade head
python -m scripts.seed_horarios
uvicorn app.main:app --reload
```

## 5. Criterios

**Entrada:**
- El código compila.
- Las migraciones aplican sin error.
- La base de pruebas existe.

**Salida (para cerrar T6):**
- El 100 % de las pruebas automatizadas pasa en 10 ejecuciones seguidas, sin pruebas intermitentes.
- Cobertura del módulo crítico de horarios ≥ 50 %. Meta del proyecto: ≥ 80 %.
- La colección de Postman pasa completa.
- `ruff check .` termina sin errores.
- Ningún defecto de severidad Alta queda abierto.

**Suspensión:** si falla la base de datos o el arranque del backend, se detiene la ejecución y se registra un defecto.

## 6. Severidad de los defectos

| Severidad | Criterio |
|---|---|
| Alta | Rompe una regla de negocio o de seguridad, o deja sin protección un módulo crítico |
| Media | Resultado incorrecto con alternativa, o pruebas poco confiables |
| Baja | Configuración, portabilidad o detalle visual sin impacto funcional |

**Estados:** Abierto → En corrección → Corregido → Verificado (o Cerrado).

Los defectos se registran como issues de GitHub. El commit que los corrige usa el prefijo `fix(...)` y referencia el issue (`closes #N`).

## 7. Cómo ejecutar

**Backend:** desde `backend`, con el venv activo.

```bash
pip install -r requirements-dev.txt
pytest                                   # todas las pruebas
pytest --cov --cov-report=term           # con cobertura
pytest --cov --cov-report=html           # reporte navegable en htmlcov/
ruff check .                             # linter
```

**Postman:**
1. Importa `SIHS.postman_collection.json` y `SIHS-local.postman_environment.json`.
2. Selecciona el entorno "SIHS local".
3. Ejecuta la colección con el **Collection Runner**.

**E2E:** desde `frontend`, con el backend corriendo y el seed cargado.

```bash
pnpm test:e2e
pnpm lint
```

## 8. Entregables

| Documento | Archivo |
|---|---|
| Plan de pruebas | `_docs/pruebas/plan-de-pruebas.md` |
| Matriz de casos de prueba | `_docs/pruebas/matriz-casos-de-prueba.md` |
| Registro de defectos | `_docs/pruebas/defectos.md` |
| Reporte de ejecución | `_docs/pruebas/reporte-ejecucion.md` |
| Evidencias (salidas de consola) | `_docs/pruebas/evidencias/` |
| Colección y entorno de Postman | `_docs/pruebas/postman/` |

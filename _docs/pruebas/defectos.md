# Registro de defectos — SIHS (T6)

**Sistema de seguimiento:** issues de GitHub (`JessIts/SIHS_V1`), con las etiquetas `bug` y `severidad: alta|media|baja`.

**Ciclo de cada defecto:**
1. **Detectar:** prueba que falla, guardada como evidencia.
2. **Corregir:** commit `fix(...)` con `closes #N`.
3. **Verificar:** volver a ejecutar las pruebas y guardar la evidencia.

| ID | Issue | Título | Severidad | Estado | Detectado con | Commit de corrección | Verificación |
|---|---|---|---|---|---|---|---|
| DEF-01 | #3 | Suite de autenticación y usuarios desactualizada tras el cambio a sesión por cookie | Alta | Verificado | Ejecución 1: 19 fallos y 22 errores | `fix(tests): …` | Ejecución 2: 129/129 |
| DEF-02 | #5 | El correo distingue mayúsculas: permite cuentas duplicadas y falla el login | Alta | Verificado | `test_email_normalization.py` (4 fallos) | `fix(auth): …` | 4/4 y PM 5.2 |
| DEF-03 | #6 | `test_horarios_routes` falla de forma intermitente | Media | Verificado | 4 de 10 ejecuciones con errores | `fix(tests): …` | 10 de 10 ejecuciones limpias |
| DEF-04 | #7 | Playwright busca las pruebas en `e2e` pero la carpeta es `E2E` | Baja | Corregido (falta verificar en Linux/CI) | Revisión de la configuración | `fix(e2e): …` | Pendiente: `pnpm test:e2e` |

Reemplaza `#__` por el número de cada issue cuando lo crees en GitHub.

---

## DEF-01 · Suite de autenticación y usuarios desactualizada tras el cambio a sesión por cookie

- **Severidad:** Alta. El módulo de autenticación quedó sin pruebas confiables: 41 de 122 fallaban, y 4 pasaban sin validar nada.
- **Módulo:** `backend/tests` (autenticación, usuarios y dependencias).
- **Introducido por:** el commit `7f4b4cf` "Se actualizó la sesión local por una sesión con HttpCookie" y el cambio del registro público a `/auth/register`.

**Pasos para reproducir:**
1. `pytest` en `backend`.
2. Revisar `test_auth_routes.py`, `test_user_routes.py` y `tests/unit/core/test_dependencies.py`.

**Resultado esperado:** todas las pruebas pasan y validan el mecanismo real de sesión.

**Resultado obtenido:** `19 failed, 81 passed, 22 errors` (evidencia `01_ejecucion1_suite_antes.txt`). Hay tres causas:
1. Las pruebas crean usuarios con `POST /users` sin sesión, pero ahora ese endpoint es solo para el admin.
2. Esperan el `access_token` en el cuerpo del login y lo envían en `Authorization: Bearer`, pero la API lo maneja en una cookie httponly.
3. Las pruebas unitarias llaman a `get_current_user(credentials=...)`, la firma anterior al cambio.

**Corrección:**
- Las pruebas usan `/auth/register`, leen el token de la cookie y lo envían como cookie.
- Las pruebas unitarias usan `get_current_user(access_token=...)`.
- Se agregaron casos nuevos: la cookie es httponly (CP-01), crear usuarios por `/users` es solo para el admin (CP-11), y falta de cookie (prueba unitaria).

**Verificación:** `129 passed` (evidencia `06_ejecucion2_suite_despues.txt`).

## DEF-02 · El correo distingue mayúsculas: permite cuentas duplicadas y falla el login

- **Severidad:** Alta. Una misma persona puede tener dos cuentas, y no puede iniciar sesión ni recuperar la contraseña si escribe el correo con otras mayúsculas.
- **Módulo:** `schemas` (registro, login, usuarios, recuperación) y `user_repository.get_by_email`.

**Pasos para reproducir:**
1. `POST /auth/register` con `Ana.Prueba@Example.com`.
2. `POST /auth/register` con `ana.prueba@example.com` y otro documento.
3. `POST /auth/login` con `ANA.PRUEBA@example.com`.

**Resultado esperado:**
- El paso 2 responde 409 (correo ya registrado).
- El paso 3 inicia sesión.
- El correo queda guardado en minúsculas.

**Resultado obtenido:**
- El paso 2 responde 201 y crea una segunda cuenta.
- El paso 3 responde 401.
- La recuperación de contraseña no envía el enlace (evidencia `02_DEF-02_correo_antes.txt`).

**Corrección:**
- Tipo `NormalizedEmail` en `app/schemas/types.py`, que quita espacios y pasa a minúsculas. Se usa en el registro, el login, la gestión de usuarios y la recuperación.
- `get_by_email` compara sin distinguir mayúsculas.
- Migración `d8f3b61e9a42`: pasa a minúsculas los correos existentes cuando no generan choque.

**Verificación:** `4 passed` (evidencia `03_DEF-02_correo_despues.txt`), más PM 5.1 y 5.2.

**Pendiente (deuda técnica):** si ya existieran dos cuentas que solo se diferencian por mayúsculas, la migración no las toca y hay que unificarlas a mano. Un índice único sobre `lower(email)` lo impediría a nivel de base de datos.

## DEF-03 · `test_horarios_routes` falla de forma intermitente

- **Severidad:** Media. Una prueba que a veces falla sin que haya cambiado el código le quita confianza a toda la suite.
- **Módulo:** `backend/tests/integration/routes/test_horarios_routes.py` (fixture `escenario`).

**Pasos para reproducir:** ejecutar la suite completa 10 veces seguidas.

**Resultado esperado:** 10 ejecuciones con `129 passed`.

**Resultado obtenido:** 4 de 10 ejecuciones con 1 o 2 errores `409 Ya existe ese trimestre para el año indicado` (evidencia `04_DEF-03_intermitente_antes.txt`).

**Causa:** cada escenario crea un trimestre con un año elegido al azar entre solo 100 valores. Con unos 13 escenarios por ejecución, la probabilidad de que dos coincidan es alta (problema del cumpleaños).

**Corrección:** un contador de sesión asigna a cada escenario un par (año, número) distinto.

**Verificación:** 10 de 10 ejecuciones con `129 passed` (evidencia `05_DEF-03_intermitente_despues.txt`).

## DEF-04 · Playwright busca las pruebas en `e2e` pero la carpeta es `E2E`

- **Severidad:** Baja. En Windows funciona porque el sistema de archivos no distingue mayúsculas. En Linux o en un servidor de integración continua, Playwright no encontraría ninguna prueba.
- **Módulo:** `frontend/playwright.config.ts`.

**Pasos para reproducir:** ejecutar `pnpm test:e2e` en Linux.

**Resultado esperado:** se ejecutan las 2 pruebas de `E2E/fichas.spec.ts`.

**Resultado obtenido:** el directorio `./e2e` no existe.

**Corrección:** `testDir: './E2E'`.

**Verificación:** pendiente. Ejecutar `pnpm test:e2e` y anotar el resultado en el reporte.

---

## Texto para crear los issues en GitHub

Crea cada issue en GitHub → **Issues** → **New issue**, con la etiqueta `bug` y la de severidad. Usa como cuerpo la sección de su defecto de este archivo: pasos, resultado esperado y resultado obtenido.

| Título del issue | Etiquetas |
|---|---|
| `[DEF-01] Suite de autenticación y usuarios desactualizada tras el cambio a sesión por cookie` | `bug`, `severidad: alta` |
| `[DEF-02] El correo distingue mayúsculas: permite cuentas duplicadas y falla el login` | `bug`, `severidad: alta` |
| `[DEF-03] test_horarios_routes falla de forma intermitente` | `bug`, `severidad: media` |
| `[DEF-04] Playwright busca las pruebas en e2e pero la carpeta es E2E` | `bug`, `severidad: baja` |

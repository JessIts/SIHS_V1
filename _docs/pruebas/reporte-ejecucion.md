# Reporte de ejecución de pruebas — SIHS (T6)

**Fecha:** 24-nov-2026 · **Rama:** `main` (después de fusionar recuperación de contraseña) · **Plan:** `plan-de-pruebas.md`

## 1. Ambiente

| | |
|---|---|
| Base de datos | PostgreSQL 16, base `sihs_test` (separada de la de desarrollo) |
| Backend | Python 3.12+, FastAPI 0.141, SQLAlchemy 2.0, pytest 9 |
| Comandos | `pytest`, `pytest --cov`, `ruff check .` (ver `plan-de-pruebas.md`) |
| Datos | Creados por cada prueba; Postman y E2E usan `scripts.seed_horarios` |

## 2. Resumen

| Métrica | Ejecución 1 (antes) | Ejecución 2 (después) |
|---|---|---|
| Pruebas automatizadas del backend | 122 | 129 |
| Pasaron | 81 | **129** |
| Fallaron | 19 | 0 |
| Errores | 22 | 0 |
| Tasa de éxito | 66 % | **100 %** |
| Estabilidad (10 ejecuciones seguidas) | 6 de 10 limpias | **10 de 10 limpias** |
| Cobertura total del backend | No se medía | **87 %** (líneas y ramas) |
| Cobertura del módulo crítico (horarios) | No se medía | **90 %** el servicio, **97 %** las rutas |
| Linter (ruff) | No configurado | **0 errores** |
| Defectos abiertos | 4 | 0 de severidad Alta o Media |

Evidencias: `evidencias/01_ejecucion1_suite_antes.txt` y `evidencias/06_ejecucion2_suite_despues.txt`.

## 3. Resultados por nivel (Ejecución 2)

| Nivel | Pruebas | Resultado |
|---|---|---|
| Unitarias (`tests/unit`) | 54 | 54 pasaron |
| Integración (`tests/integration`) | 75 | 75 pasaron |
| API: colección de Postman | 29 peticiones / 48 tests | 29 de 29 respuestas esperadas en el runner de verificación*. Pendiente: ejecutar en Postman y adjuntar la captura del Runner |
| E2E (Playwright) | 2 | Pendiente de ejecutar en el equipo local (`pnpm test:e2e`) |

\* La colección se validó con un script que envía las mismas peticiones, en el mismo orden, contra una base cargada con el seed, y compara el código de respuesta y los datos clave. La ejecución en la aplicación de Postman se registra en la sección 7.

## 4. Cobertura del módulo crítico

Comando: `pytest --cov --cov-report=term`. Evidencia: `evidencias/07_cobertura.txt`.

| Archivo | Cobertura |
|---|---|
| `app/services/horario_service.py` | 90 % |
| `app/routes/horario_routes.py` | 97 % |
| `app/repositories/horario_repository.py` | 100 % |
| `app/controllers/horario_controller.py` | 100 % |
| `app/schemas/horario.py` | 100 % |
| `app/models/horario.py` | 100 % |
| **Total del backend** | **87 %** |

La meta de la lista de chequeo es ≥ 50 % en el módulo crítico, y se supera.

Lo que queda sin cubrir en `horario_service` son ramas de filtros de listado poco usadas y un mensaje de error de integridad que la validación previa nunca deja llegar a la base de datos.

## 5. Defectos de la ejecución

Detalle completo en `defectos.md`.

| ID | Severidad | Detectado | Corregido y verificado |
|---|---|---|---|
| DEF-01 Suite de auth/usuarios desactualizada | Alta | Ejecución 1: 41 de 122 sin pasar | Ejecución 2: 129/129 |
| DEF-02 Correo distingue mayúsculas | Alta | 4 de 4 pruebas fallaban | 4 de 4 pasan |
| DEF-03 Prueba intermitente de horarios | Media | 4 de 10 ejecuciones con errores | 10 de 10 limpias |
| DEF-04 Ruta de las pruebas E2E | Baja | Revisión de la configuración | Pendiente de verificar con `pnpm test:e2e` |

## 6. Análisis

**Lo más importante:** DEF-01 dejó al descubierto que 4 pruebas pasaban por la razón equivocada.
- El usuario no llegaba a crearse, o el token se enviaba por un canal que la API ya no leía.
- Igual obtenían el 401 que esperaban.
- Por eso un 66 % de éxito escondía que la autenticación no se estaba probando de verdad.

Desde la corrección, cada prueba de sesión verifica la cookie httponly real.

**Defecto de producto:** DEF-02 era un error real del sistema, no de las pruebas. Se encontró con casos negativos (escribir el mismo correo con otras mayúsculas) que no estaban en la suite.

**Proceso:**
- Ninguna prueba se ejecutaba de forma rutinaria después de cada cambio, y por eso DEF-01 pasó inadvertido desde el cambio a cookie (commit `7f4b4cf`) hasta esta ejecución.
- Acción: ejecutar `pytest` y `ruff check .` antes de cada merge a `development`. Queda como deuda técnica automatizarlo con GitHub Actions.

## 7. Ejecuciones locales pendientes

Completar en el equipo del desarrollador y adjuntar las capturas en `evidencias/`.

| Prueba | Comando | Resultado | Fecha |
|---|---|---|---|
| Colección de Postman (Runner) | Collection Runner → "SIHS API - Pruebas" | | |
| E2E Playwright | `pnpm test:e2e` | | |
| ESLint del frontend | `pnpm lint` | | |
| Suite del backend en Windows | `pytest --cov` | | |

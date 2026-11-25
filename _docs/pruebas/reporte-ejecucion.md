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
| Linter del frontend (ESLint) | 3 errores | **0 errores** |
| Defectos abiertos | 4 | 0 de severidad Alta o Media |

Evidencias: `evidencias/01_ejecucion1_suite_antes.txt` y `evidencias/06_ejecucion2_suite_despues.txt`.

## 3. Resultados por nivel (Ejecución 2)

| Nivel | Pruebas | Resultado |
|---|---|---|
| Unitarias (`tests/unit`) | 54 | 54 pasaron |
| Integración (`tests/integration`) | 75 | 75 pasaron |
| API: colección de Postman | 29 peticiones / 48 tests | 29 de 29 respuestas esperadas en el runner de verificación*. En Postman: 44 de 44 tests (sección 7) |
| E2E (Playwright) | 2 | 2 de 2 en el equipo local, después de corregir DEF-05 (sección 7) |

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
| DEF-04 Ruta de las pruebas E2E | Baja | Revisión de la configuración | `pnpm test:e2e` encuentra `E2E/` y ejecuta las 2 pruebas (`12_e2e_despues.png`) |
| DEF-05 Prueba E2E de fichas con el rol coordinador | Media | Ejecución local: 0 de 2 (`11_e2e_antes.png`) | 2 de 2 (`12_e2e_despues.png`) |

## 6. Análisis

**Lo más importante:** DEF-01 dejó al descubierto que 4 pruebas pasaban por la razón equivocada.
- El usuario no llegaba a crearse, o el token se enviaba por un canal que la API ya no leía.
- Igual obtenían el 401 que esperaban.
- Por eso un 66 % de éxito escondía que la autenticación no se estaba probando de verdad.

Desde la corrección, cada prueba de sesión verifica la cookie httponly real.

**Defecto de producto:** DEF-02 era un error real del sistema, no de las pruebas. Se encontró con casos negativos (escribir el mismo correo con otras mayúsculas) que no estaban en la suite.

**Proceso:**
- Ninguna prueba se ejecutaba de forma rutinaria después de cada cambio, y por eso DEF-01 pasó inadvertido desde el cambio a cookie hasta esta ejecución.
- Acción: ejecutar `pytest` y `ruff check .` antes de cada merge a `development`. Queda como deuda técnica automatizarlo con GitHub Actions.

## 7. Ejecuciones locales (equipo del desarrollador, Windows)

| Prueba | Comando | Resultado | Fecha |
|---|---|---|---|
| Colección de Postman (Runner) | Collection Runner → "SIHS API - Pruebas" | 44 de 44 tests, 0 errores (`10_postman_runner.png`). La carpeta 7 (admin, 4 tests) se omitió porque la cuenta de admin aún no existía | 2026-11-25 |
| E2E Playwright | `pnpm test:e2e` | Ejec. 1: 0 de 2, se detectó DEF-05 (`11_e2e_antes.png`). Ejec. 2: 2 de 2 (`12_e2e_despues.png`) | 2026-11-25 |
| ESLint del frontend | `pnpm lint` | Ejec. 1: 3 errores (`13_eslint.txt`). Corregidos en el commit `fix(lint)`. Ejec. 2: 0 errores (`14_eslint_despues.txt`) | 2026-11-25 |
| Suite del backend en Windows | `pytest --cov` | 129 passed, cobertura total 87 % (`09_pytest_windows.txt`) | 2026-11-25 |

**Hallazgos de análisis estático (ESLint):**

| Regla | Archivo | Problema | Corrección |
|---|---|---|---|
| `react-refresh/only-export-components` | `src/context/AuthContext.tsx` | El archivo exportaba el componente `AuthProvider` y el hook `useAuthContext`; con esa mezcla, Vite recarga toda la página en vez de conservar el estado | El contexto pasó a `context/auth.context.ts` y el hook a `hooks/useAuth.ts`. `AuthContext.tsx` exporta solo el componente |
| `react-hooks/set-state-in-effect` | `src/pages/Horarios/Horarios.tsx` | El efecto activaba `loading` y limpiaba el error de forma síncrona, lo que provoca un render extra en cascada | El efecto solo cambia el estado cuando llega la respuesta. "Cargando" se calcula en el render, y después de guardar se usa `recargarGrilla()` desde el evento |
| `react-hooks/set-state-in-effect` | `src/pages/ResetPassword/ResetPassword.tsx` | Sin token, el efecto asignaba el estado "enlace incompleto" | Ese estado se calcula en el render (`estadoActual`); el efecto solo corre cuando hay token que validar |

Estos hallazgos no se registraron como defectos (issues) porque no los ve el usuario final: son problemas de calidad del código detectados por el linter, y se corrigieron en el mismo ciclo detectar → corregir → verificar.

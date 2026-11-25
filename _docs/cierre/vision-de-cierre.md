# Visión de cierre — T6

**Proyecto:** SIHS, Sistema de Información de Horarios · **Desarrollador:** Angel Gómez (equipo de una persona) · **Fecha:** noviembre de 2026

## Propósito del sistema

Que un centro de formación arme los horarios de sus fichas sin choques y que cada persona consulte lo que le corresponde:
- **Administrador:** gestiona todo, incluido el reparto de ambientes entre coordinaciones.
- **Coordinador:** programa los horarios de su coordinación con sus propios ambientes.
- **Instructores y aprendices:** consultan su horario y su programa.

El fuerte previsto del sistema es la **gestión de datos y las cargas masivas**.

## Qué queda terminado en T6

| Área | Entregado | Evidencia |
|---|---|---|
| Modelo de datos | 18 tablas con reglas de integridad en la BD: anti-choque, modalidad/ambiente, trigger de validación y ambiente por coordinación | `backend/alembic/versions/`, `_docs/arquitectura/` |
| Backend | API REST FastAPI por capas: 14 recursos académicos con CRUD, gestión de usuarios, autenticación con cookie httponly, 5 roles, alcance por coordinación y recuperación de contraseña | `backend/`, Swagger en `/docs` |
| Frontend | SPA React: dashboard por rol, CRUD de gestión, grilla de horarios, vistas personales y recuperación de contraseña | `frontend/` |
| Pruebas | 129 automatizadas (unitarias e integración), colección de Postman con 48 tests y 2 E2E con Playwright. Cobertura del 87 % (90 % en el módulo crítico) | `_docs/pruebas/` |
| Calidad | ruff sin errores, 4 defectos registrados y corregidos con su ciclo completo | `_docs/pruebas/defectos.md` |
| Datos de prueba | Seed idempotente con 30 registros por entidad | `backend/scripts/seed_horarios.py` |

## Qué no quedó terminado y pasa a T7

Lo honesto es separar lo que funciona de lo que falta.

| Pendiente | Estado real hoy | Por qué no entró en T6 |
|---|---|---|
| **Carga masiva de horarios** (CSV/Excel desde la API) | Existe como prototipo SQL (`db_horarios/03_carga_masiva.sql`), no como endpoint ni pantalla | Primero había que estabilizar el modelo, los roles y las reglas anti-choque, porque la carga masiva depende de ellos |
| Exportar el horario a PDF | No iniciado | Prioridad menor que las reglas de negocio |
| Despliegue | Solo ambiente local | Falta parametrizar la cookie `secure`, CORS y los secretos (ver deuda técnica) |
| Integración continua | Las pruebas se ejecutan a mano | Se documentó el proceso manual; la automatización con GitHub Actions es el siguiente paso |
| Funciones propias del instructor | Hoy solo consulta, igual que el aprendiz | Decisión de alcance: se ampliará en T7 |
| Pruebas del frontend | 2 pruebas E2E; sin pruebas unitarias de componentes | El esfuerzo de pruebas se concentró en el backend, donde están las reglas críticas |

## Criterio de "terminado" usado en T6

Una funcionalidad se considera terminada cuando cumple las cuatro condiciones:

1. Tiene endpoint documentado en Swagger y la pantalla del rol que la usa.
2. Tiene pruebas automatizadas de casos positivos y negativos.
3. Pasa `pytest` y `ruff check .` sin errores.
4. Está fusionada en `main`.

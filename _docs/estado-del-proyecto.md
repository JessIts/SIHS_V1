# Estado del proyecto — SIHS

**Corte:** 25 de noviembre de 2026 · **Rama:** `main`

## Resumen

| Alcance | Avance |
|---|---|
| **Funcionalidades principales** (lo que el sistema hace hoy) | **≈ 93 %** |
| **Sistema completo** (incluye lo que pasa a T7) | **≈ 78 %** |

Las funcionalidades principales están construidas, conectadas de punta a punta (base de datos → API → interfaz) y probadas. El trabajo que falta en ellas es de **pulido**: experiencia de uso, mensajes, casos borde y algunas pruebas. La diferencia con el sistema completo se debe sobre todo a la **carga masiva de horarios**, que es el fuerte previsto del sistema y hoy existe solo como prototipo SQL.

## Cómo se calculó

- Cada módulo tiene un **peso** según su importancia para el propósito del sistema.
- El **avance** de cada módulo se mide contra lo que hace falta para darlo por terminado:
  - funciona en la API y en la pantalla del rol que lo usa,
  - tiene pruebas,
  - pasa los linters,
  - está en `main`.
- El total es la suma de peso × avance.

Es una **estimación del desarrollador**, apoyada en las evidencias de `_docs/pruebas/`. No es una medición automática.

## Avance por módulo

### Funcionalidades principales (80 % del peso total)

| Módulo | Peso | Avance | Qué está hecho | Qué falta pulir |
|---|---|---|---|---|
| Modelo de datos y reglas en la BD | 15 % | 100 % | 18 tablas, constraints anti-choque, trigger `fn_validar_horario`, ambiente por coordinación y migraciones | — |
| Autenticación, roles y permisos | 15 % | 95 % | Login con cookie `httponly`, 5 roles, alcance por coordinación y recuperación de contraseña | Sesión de 5 minutos sin renovación (DT-04) y límite de intentos (DT-05) |
| Gestión de información (CRUD) | 20 % | 95 % | 14 entidades académicas y usuarios, con paginación, filtros y borrado lógico, en la API y en pantalla | Búsqueda en las tablas y aviso de usuarios pendientes de rol (DT-08) |
| Programación de horarios | 20 % | 90 % | Registro, edición y eliminación de clases, validación anti-choque en la API y en la BD, y grilla visual por ficha | Experiencia en la grilla (mensajes de choque más claros) y pruebas E2E del flujo de horarios |
| Paneles y vistas personales | 10 % | 85 % | Dashboard por rol, "Mi programa" y "Mi horario" | Funciones propias del instructor (hoy solo consulta, igual que el aprendiz) |

**Subtotal:** 74,75 de 80 puntos, es decir **≈ 93 %** de las funcionalidades principales.

### Pendiente para completar el sistema (20 % del peso total)

| Módulo | Peso | Avance | Estado |
|---|---|---|---|
| Carga masiva de horarios (CSV/Excel) | 10 % | 20 % | Prototipo SQL en `db_horarios/03_carga_masiva.sql`. Falta el endpoint, la pantalla y el reporte de errores por fila (DT-02) |
| Exportar horarios a PDF | 5 % | 0 % | No iniciado |
| Despliegue e integración continua | 5 % | 30 % | Contenedores listos: `docker-compose.yml` con PostgreSQL de desarrollo y de pruebas, y el `Dockerfile` de la API. Falta parametrizar cookie, CORS y URL de la API (DT-03), sacar los secretos del compose (DT-12) y configurar GitHub Actions (DT-01) |

**Total del sistema:** 74,75 + 3,5 = 78,25 de 100 puntos, es decir **≈ 78 %**.

## Calidad alcanzada

La calidad no suma puntos aparte, pero respalda los porcentajes anteriores:

| Indicador | Resultado |
|---|---|
| Pruebas del backend (unitarias e integración) | 129 de 129, estables en 10 ejecuciones seguidas |
| Cobertura | 87 % total; 90 % en el servicio de horarios |
| API (Postman) | 44 de 44 tests |
| E2E (Playwright) | 2 de 2 |
| Linters | ruff: 0 errores · ESLint: 0 errores |
| Defectos | 5 detectados, 5 corregidos y verificados |

## Próximos pasos (T7), en orden de prioridad

1. **Carga masiva de horarios** desde la API y la interfaz, reutilizando las validaciones de `HorarioService`.
2. **Integración continua** con GitHub Actions: pytest, ruff, ESLint y E2E en cada pull request.
3. **Preparar el despliegue:** variables de entorno para la cookie, CORS y la URL de la API.
4. **Exportar horarios a PDF.**
5. **Pulido:**
   - funciones propias del instructor,
   - renovación de la sesión,
   - búsqueda en las tablas,
   - pruebas del frontend.

Detalle de cada punto en [`cierre/deuda-tecnica.md`](cierre/deuda-tecnica.md) y [`cierre/vision-de-cierre.md`](cierre/vision-de-cierre.md).

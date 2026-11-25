# Deuda técnica — SIHS (cierre T6)

**Prioridad:**
- **Alta:** bloquea el despliegue o deja un riesgo de seguridad o de datos.
- **Media:** afecta la calidad o la experiencia, pero hay forma de seguir.
- **Baja:** mejora deseable.

**Esfuerzo:** S (horas) · M (1–2 días) · L (una semana o más).

| ID | Deuda | Impacto si no se atiende | Prioridad | Esfuerzo | Plan |
|---|---|---|---|---|---|
| DT-01 | Sin integración continua: las pruebas y el linter se ejecutan a mano | Una regresión como DEF-01 puede volver a pasar inadvertida | Alta | S | GitHub Actions: PostgreSQL de servicio, `pytest --cov` y `ruff check .` en cada pull request |
| DT-02 | Carga masiva de horarios solo como prototipo SQL | Es la funcionalidad central prevista del sistema y no está disponible en la API | Alta | L | Endpoint `POST /horarios/carga-masiva` (CSV/Excel) que reutilice las validaciones de `HorarioService` y devuelva un reporte fila por fila |
| DT-03 | Cookie con `secure=False` fija y CORS limitado a `localhost:5173` en el código | No se puede desplegar con HTTPS ni con otro dominio sin tocar código | Alta | S | Mover `COOKIE_SECURE` y `CORS_ORIGINS` a la configuración (`.env`) |
| DT-04 | La sesión dura 5 minutos y no se renueva | El usuario pierde la sesión mientras trabaja en la grilla | Media | M | Ampliar la duración por configuración o agregar renovación (refresh) al hacer peticiones |
| DT-05 | Sin límite de intentos en el login y en la recuperación de contraseña | Exposición a fuerza bruta y a envío masivo de correos | Media | M | Limitar por IP y por correo (por ejemplo, con `slowapi`) |
| DT-06 | Unicidad del correo garantizada por la aplicación, no por la BD | Una inserción por fuera de la API podría duplicar cuentas que solo difieren en mayúsculas | Media | S | Índice único sobre `lower(email)`, después de unificar duplicados si existieran |
| DT-07 | Frontend sin pruebas unitarias; solo 2 pruebas E2E | Los cambios en componentes compartidos (`CrudPage`, `HorarioGrid`) no tienen protección | Media | M | Vitest + Testing Library para los componentes compartidos, y E2E de la grilla de horarios |
| DT-08 | El usuario del registro público queda con rol `user` hasta que el admin lo cambie, sin aviso | Nuevos usuarios que no ven nada útil y un admin que no se entera | Baja | M | Listado de "pendientes de rol" en el dashboard del admin |
| DT-09 | El correo se envía en segundo plano dentro del mismo proceso, sin reintentos | Si el SMTP falla, el enlace se pierde (queda solo en el log) | Baja | M | Cola de tareas con reintentos, o un proveedor de correo con API |
| DT-11 | La migración `d8f3b61e9a42` no se puede revertir | Un `downgrade` no recupera cómo estaba escrito cada correo | Baja | — | Aceptada: la normalización es irreversible por naturaleza |
| DT-12 | Usuario y contraseña de PostgreSQL escritos en `docker-compose.yml` | Válido solo para desarrollo local; en un servidor quedarían expuestos en el repositorio | Media | S | Leerlos de un `.env` en la raíz (`${POSTGRES_PASSWORD}`) que no se suba a Git, con un `.env.example` de referencia |

## Deuda pagada en T6

| Deuda | Cómo se resolvió |
|---|---|
| Suite de autenticación rota tras el cambio a cookie (DEF-01) | Pruebas actualizadas al mecanismo real de sesión |
| Correos que distinguían mayúsculas (DEF-02) | `NormalizedEmail`, búsqueda sin distinguir mayúsculas y migración de datos |
| Prueba intermitente de horarios (DEF-03) | Trimestres únicos por escenario |
| Sin linter en el backend | ruff configurado, 0 errores (incluye las referencias de modelos con `TYPE_CHECKING`) |
| Sin medición de cobertura | pytest-cov configurado en `pyproject.toml` |
| `requirements.txt` en UTF-16 (generado con `pip freeze >` en PowerShell) | Convertido a UTF-8, más `requirements-dev.txt` |
| `JWT_SECRET_KEY` sin guía de longitud en `.env.example` | Comentario con el mínimo de 32 caracteres y el comando para generar una clave |
| 3 errores de ESLint en el frontend (Fast Refresh en `AuthContext.tsx` y `setState` dentro de efectos en `Horarios.tsx` y `ResetPassword.tsx`) | Corregidos: contexto y hook en archivos separados, y estados de carga calculados en el render. `pnpm lint` queda en 0 errores |
| Prueba E2E de fichas desactualizada tras el cambio de roles (DEF-05) | Sesión de admin y verificación por API, que no depende de la paginación de la tabla |
| `frontend/README.md` desactualizado (describía solo el login) (antes DT-10) | Reescrito con stack, instalación, scripts, pantallas por rol y estructura |

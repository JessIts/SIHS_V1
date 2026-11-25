# SISTEMA SIHS

Sistema de gestión de horarios para fichas de formación: programación de clases por trimestre, día y franja, con control de cruces de instructor, ambiente y ficha.

## Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Backend** | Python · FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · Uvicorn |
| **Base de datos** | PostgreSQL (psycopg 3) · triggers y constraints para reglas de negocio |
| **Autenticación** | JWT (PyJWT) en cookie `httponly` · Argon2 para contraseñas |
| **Frontend** | React 19 · TypeScript 6 · Vite 8 · React Router 7 · CSS por componente (BEM) |
| **Pruebas y calidad** | pytest · pytest-cov · Postman · Playwright · ruff · ESLint |
| **Gestores** | pip + venv (backend) · pnpm (frontend) |

## Estructura

```
SISTEMA SIHS/
├── backend/       API REST (routes → controllers → services → repositories)
├── frontend/      SPA en React con dashboards por rol
├── db_horarios/   Prototipo SQL del modelo de horarios y carga masiva por CSV
└── _docs/
    ├── arquitectura/  Diagramas del sistema, capas, modelo de datos y flujos
    ├── pruebas/       Plan, matriz de casos, defectos, reporte, evidencias y colección de Postman
    └── cierre/        Visión de cierre T6, retrospectivas, deuda técnica y reflexión de backends
```

## Progreso actual

### Hecho
- **Modelo de datos relacional**: sedes, ambientes, coordinaciones, programas, competencias, resultados y actividades de aprendizaje, jornadas, franjas, días, trimestres, fichas, ficha-trimestre y horarios.
- **Reglas en BD**: sin cruces de ficha, instructor ni ambiente en la misma franja. La modalidad sincrónica no lleva ambiente. Validación con el trigger `fn_validar_horario`.
- **Backend**:
  - CRUD completo de todas las entidades, con UUID como identificador público, paginación, filtros y borrado lógico.
  - Grilla y calendario de horario por ficha-trimestre.
  - Endpoints personales (`/mi/*`) y resumen para el dashboard.
  - Todo documentado en Swagger.
- **Roles y permisos**:
  - `admin`: acceso completo; registra y modifica todo (usuarios, catálogos, fichas, ambientes, horarios).
  - `coordinador`: solo registra horarios de las fichas de su coordinación, usando los ambientes asignados a ella; el resto lo consulta.
  - `instructor` y `aprendiz`: consultan su información y la de su programa, y editan sus datos básicos.
- **Ambientes por coordinación**: el admin reparte los ambientes de cada sede entre las coordinaciones; una coordinación no puede usar los ambientes de otra (validado en la API y en la BD).
- **Frontend**:
  - Login y registro.
  - Dashboard distinto por rol.
  - Vistas CRUD para las 14 entidades académicas.
  - Gestión de usuarios y roles.
  - Grilla visual de horario, y vistas "Mi programa" y "Mi horario".
- **Recuperación de contraseña**: enlace de un solo uso que vence en 30 minutos, con envío por SMTP.
- **Datos de prueba**: el script `seed_horarios` carga 30 registros por entidad, un coordinador con su coordinación y la ficha 3141665 con su horario real.

### Pendiente (T7)
- Carga masiva de horarios desde la API (CSV/Excel), hoy disponible solo en el prototipo SQL (`db_horarios/03_carga_masiva.sql`).
- Exportar horarios a PDF.
- Integración continua y despliegue.

Detalle en [`_docs/cierre/vision-de-cierre.md`](_docs/cierre/vision-de-cierre.md) y [`_docs/cierre/deuda-tecnica.md`](_docs/cierre/deuda-tecnica.md).

## Pruebas

| Nivel | Cantidad | Herramienta | Cómo ejecutarlas |
|---|---|---|---|
| Unitarias | 54 | pytest | `cd backend && pytest tests/unit` |
| Integración (API + PostgreSQL) | 75 | pytest + TestClient | `cd backend && pytest tests/integration` |
| API | 29 peticiones / 48 tests | Postman | Importar `_docs/pruebas/postman/` y ejecutar el Collection Runner |
| E2E | 2 | Playwright (Chrome) | `cd frontend && pnpm test:e2e` |

- **Último resultado:** 129/129 pruebas del backend, estables en 10 ejecuciones seguidas.
- **Cobertura:** 87 % en total; 90 % en el módulo crítico de horarios (`pytest --cov`).
- **Linter:** `ruff check .` sin errores en el backend; `pnpm lint` en el frontend.
- **Ambiente separado:** las pruebas usan la base `sihs_test`, nunca la de desarrollo.

| Documento | Contenido |
|---|---|
| [Plan de pruebas](_docs/pruebas/plan-de-pruebas.md) | Alcance, niveles, ambientes y criterios |
| [Matriz de casos](_docs/pruebas/matriz-casos-de-prueba.md) | 29 casos positivos y negativos con datos, pasos y resultados |
| [Registro de defectos](_docs/pruebas/defectos.md) | 4 defectos con severidad, estado y ciclo detectar → corregir → verificar |
| [Reporte de ejecución](_docs/pruebas/reporte-ejecucion.md) | Ejecución antes y después de las correcciones, y cobertura |


## Ejecución local

**Backend** (guía completa y documentación de la API en [`backend/README.md`](backend/README.md))
```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows (Git Bash)
pip install -r requirements-dev.txt
cp .env.example .env                                    # configurar DATABASE_URL y JWT_SECRET_KEY
alembic upgrade head
python -m scripts.seed_horarios                         # opcional: datos de ejemplo
uvicorn app.main:app --reload                           # Swagger en http://localhost:8000/docs
```

**Frontend**
```bash
cd frontend
pnpm install
pnpm dev                                                # http://localhost:5173
```

**Crear un administrador:** registra un usuario y promuévelo.
```bash
python -m scripts.create_admin correo@ejemplo.com
```

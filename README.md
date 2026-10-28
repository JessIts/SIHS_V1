# SISTEMA SIHS

Sistema de gestión de horarios para fichas de formación: programación de clases por trimestre, día y franja, con control de cruces de instructor, ambiente y ficha.

## Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Backend** | Python · FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · Uvicorn |
| **Base de datos** | PostgreSQL (psycopg 3) · triggers y constraints para reglas de negocio |
| **Autenticación** | JWT (PyJWT) en cookie `httponly` · Argon2 para contraseñas |
| **Frontend** | React 19 · TypeScript 6 · Vite 8 · React Router 7 · CSS por componente (BEM) |
| **Pruebas y calidad** | Pytest · ESLint |
| **Gestores** | pip + venv (backend) · pnpm (frontend) |

## Estructura

```
SISTEMA SIHS/
├── backend/       API REST (routes → controllers → services → repositories)
├── frontend/      SPA en React con dashboards por rol
├── db_horarios/   Prototipo SQL del modelo de horarios y carga masiva por CSV
└── _docs/         Scripts y notas de apoyo
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
- **Roles y permisos**: `admin`, `coordinador`, `instructor`, `aprendiz`. Solo admin y coordinador modifican datos académicos; instructores y aprendices ven solo su información y la de su programa.
- **Frontend**:
  - Login y registro.
  - Dashboard distinto por rol.
  - Vistas CRUD para las 14 entidades académicas.
  - Gestión de usuarios y roles.
  - Grilla visual de horario, y vistas "Mi programa" y "Mi horario".
- **Datos de prueba**: el script `seed_horarios` carga la ficha 3141665 con su horario real de ejemplo y usuarios de cada rol.

### Pendiente
- Carga masiva de horarios desde la API (CSV/Excel), hoy disponible solo en el prototipo SQL (`db_horarios/03_carga_masiva.sql`).
- Exportar horarios a PDF.
- Despliegue.

## Ejecución local

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows (Git Bash)
pip install -r requirements.txt
cp .env.example .env                                    # configurar DATABASE_URL
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

**Crear un administrador**
```bash
python -m scripts.create_admin correo@ejemplo.com
```

# SISTEMA SIHS

**Sistema de Información de Horarios** para centros de formación.

## ¿Para qué está diseñado?

Organizar los horarios de las fichas de formación sin choques, y que cada persona consulte lo que le corresponde.

- **Problema que resuelve:** programar a mano las clases de cada ficha por trimestre, día y franja suele generar cruces. Pasa cuando un instructor queda en dos lugares a la vez, un ambiente se asigna dos veces o una ficha tiene dos clases en la misma franja. SIHS **impide esos cruces** desde la API y desde la propia base de datos.
- **Cómo se organiza el trabajo:**
  - **Administrador:** registra la información base (sedes, ambientes, programas, fichas, trimestres y usuarios) y reparte los ambientes entre las coordinaciones.
  - **Coordinador:** programa los horarios de las fichas de su coordinación, usando solo los ambientes asignados a ella.
  - **Instructores y aprendices:** consultan su horario y su programa desde su propio panel.
- **Fuerte previsto:** la gestión de datos y la carga masiva de horarios.

## Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Backend** | Python · FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · Uvicorn |
| **Base de datos** | PostgreSQL 16, con constraints y triggers para las reglas de negocio |
| **Autenticación** | JWT en cookie `httponly` · contraseñas con Argon2 |
| **Frontend** | React 19 · TypeScript · Vite · React Router 7 · CSS por componente |
| **Pruebas y calidad** | pytest · pytest-cov · Postman · Playwright · ruff · ESLint |

Instalación y detalle de cada parte:
- [`backend/README.md`](backend/README.md): API, instalación, variables de entorno y endpoints.
- [`frontend/README.md`](frontend/README.md): interfaz web, instalación y pantallas por rol.

## Estructura

```
SISTEMA SIHS/
├── backend/       API REST por capas (routes → controllers → services → repositories)
├── frontend/      Aplicación web en React con un panel por rol
├── db_horarios/   Prototipo SQL del modelo y de la carga masiva por CSV
└── _docs/
    ├── estado-del-proyecto.md  Porcentaje de avance por módulo
    ├── arquitectura/           Diagramas del sistema, capas, modelo de datos y flujos
    ├── pruebas/                Plan, matriz de casos, defectos, reporte, evidencias y Postman
    └── cierre/                 Visión de cierre, retrospectivas y deuda técnica
```

## Estado del proyecto

Las funcionalidades principales están construidas y probadas. Lo que queda es pulirlas y completar lo que pasa a la siguiente fase. El avance por módulo está en [`_docs/estado-del-proyecto.md`](_docs/estado-del-proyecto.md).

**Funcionando:**
- Autenticación con cookie, 5 roles y recuperación de contraseña.
- Gestión completa de las 14 entidades académicas y de los usuarios.
- Ambientes repartidos por coordinación.
- Programación de horarios con validación anti-choque y grilla visual por ficha.
- Paneles por rol, y las vistas "Mi programa" y "Mi horario".

**Pendiente:**
- Carga masiva de horarios desde la aplicación (hoy existe solo como prototipo SQL).
- Exportar horarios a PDF.
- Despliegue e integración continua.

## Pruebas

| Nivel | Resultado | Herramienta |
|---|---|---|
| Unitarias e integración del backend | 129 de 129 · cobertura del 87 % (90 % en horarios) | pytest |
| API | 44 de 44 tests de la colección (sin la carpeta opcional de admin) | Postman |
| E2E | 2 de 2 | Playwright |
| Linters | 0 errores | ruff · ESLint |

En las pruebas se detectaron 5 defectos, y todos se corrigieron y verificaron. El detalle está en [`_docs/pruebas/`](_docs/pruebas/).

## Inicio rápido

```bash
# Backend: http://localhost:8000/docs
cd backend
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements-dev.txt
cp .env.example .env            # configurar DATABASE_URL y JWT_SECRET_KEY
alembic upgrade head
python -m scripts.seed_horarios
uvicorn app.main:app --reload

# Frontend: http://localhost:5173 (en otra terminal)
cd frontend
pnpm install
pnpm dev
```

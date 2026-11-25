# Arquitectura de SIHS

Actualizado al cierre de T6 (noviembre de 2026). GitHub dibuja los diagramas Mermaid de este archivo.

## 1. Vista general del sistema

```mermaid
flowchart LR
    subgraph Cliente["Navegador"]
        SPA["Frontend SPA<br/>React 19 + TypeScript + Vite<br/>React Router · CSS por componente"]
    end

    subgraph Servidor["Backend · FastAPI (Python)"]
        API["API REST /api/v1<br/>Routes → Controllers → Services → Repositories"]
        AUTH["Sesión JWT en cookie httponly<br/>Roles y alcance por coordinación"]
        MAIL["Envío de correo<br/>(SMTP o consola en desarrollo)"]
    end

    DB[("PostgreSQL 16<br/>constraints + trigger<br/>fn_validar_horario")]
    SMTP["Servidor SMTP"]

    SPA -- "HTTPS / JSON<br/>cookie access_token" --> API
    API --- AUTH
    API -- "SQLAlchemy 2 + Alembic" --> DB
    MAIL -. "recuperación de contraseña" .-> SMTP
    API --- MAIL

    subgraph Pruebas["Verificación"]
        PY["pytest<br/>unitarias + integración"]
        PM["Postman<br/>colección con tests"]
        PW["Playwright<br/>E2E en Chrome"]
    end

    PY -. "TestClient" .-> API
    PY -. "sihs_test" .-> DB
    PM -. HTTP .-> API
    PW -. navegador .-> SPA
```

| Componente | Responsabilidad |
|---|---|
| Frontend (`frontend/`) | Interfaz por rol: dashboards, CRUD de gestión, grilla de horarios, "Mi horario", "Mi programa" y recuperación de contraseña. Oculta lo que el rol no puede hacer, pero **la seguridad real está en la API** |
| Backend (`backend/`) | Reglas de negocio, validación de datos, autenticación, permisos por rol y por coordinación |
| PostgreSQL | Integridad: UNIQUE contra choques de horario, CHECK de modalidad y ambiente, FK compuesta ficha-trimestre, y el trigger que exige rol instructor, temática del programa y ambiente de la misma coordinación |
| Prototipo SQL (`db_horarios/`) | Modelo inicial y carga masiva por CSV. Es la base del módulo de carga masiva de T7 |

## 2. Capas del backend

```mermaid
flowchart TB
    R["routes/<br/>endpoint, Depends(sesión, rol, alcance), response_model"]
    C["controllers/<br/>coordina y arma la respuesta"]
    S["services/<br/>reglas de negocio · BaseService (CRUD genérico) · AccessScope"]
    RP["repositories/<br/>consultas · BaseRepository (paginación, borrado lógico)"]
    M["models/<br/>SQLAlchemy"]
    DB[("PostgreSQL")]
    X["core/<br/>config · seguridad · dependencias · excepciones · correo"]
    SC["schemas/<br/>Pydantic: entrada validada y salida"]

    R --> C --> S --> RP --> M --> DB
    R -.-> SC
    S -.-> X
    R -.-> X
```

## 3. Modelo de datos (resumen)

```mermaid
erDiagram
    SEDE ||--o{ AMBIENTE : tiene
    COORDINACION }o--o{ SEDE : "opera en"
    COORDINACION ||--o{ AMBIENTE : "es dueña de"
    COORDINACION ||--o{ PROGRAMA : agrupa
    COORDINACION ||--o{ USER : "gestionada por (coordinador)"
    PROGRAMA ||--o{ COMPETENCIA : tiene
    COMPETENCIA ||--o{ RESULTADO_APRENDIZAJE : tiene
    RESULTADO_APRENDIZAJE ||--o{ ACTIVIDAD_APRENDIZAJE : tiene
    PROGRAMA ||--o{ FICHA : tiene
    JORNADA ||--o{ FICHA : "en"
    JORNADA ||--o{ FRANJA_HORARIA : divide
    FICHA }o--o{ USER : "aprendices"
    FICHA ||--o{ FICHA_TRIMESTRE : "programada en"
    TRIMESTRE ||--o{ FICHA_TRIMESTRE : contiene
    FICHA_TRIMESTRE ||--o{ HORARIO : "casillas"
    DIA_SEMANA ||--o{ HORARIO : "día"
    FRANJA_HORARIA ||--o{ HORARIO : "franja"
    RESULTADO_APRENDIZAJE ||--o{ HORARIO : "temática"
    USER ||--o{ HORARIO : "instructor"
    AMBIENTE ||--o{ HORARIO : "lugar (presencial)"
    USER ||--o{ PASSWORD_RESET_TOKEN : solicita
```

Una **casilla de horario** se identifica por ficha-trimestre × día × franja. Tres restricciones UNIQUE impiden los choques:
- `(ficha-trimestre, día, franja)`
- `(trimestre, día, franja, instructor)`
- `(trimestre, día, franja, ambiente)`

## 4. Flujo: un coordinador programa una clase

```mermaid
sequenceDiagram
    actor Co as Coordinador
    participant FE as Frontend
    participant API as horario_routes
    participant Dep as get_access_scope
    participant Sv as HorarioService
    participant BD as PostgreSQL

    Co->>FE: Clic en una casilla vacía de la grilla
    FE->>API: POST /api/v1/horarios (cookie access_token)
    API->>Dep: valida JWT, rol y coordinación del usuario
    Dep-->>API: AccessScope(coordinacion_id)
    API->>Sv: create(datos, alcance)
    Sv->>Sv: ¿la ficha es de su coordinación? (si no, 403)
    Sv->>Sv: ¿el ambiente es de su coordinación? (si no, 403)
    Sv->>Sv: modalidad, temática del programa, rol instructor (si no, 422)
    Sv->>BD: ¿choque de ficha, instructor o ambiente? (si sí, 409)
    Sv->>BD: INSERT horario
    BD->>BD: trigger fn_validar_horario + UNIQUE (última barrera)
    BD-->>Sv: OK
    Sv-->>API: casilla creada
    API-->>FE: 201 { success, message, data }
    FE-->>Co: La clase aparece en la grilla
```

## 5. Decisiones de arquitectura

| Decisión | Motivo |
|---|---|
| JWT en cookie **httponly** en vez de `Authorization: Bearer` desde el frontend | JavaScript no puede leer el token, lo que mitiga el robo por XSS. El navegador lo envía solo |
| UUID público + `id` entero interno | Las URLs no exponen el orden ni la cantidad de registros, y los joins internos siguen siendo rápidos |
| Reglas de horario en el servicio **y** en la BD | El servicio devuelve mensajes claros; la BD protege aunque alguien inserte por fuera de la API (seed, SQL manual) |
| `AccessScope` en `BaseService` | Un solo punto aplica el filtro por coordinación a todas las lecturas, sin repetirlo en cada endpoint |
| Borrado lógico (`is_active`) en catálogos y borrado físico en horarios | Los catálogos tienen historial; una casilla de horario eliminada debe liberar el espacio |
| Correos en minúsculas (`NormalizedEmail`) | Una persona tiene una sola cuenta, sin importar cómo escriba su correo (DEF-02) |

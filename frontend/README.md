# SISTEMA SIHS — Frontend

Interfaz web del **Sistema de Información de Horarios (SIHS)**. Cada rol entra a su propio panel:
- el administrador gestiona toda la información,
- el coordinador programa los horarios de su coordinación,
- instructores y aprendices consultan su programa y su horario.

Consume la API del backend (`../backend`). La sesión viaja en una cookie `httponly`, así que el frontend nunca guarda el token.

---

## Stack tecnológico

| Uso | Herramienta | Versión |
|---|---|---|
| Librería de interfaz | React | 19.2 |
| Lenguaje | TypeScript | 6.0 |
| Empaquetador y servidor de desarrollo | Vite (`@vitejs/plugin-react`) | 8.2 |
| Navegación | React Router (`react-router-dom`) | 7.18 |
| Estilos | CSS por componente, con variables globales en `src/styles/` | — |
| Comunicación con la API | `fetch` con `credentials: 'include'` (`src/services/api.ts`) | — |
| Pruebas E2E | Playwright, sobre Google Chrome | 1.64 |
| Linter | ESLint, con las reglas de React Hooks y React Refresh | 10.9 |
| Gestor de paquetes | pnpm | — |

Las versiones exactas están en `package.json`.

---

## Instalación

### Requisitos

- **Node.js 20.19 o superior** (recomendado 22 LTS). Compruébalo con `node --version`.
- **pnpm.** Si no lo tienes, instálalo con `npm install -g pnpm`.
- **El backend corriendo** en `http://localhost:8000`. Ver [`../backend/README.md`](../backend/README.md).

### Pasos

Todos los comandos se ejecutan dentro de la carpeta `frontend`.

**1. Instalar las dependencias**

```bash
pnpm install
```

**2. Iniciar el servidor de desarrollo**

```bash
pnpm dev
```

**3. Abrir la aplicación en `http://localhost:5173`**

Usa `localhost`, no `127.0.0.1`. El backend solo acepta peticiones (CORS) desde `http://localhost:5173`, y la cookie de sesión depende del nombre del host.

**4. Iniciar sesión.** Si cargaste el seed del backend, puedes usar estas cuentas:

| Rol | Correo | Contraseña |
|---|---|---|
| Coordinador | `coordinacion.mercadeo@example.com` | `Coordinador123*` |
| Instructor | `carlos.perez@example.com` | `Instructor123*` |
| Aprendiz | `sofia.martinez@example.com` | `Aprendiz123*` |

Para el administrador, registra una cuenta en `/register` y promuévela desde el backend con `python -m scripts.create_admin tu_correo@example.com`.

### Scripts

| Comando | Qué hace |
|---|---|
| `pnpm dev` | Servidor de desarrollo con recarga en caliente |
| `pnpm build` | Revisa los tipos (`tsc -b`) y genera la versión de producción en `dist/` |
| `pnpm preview` | Sirve localmente la versión de `dist/` |
| `pnpm lint` | Ejecuta ESLint (hoy 0 errores) |
| `pnpm test:e2e` | Ejecuta las pruebas E2E con Playwright |
| `pnpm test:e2e:ui` | Abre Playwright en modo visual para depurar |

### Pruebas E2E

La primera vez instala el navegador de Playwright con `pnpm exec playwright install`. Las pruebas usan el canal `chrome`, así que también necesitas Google Chrome instalado.

Antes de ejecutarlas, deja preparado lo siguiente:
- El backend corriendo, con el seed cargado.
- La cuenta de admin `admin.sihs@example.com` (contraseña `Admin123*`) registrada y promovida.

Playwright levanta el frontend solo, o reutiliza el que ya tengas abierto con `pnpm dev`. Para ver el último reporte, usa `pnpm exec playwright show-report`.

---

## Pantallas por rol

| Rol | Pantallas |
|---|---|
| Todos | Login, registro, recuperar y restablecer contraseña, perfil |
| Administrador | Dashboard, usuarios y roles, y gestión de sedes, ambientes, coordinaciones, programas, competencias, resultados, actividades, jornadas, franjas, días, trimestres, fichas, fichas por trimestre y horarios |
| Coordinador | Dashboard de su coordinación y registro de horarios. Fichas, fichas por trimestre y ambientes son solo de consulta |
| Instructor | Dashboard, "Mi programa" y "Mi horario" (consulta) |
| Aprendiz | Dashboard, "Mi programa" y "Mi horario" (consulta) |

Las rutas se protegen por rol en `src/app/routes.tsx` (`ProtectedRoute`). Los botones de crear, editar y desactivar se muestran según `usePermissions`. El backend vuelve a validar cada permiso.

---

## Estructura de carpetas

```text
frontend/
├── E2E/                  Pruebas de Playwright (fichas.spec.ts, helpers.ts)
├── src/
│   ├── app/              App, rutas y protección por rol
│   ├── components/
│   │   ├── common/       Header, Sidebar, PageHeader, ProtectedRoute…
│   │   ├── crud/         CrudPage y EntityForm: base de todas las pantallas de gestión
│   │   ├── dashboard/    Tarjetas y tablas de los paneles
│   │   ├── horario/      Grilla de horario por ficha
│   │   ├── mi/           Vistas personales
│   │   └── ui/           Button, Input, Modal
│   ├── context/          Sesión del usuario (AuthProvider)
│   ├── hooks/            useAuth, usePermissions
│   ├── layouts/          AuthLayout y DashboardLayout
│   ├── pages/            Una carpeta por pantalla (componente + CSS)
│   ├── services/         Llamadas a la API por módulo
│   ├── styles/           Reset, variables y estilos globales
│   ├── types/            Tipos de TypeScript que reflejan los schemas de la API
│   └── utils/            Formatos, etiquetas, navegación y opciones de formularios
├── eslint.config.js
├── playwright.config.ts
└── vite.config.ts
```

**Convenciones:**
- Cada componente o página tiene su carpeta, con su `.tsx` y su `.css`.
- Las pantallas de gestión se construyen sobre `CrudPage`: solo definen columnas, campos y servicio.
- Toda petición pasa por `apiRequest`, que envía la cookie y convierte los errores de la API en mensajes.

---

## Limitaciones conocidas

- La URL de la API está fija en `src/services/api.ts` (`http://localhost:8000/api/v1`). Para desplegar hay que pasarla a una variable de entorno de Vite (`VITE_API_URL`).
- Solo hay pruebas E2E (2). Faltan pruebas unitarias de componentes (deuda técnica DT-07).

# Retrospectivas de sprint — T6

> **Borrador.** Está armado con los hechos verificables del repositorio: commits, defectos y evidencias. Ajusta las opiniones y aprendizajes con tu propia voz antes de presentarlo.

**Formato de cada sprint:**
1. Objetivo y resultado.
2. Qué funcionó.
3. Qué no funcionó.
4. **Reflexión sobre las pruebas.**
5. Acciones para el siguiente sprint.

El proyecto lo desarrolla una sola persona, así que cada retrospectiva es individual.

---

## Sprint 1 — Modelo de horarios y construcción de los módulos

**Periodo:** octubre de 2026.

**Objetivo:** pasar del diagrama entidad-relación inicial a un sistema que arme horarios como el formato real de una ficha (3141665).

**Resultado:**
- Modelo rediseñado y probado primero en una base aparte (`db_horarios/`), con carga masiva por CSV y consultas de prueba.
- Backend con el CRUD de los 14 recursos académicos usando UUID, horarios con reglas anti-choque y grilla por ficha.
- Frontend con un dashboard por rol y vistas CRUD.

### Qué funcionó
- **Probar el modelo en una base aparte antes de tocar la API.** Los errores de diseño se encontraron en SQL, donde corregirlos es barato: la llave compuesta ficha-trimestre, la modalidad sincrónica sin ambiente, las restricciones anti-choque.
- **Reutilizar código.** `BaseService` y `BaseRepository` permitieron crear 14 CRUD con el mismo patrón, sin repetir código.
- **Validar las reglas dos veces.** Ponerlas en el servicio y en la base de datos fue clave: el seed y las pruebas encontraron casos que solo la BD habría atajado.

### Qué no funcionó
- **Se borró trabajo sin querer.** Durante una operación de Git se eliminaron archivos del proyecto. Se recuperaron porque existía el commit "version actual", pero ese mensaje no describía su contenido.
- **Los commits eran grandes y poco descriptivos.** Un solo commit con mucho trabajo es difícil de revisar y de revertir.

### Reflexión sobre las pruebas
- Las 9 pruebas de integración de horarios se escribieron junto con el módulo, recorriendo el flujo completo: catálogos → casillas → choques → grilla. Eso dio confianza en el módulo crítico.
- **Error de proceso:** después de cambiar la sesión a cookie httponly, la suite completa no se volvió a ejecutar. Las pruebas de autenticación y usuarios quedaron desactualizadas sin que nadie lo notara (DEF-01).
- **Aprendizaje:** una prueba que no se ejecuta no protege nada. Y que una prueba pase no significa que valide lo que dice: 4 pasaban por la razón equivocada.

### Acciones para el Sprint 2
- Hacer commits pequeños, con prefijo (`feat`, `fix`, `docs`, `test`), y trabajar en ramas por funcionalidad.
- Escribir pruebas E2E del flujo de interfaz más usado (registro de fichas), siguiendo el patrón AAA.
- Separar la base de datos de pruebas de la de desarrollo.

---

## Sprint 2 — Roles por coordinación, seguridad y proceso de pruebas

**Periodo:** finales de octubre a noviembre de 2026.

**Objetivo:**
- Ajustar los permisos a la realidad del centro: el coordinador solo programa horarios con los ambientes de su coordinación.
- Agregar la recuperación de contraseña.
- Cerrar T6 con un proceso de pruebas documentado.

**Resultado:**
- Ambientes asignados por coordinación, validados en la API y en un trigger de la BD.
- Recuperación de contraseña con un token de un solo uso.
- Seed con 30 registros por entidad.
- Pruebas E2E con Playwright.
- 4 defectos encontrados y corregidos.
- 129 de 129 pruebas pasando, con 87 % de cobertura.

### Qué funcionó
- **Una rama por funcionalidad** (`testing`, `roles`, `feature/recuperar-contrasena`), fusionada en `development` y luego en `main`. El historial muestra qué entró en cada versión.
- **El seed con datos realistas** sirvió a la vez para demos, para Postman y para las pruebas E2E.
- **Documentar los defectos con evidencia** (antes y después) convirtió una suite rota en un proceso verificable.

### Qué no funcionó
- **Choque entre GitHub y la copia local.** Mezclar merges hechos en GitHub (pull requests) con merges locales, sin hacer `git pull` en medio, provocó pushes rechazados y un merge duplicado en el historial.
- **OneDrive y Git.** El proyecto vive en una carpeta sincronizada por OneDrive, que bloqueó archivos al cambiar de rama.
- **El registro de defectos llegó tarde.** Al hacerse al final del trimestre, la Ejecución 1 mostró problemas que llevaban tiempo ahí.

### Reflexión sobre las pruebas
- **Los casos negativos encontraron el defecto real del producto (DEF-02).** Probar el mismo correo con otras mayúsculas reveló cuentas duplicadas y fallas de login. Las pruebas de "camino feliz" nunca lo habrían detectado.
- **Una prueba intermitente (DEF-03) solo se ve ejecutando la suite varias veces.** Desde entonces, el criterio de salida exige 10 ejecuciones limpias seguidas.
- **Medir la cobertura cambió la conversación.** Pasamos de "creo que está probado" a "el servicio de horarios tiene 90 % y sabemos qué líneas faltan".
- **Las pruebas de API (Postman) y las de interfaz (E2E) validan cosas distintas.** Postman prueba el contrato HTTP y los permisos; Playwright prueba que el usuario ve el resultado correcto.

### Acciones para T7
- Automatizar `pytest` y `ruff check .` con GitHub Actions en cada pull request a `development` (ver deuda técnica DT-01).
- Antes de trabajar después de un merge en GitHub, hacer siempre `git pull`.
- Mover el proyecto fuera de OneDrive.
- Escribir la prueba del defecto **antes** de corregirlo, como ya se hizo con DEF-02.

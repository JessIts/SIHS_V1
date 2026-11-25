# Reflexión sobre el backend — SIHS

> **Nota sobre este documento.** La lista de chequeo pide una reflexión comparando los backends construidos durante el programa. En este proyecto hubo **un solo backend**: el de SIHS. Se desarrolló de forma continua desde el inicio, con la misma arquitectura por capas. Por eso esta reflexión no compara proyectos distintos, sino las **etapas por las que pasó el mismo backend**: qué se mantuvo, qué cambió, qué costó y qué se aprendió.

---

## 1. Línea de tiempo

Reconstruida a partir de las migraciones de Alembic (`backend/alembic/versions/`) y del historial de Git.

| Etapa | Fecha | Qué se agregó | Migraciones |
|---|---|---|---|
| 1. Usuarios | Finales de agosto de 2026 | Modelo de usuario con UUID público, documento y datos de contacto | `d29ff6cf90b3`, `4f5c1873669b` |
| 2. Autenticación | Septiembre de 2026 | Contraseñas con Argon2, roles y JWT. Primero con sesión local; después con cookie `httponly` | `466ab2266069` |
| 3. Módulo de horarios | Octubre de 2026 | Sedes, ambientes, estructura académica, calendario, fichas, programación por trimestre y horarios con reglas anti-choque. El modelo se probó primero en una base aparte (`db_horarios/`) | `0656244fbcc0` |
| 4. Roles por coordinación | Noviembre de 2026 | El coordinador solo programa horarios de su coordinación, con los ambientes asignados a ella | `a7c3e91d5b20` |
| 5. Recuperación de contraseña | Noviembre de 2026 | Token de un solo uso, con vencimiento y envío por correo | `c5e2a8f41b37` |
| 6. Cierre de calidad (T6) | Noviembre de 2026 | Pruebas actualizadas, 5 defectos corregidos, normalización de correos, linter y cobertura | `d8f3b61e9a42` |

Cada etapa se construyó **encima** de la anterior, sin reescribir lo que ya existía.

---

## 2. Lo que se mantuvo desde el inicio, y por qué funcionó

**Arquitectura por capas.** La separación routes → controllers → services → repositories → models no cambió en todo el proyecto. Fue la decisión que más rindió:
- Agregar el módulo de horarios (14 recursos) no obligó a tocar la autenticación.
- El cambio de roles se resolvió casi entero en la capa de servicios (`AccessScope` + `BaseService`), sin modificar los repositorios.
- La recuperación de contraseña siguió la misma estructura de archivos que el resto. Con eso, la decisión de dónde va cada cosa ya estaba tomada.

**Clases base reutilizables.** `BaseService` y `BaseRepository` concentran el CRUD, la paginación, los filtros y el borrado lógico. Cada recurso nuevo solo define lo que lo hace distinto.

**Convenciones de la API desde el primer día:**
- Respuesta uniforme `{success, message, data}`.
- UUID como identificador público, sin exponer los IDs internos.
- Borrado lógico (`is_active`).
- Swagger como documentación viva.

Por mantenerlas, el frontend y las pruebas se escriben siempre de la misma manera.

---

## 3. Lo que cambió en el camino, y por qué

| Cambio | Antes | Después | Motivo |
|---|---|---|---|
| Manejo de la sesión | Token guardado por el frontend (sesión local) | JWT en cookie `httponly` | JavaScript no puede leer la cookie, así que un ataque XSS no puede robar la sesión |
| Dónde viven las reglas de negocio | Solo en el servicio | En el servicio **y** en la base de datos (constraints y el trigger `fn_validar_horario`) | La BD es la última barrera: el seed y las inserciones directas también quedan validados |
| Permisos | Por rol | Por rol **y** por coordinación (`AccessScope`) | La realidad del centro: cada coordinación tiene sus propios ambientes |
| Correos | Se comparaban tal como se escribían | Normalizados a minúsculas | Evitar cuentas duplicadas y logins fallidos (DEF-02) |
| Calidad | Pruebas escritas, pero ejecutadas a mano y sin rutina | Suite estable, cobertura medida y linter configurado | Los cambios transversales estaban rompiendo pruebas sin que se notara |

---

## 4. Lo que costó

- **Los cambios transversales rompen cosas lejos de donde se hacen.** El paso a cookie dejó desactualizadas las pruebas de autenticación y usuarios (DEF-01: 41 de 122 sin pasar). El cambio de roles rompió la prueba E2E de fichas (DEF-05). En los dos casos el código de la aplicación estaba bien; lo que se quedó atrás fueron las pruebas.
- **Las pruebas no se ejecutaban de forma rutinaria.** Por eso esos defectos se descubrieron tiempo después, en el cierre de T6, y no el mismo día del cambio.
- **El historial de Git se perdió.** En una operación de Git se borraron archivos, y el historial anterior no se conservó: el repositorio actual arranca en el commit "Proyecto base". La línea de tiempo de este documento se reconstruyó gracias a que las migraciones guardan su fecha.
- **La carga masiva, que es el fuerte previsto del sistema, quedó para T7.** Primero había que estabilizar el modelo, los roles y las reglas anti-choque, porque la carga masiva depende de todo eso.

---

## 5. Aprendizajes

1. **Una buena estructura inicial abarata cada etapa siguiente.** Mantener la misma arquitectura permitió crecer de usuarios a un sistema de horarios completo sin reescribir.
2. **Validar en dos niveles** (aplicación y base de datos) da tranquilidad: los datos quedan protegidos aunque entren por otro camino.
3. **Después de un cambio transversal hay que correr toda la suite**, no solo las pruebas del módulo tocado. Una prueba que no se ejecuta no protege nada.
4. **Las pruebas también son código que envejece.** Cuando cambian las reglas, hay que actualizar las pruebas junto con la aplicación, en el mismo commit.
5. **Commits pequeños, con prefijo y en ramas** hacen que el historial sirva para algo: para entender qué pasó, revertir y enlazar los issues.

---

## 6. Qué haría distinto si empezara hoy

- Configurar la **integración continua** (pytest, ruff y ESLint en cada push) desde la primera semana, no al cierre.
- Separar desde el inicio la **base de datos de pruebas** de la de desarrollo.
- Definir los **roles y el alcance por coordinación** antes de construir las pantallas de gestión, para no tener que ajustarlas después.
- Diseñar la **carga masiva** junto con el modelo de horarios, porque es la funcionalidad que más depende de él.

---

## 7. Hacia dónde sigue

El backend llega al cierre de T6 estable: 129 pruebas, 87 % de cobertura y ruff sin errores. La base está lista para T7, donde lo prioritario es:
- la carga masiva de horarios,
- la integración continua,
- la preparación para el despliegue.

Ver [`deuda-tecnica.md`](deuda-tecnica.md) y [`../estado-del-proyecto.md`](../estado-del-proyecto.md).

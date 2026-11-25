# Matriz de casos de prueba — SIHS

**Convenciones:**
- **Tipo:** ✚ positivo (debe funcionar) · ✖ negativo (debe rechazarse).
- **Ejec. 1:** 24-nov-2026, antes de corregir los defectos.
- **Ejec. 2:** 24-nov-2026, después de corregirlos. Ver `reporte-ejecucion.md`.
- **Automatización:** prueba que ejecuta el caso. `pytest` = `backend/tests/...`, `PM` = colección de Postman, `E2E` = `frontend/E2E/`.
- **Datos de prueba:** las cuentas del seed (`python -m scripts.seed_horarios`) o los datos que crea cada prueba.

**Pasó\* en la Ejecución 1:** la prueba pasó por coincidencia. El usuario no llegó a crearse, o el token se enviaba por un canal que la API ya no lee, así que el 401 llegó por otra razón. Por eso no validaba lo que decía validar. Ver DEF-01.

## Autenticación y sesión

| ID | Caso | Tipo | Datos | Pasos | Resultado esperado | Ejec. 1 | Ejec. 2 | Automatización |
|---|---|---|---|---|---|---|---|---|
| CP-01 | Login correcto | ✚ | Usuario registrado · `Password123!` | 1. Registrar usuario 2. `POST /auth/login` | 200. Cookie `access_token` httponly. El cuerpo **no** trae el token | ✖ Falló (DEF-01) | ✔ Pasó | pytest `test_auth_routes::test_login_success` · PM 1.3 |
| CP-02 | Login con contraseña incorrecta | ✖ | Correo válido · `ClaveEquivocada1` | `POST /auth/login` | 401 "Credenciales inválidas." | ✔ Pasó\* | ✔ Pasó | pytest `test_login_invalid_password` · PM 1.1 |
| CP-03 | Login con correo no registrado | ✖ | `noexiste@example.com` | `POST /auth/login` | 401 con el **mismo** mensaje que CP-02 (no revela qué correos existen) | ✔ Pasó\* | ✔ Pasó | pytest `test_login_invalid_password_does_not_reveal_user_existence` |
| CP-04 | Login de usuario inactivo | ✖ | Usuario con `is_active=false` | 1. Desactivar 2. `POST /auth/login` | 401. No se entrega cookie | ✖ Falló (DEF-01) | ✔ Pasó | pytest `test_login_inactive_user_does_not_return_access_token` |
| CP-05 | Consultar perfil sin sesión | ✖ | Sin cookie | `GET /users/me` | 401 `{"success": false, "message": "No autenticado."}` | ✖ Falló (DEF-01) | ✔ Pasó | pytest `test_get_my_profile_without_token` · PM 3.2 |
| CP-06 | Token vencido | ✖ | JWT con `exp` en el pasado | `GET /users/me` con la cookie | 401 "Token inválido." | ✔ Pasó\* | ✔ Pasó | pytest `test_get_my_profile_with_expired_token` |
| CP-07 | Token sin firma (`alg: none`) | ✖ | JWT sin firmar | `GET /users/me` con la cookie | 401 (se rechaza el algoritmo) | ✔ Pasó\* | ✔ Pasó | pytest `test_get_my_profile_with_none_algorithm` |

## Registro y usuarios

| ID | Caso | Tipo | Datos | Pasos | Resultado esperado | Ejec. 1 | Ejec. 2 | Automatización |
|---|---|---|---|---|---|---|---|---|
| CP-08 | Registro público | ✚ | Nombre, correo, teléfono, documento y clave válidos | `POST /auth/register` | 201. Rol `user` | ✖ Falló (DEF-01) | ✔ Pasó | pytest `test_register_user_success` · PM 5.1 |
| CP-09 | Registro duplicando el correo con mayúsculas | ✖ | `Ana@x.com` y luego `ANA@x.com` | Registrar dos veces | La segunda vez: 409 | ✖ Falló, creaba otra cuenta (DEF-02) | ✔ Pasó | pytest `test_email_normalization::test_no_permite_duplicar_correo_cambiando_mayusculas` · PM 5.2 |
| CP-10 | Login escribiendo el correo con otras mayúsculas | ✚ | Registrado `login.x@example.com`, login con `LOGIN.X@EXAMPLE.com` | `POST /auth/login` | 200 | ✖ Falló, 401 (DEF-02) | ✔ Pasó | pytest `test_login_sin_importar_mayusculas` |
| CP-11 | Crear usuario por `/users` sin ser admin | ✖ | Sin sesión | `POST /users` | 401 (solo el admin crea usuarios por esta ruta) | — (nuevo) | ✔ Pasó | pytest `test_create_user_requires_admin` |
| CP-12 | Usuario sin rol de gestión lista usuarios | ✖ | Sesión de rol `user` | `GET /users` | 403 | ✖ Error (DEF-01) | ✔ Pasó | pytest `test_user_cannot_list_users` |

## Horarios (módulo crítico)

| ID | Caso | Tipo | Datos | Pasos | Resultado esperado | Ejec. 1 | Ejec. 2 | Automatización |
|---|---|---|---|---|---|---|---|---|
| CP-13 | Admin crea sede y ambiente | ✚ | Sede y ambiente con nombres únicos | `POST /sedes`, `POST /ambientes` | 201 en ambos | ✔ Pasó | ✔ Pasó | pytest `test_crud_sede_y_ambiente` |
| CP-14 | Programar una clase válida | ✚ | Ficha-trimestre, lunes, franja 3, resultado del programa, instructor, ambiente A | `POST /horarios` | 201. Aparece en la grilla | ✔ Pasó | ✔ Pasó | pytest `test_crear_casilla_y_choques` |
| CP-15 | Choques de ficha, instructor y ambiente | ✖ | Mismo día y franja que CP-14 | Repetir la casilla: misma ficha / mismo instructor en otra ficha / mismo ambiente en otra ficha | 409 en cada caso, con mensaje específico | ✔ Pasó | ✔ Pasó | pytest `test_crear_casilla_y_choques` |
| CP-16 | Reglas de modalidad y temática | ✖ | Presencial sin ambiente · instructor sin ese rol · resultado de otro programa | `POST /horarios` con cada dato | 422 "Una clase presencial requiere ambiente." y equivalentes | ✔ Pasó | ✔ Pasó | pytest `test_validaciones_de_casilla` · PM 2.7 |
| CP-17 | El coordinador no registra catálogos | ✖ | Sesión de coordinador | `POST /sedes`, `POST /ambientes`, `POST /fichas` | 403 | ✔ Pasó | ✔ Pasó | pytest `test_coordinador_solo_consulta_y_otros_roles_no_leen_catalogos` · PM 2.1, 2.2 |
| CP-18 | El coordinador usa un ambiente de otra coordinación | ✖ | Ambiente B asignado a otra coordinación | `POST /horarios` con el ambiente B | 403 "no está asignado a tu coordinación" | ✔ Pasó | ✔ Pasó | pytest `test_coordinador_programa_solo_su_coordinacion` |
| CP-19 | El coordinador programa una ficha de otra coordinación | ✖ | Ficha de otra coordinación | `POST /horarios` y `GET /horarios/grilla/{ft}` | 403 "no pertenece a tu coordinación" | ✔ Pasó | ✔ Pasó | pytest `test_coordinador_programa_solo_su_coordinacion` |
| CP-20 | Ni el admin usa el ambiente de otra coordinación | ✖ | Ambiente B de otra coordinación, ficha de la coordinación A | `POST /horarios` como admin | 422 "pertenece a …" | ✔ Pasó | ✔ Pasó | pytest `test_ambiente_de_otra_coordinacion_no_se_usa_ni_se_reasigna` |
| CP-21 | Reasignar un ambiente que ya tiene clases | ✖ | Ambiente A con clases de la coordinación A | `PUT /ambientes/{A}` hacia la coordinación B | 409 "tiene clases programadas…" | ✔ Pasó | ✔ Pasó | pytest `test_ambiente_de_otra_coordinacion_no_se_usa_ni_se_reasigna` |
| CP-22 | Coordinador sin coordinación asignada | ✖ | Usuario coordinador sin coordinación | `GET /ambientes` | 403 "no tiene una coordinación asignada" | ✔ Pasó | ✔ Pasó | pytest `test_coordinador_sin_coordinacion_no_accede` |
| CP-23 | El coordinador solo ve sus ambientes | ✚ | Cuenta del coordinador del seed | `GET /ambientes` | 200. Todos de su coordinación | — (manual) | ✔ Pasó | PM 2.3 |

## Recuperación de contraseña

| ID | Caso | Tipo | Datos | Pasos | Resultado esperado | Ejec. 1 | Ejec. 2 | Automatización |
|---|---|---|---|---|---|---|---|---|
| CP-24 | Recuperación completa | ✚ | Usuario activo · nueva clave `NuevaClave456!` | 1. `POST /auth/password/forgot` 2. Abrir el enlace 3. `POST /auth/password/reset` 4. Login | 200 en cada paso. La clave nueva funciona y la anterior no. El enlace no sirve dos veces | ✔ Pasó | ✔ Pasó | pytest `test_flujo_completo_de_recuperacion` |
| CP-25 | Pedir enlace con un correo no registrado | ✖ | `nadie@example.com` | `POST /auth/password/forgot` | 200 con el mismo mensaje genérico. No se envía correo | ✔ Pasó | ✔ Pasó | pytest `test_correo_inexistente_responde_igual_y_no_envia_nada` · PM 6.1 |
| CP-26 | Enlace inválido o vencido | ✖ | Token inexistente o con `expires_at` pasado | `GET /auth/password/reset/validate`, `POST /auth/password/reset` | 422 "El enlace … no es válido o ya expiró" | ✔ Pasó | ✔ Pasó | pytest `test_token_invalido_o_vencido` · PM 6.2 |

## Paneles e interfaz (E2E)

| ID | Caso | Tipo | Datos | Pasos | Resultado esperado | Ejec. 1 | Ejec. 2 | Automatización |
|---|---|---|---|---|---|---|---|---|
| CP-27 | El aprendiz consulta su información y no la de gestión | ✚ / ✖ | Cuenta `sofia.martinez@example.com` | `GET /mi/fichas`, `GET /sedes`, `GET /dashboard/resumen` | 200 con su ficha 3141665 · 403 · 403 | ✔ Pasó | ✔ Pasó | pytest `test_paneles_de_aprendiz_e_instructor` · PM 4.1–4.4 |
| CP-28 | Registrar una ficha desde la interfaz | ✚ | Código `E2E-<timestamp>`, jornada TARDE, presencial | 1. Login 2. Gestión → Fichas 3. Nueva ficha 4. Crear | 201. Mensaje "Ficha creada correctamente.". La ficha aparece en la tabla | Sin evidencia guardada | Pendiente de ejecución local | E2E `fichas.spec.ts` |
| CP-29 | Registrar una ficha con código repetido desde la interfaz | ✖ | Código `3141665` (ya existe) | Igual que CP-28 | 409. El formulario sigue abierto con el mensaje "Ya existe una ficha con ese código." | Sin evidencia guardada | Pendiente de ejecución local | E2E `fichas.spec.ts` |

**Resumen:**
- **29 casos:** 8 positivos, 20 negativos y 1 mixto (CP-27).
- **Ejecución 1:** 7 casos fallaron y 4 pasaron sin validar lo que debían. CP-11 todavía no existía y CP-23 se probaba a mano. Las pruebas E2E no tienen evidencia guardada.
- **Ejecución 2:** 27 casos pasaron. CP-28 y CP-29 (E2E) quedan pendientes de ejecutar en el equipo local, porque necesitan navegador; su resultado se anota en `reporte-ejecucion.md`.

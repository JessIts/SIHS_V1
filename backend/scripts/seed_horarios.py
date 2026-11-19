"""
Carga datos de prueba para todo el sistema, incluido el horario real de la
ficha 3141665.

Uso (desde la carpeta backend, con el venv activo):
    python -m scripts.seed_horarios

Es idempotente: si un registro ya existe (por su llave natural) no lo duplica
ni lo modifica, así que se puede ejecutar varias veces.

Crea 30 registros de cada entidad:
  - Sedes, ambientes, coordinaciones, programas, competencias,
    resultados y actividades de aprendizaje
  - Trimestres (2020-T1 a 2027-T2; 2026-T3 es el activo)
  - Fichas, programaciones ficha-trimestre y casillas de horario
  - 30 instructores (contraseña: Instructor123*)
  - 30 aprendices   (contraseña: Aprendiz123*)
  - 1 coordinador   (contraseña: Coordinador123*), asignado a la
    Coordinación Comercio y Mercadeo (la de la ficha 3141665)

Los ambientes quedan repartidos entre coordinaciones: cada ambiente que usa
un horario queda en la coordinación de su ficha, y los que no se usan quedan
en Comercio y Mercadeo, para que el coordinador tenga varios disponibles.

Excepciones, porque son catálogos con un tamaño natural:
  - Jornadas: 3 (MAÑANA, TARDE, NOCHE)
  - Franjas horarias: 6 (2 por jornada; son las filas de la grilla)
  - Días de la semana: 6 (lunes a sábado; la BD solo admite 1 a 7)
"""

from datetime import date, time

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import (
    ActividadAprendizaje,
    Ambiente,
    Competencia,
    Coordinacion,
    DiaSemana,
    Ficha,
    FichaTrimestre,
    FranjaHoraria,
    Horario,
    Jornada,
    Programa,
    ResultadoAprendizaje,
    Sede,
    Trimestre,
    User,
)
from app.models.enums import (
    EstadoFicha,
    EstadoTrimestre,
    ModalidadClase,
    ModalidadFicha,
)
from app.models.roles import UserRole


TOTAL = 30

INSTRUCTOR_PASSWORD = "Instructor123*"
COORDINADOR_PASSWORD = "Coordinador123*"
APRENDIZ_PASSWORD = "Aprendiz123*"


# ======================================================================
# Datos
# ======================================================================

# (nombre, dirección, tipo). Las 3 primeras son las del seed original.
SEDES = [
    ("Sede Principal", "Calle 52 # 13-65", "PRINCIPAL"),
    ("Sede Unigermana", "AK 14 # 63-87", "SECUNDARIA"),
    ("Sede Fontibón", "Cl 19A # 96c-40", "SECUNDARIA"),
    ("Sede Chapinero", "Calle 57 # 9-30", "SECUNDARIA"),
    ("Sede Kennedy", "Av. 1 de Mayo # 72-15", "SECUNDARIA"),
    ("Sede Suba", "Calle 145 # 91-20", "SECUNDARIA"),
    ("Sede Usaquén", "Carrera 7 # 120-45", "SECUNDARIA"),
    ("Sede Engativá", "Calle 72 # 110-08", "SECUNDARIA"),
    ("Sede Bosa", "Calle 65 Sur # 80-12", "SECUNDARIA"),
    ("Sede Teusaquillo", "Carrera 24 # 39-50", "SECUNDARIA"),
    ("Sede Puente Aranda", "Calle 13 # 65-10", "SECUNDARIA"),
    ("Sede Ciudad Bolívar", "Diagonal 62 Sur # 20-35", "SECUNDARIA"),
    ("Sede San Cristóbal", "Calle 22 Sur # 5-40", "SECUNDARIA"),
    ("Sede Tunjuelito", "Carrera 15 # 52-18 Sur", "SECUNDARIA"),
    ("Sede Barrios Unidos", "Calle 68 # 28-20", "SECUNDARIA"),
    ("Sede Los Mártires", "Carrera 19 # 10-44", "SECUNDARIA"),
    ("Sede Antonio Nariño", "Calle 17 Sur # 18-30", "SECUNDARIA"),
    ("Sede La Candelaria", "Calle 11 # 4-21", "SECUNDARIA"),
    ("Sede Rafael Uribe", "Carrera 10 # 31-60 Sur", "SECUNDARIA"),
    ("Sede Usme", "Calle 91 Sur # 3-15", "SECUNDARIA"),
    ("Sede Santa Fe", "Carrera 5 # 26-12", "SECUNDARIA"),
    ("Sede Restrepo", "Calle 17 Sur # 22-40", "SECUNDARIA"),
    ("Sede Salitre", "Av. La Esperanza # 68-30", "SECUNDARIA"),
    ("Sede Calle 80", "Calle 80 # 69-70", "SECUNDARIA"),
    ("Sede Américas", "Av. Américas # 50-25", "SECUNDARIA"),
    ("Sede Galerías", "Calle 53 # 24-60", "SECUNDARIA"),
    ("Sede Modelia", "Calle 24 # 75-30", "SECUNDARIA"),
    ("Sede Toberín", "Calle 166 # 20-40", "SECUNDARIA"),
    ("Sede Soacha", "Carrera 7 # 13-50, Soacha", "SECUNDARIA"),
    ("Sede Funza", "Calle 15 # 12-20, Funza", "SECUNDARIA"),
]

# Ambientes 4 a 30: uno en cada sede de la 4 a la 30 (los 3 primeros están en Fontibón)
NOMBRES_AMBIENTES = [
    "Aula 101", "Aula 102", "Aula 201", "Aula 202", "Aula 301",
    "Laboratorio de Software", "Laboratorio de Redes", "Sala de Cómputo 1",
    "Sala de Cómputo 2", "Taller de Cocina", "Taller Eléctrico",
    "Taller Automotriz", "Laboratorio de Química", "Sala de Simulación",
    "Estudio de Grabación", "Taller de Confección", "Taller de Soldadura",
    "Laboratorio de Alimentos", "Sala de Diseño", "Auditorio",
    "Aula Bilingüe", "Laboratorio de Automatización", "Gimnasio",
    "Sala de Juntas", "Aula Ambiental", "Laboratorio de Topografía",
    "Sala de Animación",
]

# (coordinación, código de programa, programa, nivel)
# La primera es la del seed original (ficha 3141665).
PROGRAMAS = [
    ("Coordinación Comercio y Mercadeo", "PRG-MERC", "DESARROLLO DE PROCESOS DE MERCADEO", "TECNÓLOGO"),
    ("Coordinación Teleinformática", "PRG-ADSO", "ANÁLISIS Y DESARROLLO DE SOFTWARE", "TECNÓLOGO"),
    ("Coordinación Gestión Contable", "PRG-CONT", "CONTABILIZACIÓN DE OPERACIONES COMERCIALES Y FINANCIERAS", "TÉCNICO"),
    ("Coordinación Talento Humano", "PRG-GTH", "GESTIÓN DEL TALENTO HUMANO", "TECNÓLOGO"),
    ("Coordinación Logística", "PRG-LOG", "GESTIÓN LOGÍSTICA", "TECNÓLOGO"),
    ("Coordinación Telecomunicaciones", "PRG-REDES", "GESTIÓN DE REDES DE DATOS", "TECNÓLOGO"),
    ("Coordinación Medios Audiovisuales", "PRG-MULT", "PRODUCCIÓN DE MEDIOS AUDIOVISUALES DIGITALES", "TECNÓLOGO"),
    ("Coordinación Gastronomía", "PRG-COCI", "COCINA", "TÉCNICO"),
    ("Coordinación Electricidad", "PRG-ELEC", "ELECTRICIDAD INDUSTRIAL", "TÉCNICO"),
    ("Coordinación Automotriz", "PRG-MECA", "MANTENIMIENTO MECATRÓNICO DE AUTOMOTORES", "TECNÓLOGO"),
    ("Coordinación Salud Ocupacional", "PRG-SST", "SEGURIDAD Y SALUD EN EL TRABAJO", "TECNÓLOGO"),
    ("Coordinación Salud", "PRG-ENF", "AUXILIAR EN ENFERMERÍA", "TÉCNICO"),
    ("Coordinación Ambiental", "PRG-AMB", "GESTIÓN AMBIENTAL", "TECNÓLOGO"),
    ("Coordinación Diseño", "PRG-DIS", "DISEÑO E INTEGRACIÓN DE MULTIMEDIA", "TECNÓLOGO"),
    ("Coordinación Turismo", "PRG-TUR", "GUIANZA TURÍSTICA", "TECNÓLOGO"),
    ("Coordinación Servicios Financieros", "PRG-BANC", "GESTIÓN BANCARIA Y DE ENTIDADES FINANCIERAS", "TECNÓLOGO"),
    ("Coordinación Construcción", "PRG-CONS", "CONSTRUCCIÓN DE EDIFICACIONES", "TECNÓLOGO"),
    ("Coordinación Infraestructura", "PRG-TOPO", "TOPOGRAFÍA", "TECNÓLOGO"),
    ("Coordinación Confección y Moda", "PRG-MODA", "DISEÑO DE MODAS", "TECNÓLOGO"),
    ("Coordinación Agropecuaria", "PRG-AGRO", "PRODUCCIÓN AGROPECUARIA ECOLÓGICA", "TECNÓLOGO"),
    ("Coordinación Agroindustria", "PRG-ALIM", "CONTROL DE CALIDAD DE ALIMENTOS", "TECNÓLOGO"),
    ("Coordinación Química Industrial", "PRG-QUIM", "QUÍMICA APLICADA A LA INDUSTRIA", "TECNÓLOGO"),
    ("Coordinación Metalmecánica", "PRG-SOLD", "SOLDADURA DE PRODUCTOS METÁLICOS", "TÉCNICO"),
    ("Coordinación Automatización", "PRG-AUTO", "AUTOMATIZACIÓN DE SISTEMAS MECATRÓNICOS", "TECNÓLOGO"),
    ("Coordinación Gestión Administrativa", "PRG-ADMIN", "GESTIÓN ADMINISTRATIVA", "TECNÓLOGO"),
    ("Coordinación Gestión Documental", "PRG-DOC", "GESTIÓN DOCUMENTAL", "TECNÓLOGO"),
    ("Coordinación Actividad Física", "PRG-DEP", "ENTRENAMIENTO DEPORTIVO", "TECNÓLOGO"),
    ("Coordinación Animación Digital", "PRG-ANIM", "ANIMACIÓN 3D", "TECNÓLOGO"),
    ("Coordinación Infraestructura TIC", "PRG-TIC", "IMPLEMENTACIÓN DE INFRAESTRUCTURA TIC", "TECNÓLOGO"),
    ("Coordinación Ventas", "PRG-VENT", "VENTA DE PRODUCTOS Y SERVICIOS", "TÉCNICO"),
]

# Resultados de aprendizaje: los 3 del PDF (programa de mercadeo) y uno
# para cada uno de los programas 2 a 28. Los 2 últimos programas quedan
# sin resultados, como un programa recién creado.
RESULTADOS_MERCADEO = [
    ("13", "Aplicar acciones del plan de merchandising en el canal de acuerdo con objetivos de mercadeo y normativa"),
    ("14", "Establecer el plan de acción de endomarketing de acuerdo con la identidad corporativa"),
    ("15", "Seleccionar técnica de evaluación de estrategias para el plan de mercadeo según políticas de la organización"),
]

RESULTADOS_OTROS = [
    "Construir el modelo de datos del sistema de información según los requerimientos",
    "Registrar los hechos económicos de acuerdo con la normativa contable vigente",
    "Ejecutar el proceso de selección de personal según el perfil del cargo",
    "Planear el almacenamiento de mercancías según su naturaleza y rotación",
    "Configurar dispositivos de red según el diseño lógico establecido",
    "Editar piezas audiovisuales de acuerdo con el guion técnico",
    "Preparar bases y fondos de cocina según la técnica culinaria",
    "Instalar circuitos eléctricos de baja tensión según el RETIE",
    "Diagnosticar fallas del sistema de inyección según el manual del fabricante",
    "Identificar peligros y valorar riesgos según la metodología GTC 45",
    "Aplicar cuidados básicos al paciente según los protocolos de atención",
    "Formular el plan de manejo ambiental de acuerdo con la normativa vigente",
    "Diseñar interfaces gráficas según principios de usabilidad",
    "Orientar recorridos turísticos según el patrimonio del destino",
    "Analizar productos financieros de acuerdo con el perfil del cliente",
    "Interpretar planos arquitectónicos según las normas de construcción",
    "Realizar levantamientos topográficos con estación total",
    "Elaborar patrones de prendas según la tabla de medidas",
    "Implementar prácticas agroecológicas según el plan de producción",
    "Verificar la calidad de materias primas según especificaciones técnicas",
    "Realizar análisis químicos cuantitativos según el método normalizado",
    "Soldar uniones con proceso SMAW según el procedimiento calificado",
    "Programar controladores lógicos (PLC) según la secuencia de control",
    "Gestionar la correspondencia de la organización según el programa de gestión documental",
    "Organizar archivos de gestión según las tablas de retención documental",
    "Planificar sesiones de entrenamiento según el diagnóstico del deportista",
    "Modelar personajes en 3D según el diseño conceptual",
]

TIPOS_ACTIVIDAD = [
    ("TALLER", 120),
    ("PROYECTO", 240),
    ("EVALUACIÓN", 90),
    ("PRÁCTICA", 180),
    ("INVESTIGACIÓN", 60),
]

# Instructores: los 3 primeros son los del seed original
INSTRUCTORES = [
    ("1000000001", "CARLOS PEREZ", "carlos.perez@example.com"),
    ("1000000002", "OMAR SANCHEZ", "omar.sanchez@example.com"),
    ("1000000003", "NAYUBI ROJAS", "nayubi.rojas@example.com"),
] + [
    (f"10000001{i:02d}", nombre, None)
    for i, nombre in enumerate([
        "ANDREA CASTRO", "JORGE HERRERA", "DIANA MORALES", "LUIS FERNANDO VARGAS",
        "PAOLA JIMENEZ", "RICARDO MENDOZA", "CLAUDIA ORTIZ", "FELIPE RUIZ",
        "MARCELA SUAREZ", "ANDRES GUTIERREZ", "NATALIA RIOS", "JULIAN TORRES",
        "CAROLINA MEJIA", "SERGIO NAVARRO", "LILIANA PARRA", "MAURICIO CARDENAS",
        "ADRIANA SALAZAR", "HERNAN CORTES", "VIVIANA MORENO", "FABIAN OSORIO",
        "SANDRA PINEDA", "CAMILO ARIAS", "JOHANA MARTINEZ", "OSCAR VALENCIA",
        "PATRICIA GIRALDO", "EDWIN CASTAÑO", "MONICA RESTREPO",
    ], start=1)
]

# Aprendices: los 2 primeros son los del seed original
APRENDICES = [
    ("1000000021", "SOFIA MARTINEZ", "sofia.martinez@example.com"),
    ("1000000022", "JUAN RAMIREZ", "juan.ramirez@example.com"),
] + [
    (f"10000002{i:02d}", nombre, None)
    for i, nombre in enumerate([
        "VALENTINA GOMEZ", "SANTIAGO LOPEZ", "ISABELLA RODRIGUEZ", "MATEO GARCIA",
        "MARIANA HERNANDEZ", "SEBASTIAN DIAZ", "GABRIELA MUÑOZ", "NICOLAS ALVAREZ",
        "LAURA SOFIA ROMERO", "DANIEL ACOSTA", "SARA VALENCIA", "ALEJANDRO ROJAS",
        "MARIA JOSE CASTILLO", "DAVID OSPINA", "ANA LUCIA BELTRAN", "TOMAS QUINTERO",
        "CAMILA AGUILAR", "SAMUEL CABRERA", "DANIELA LEON", "EMMANUEL FRANCO",
        "LUCIANA VEGA", "JUAN DAVID MOLINA", "ANTONELLA SILVA", "MIGUEL ANGEL REYES",
        "SALOME CARDONA", "MARTIN BERNAL", "VALERIA PEÑA", "SIMON ZAPATA",
    ], start=1)
]

COORDINADOR = ("1000000010", "LAURA GOMEZ", "coordinacion.mercadeo@example.com")

# Fechas típicas de cada trimestre: numero -> (inicio, fin) como (mes, día)
FECHAS_TRIMESTRE = {
    1: ((1, 20), (4, 4)),
    2: ((4, 13), (6, 27)),
    3: ((7, 9), (9, 28)),
    4: ((10, 5), (12, 18)),
}

TRIMESTRE_ACTIVO = (2026, 3)


# ======================================================================
# Utilidades
# ======================================================================

def get_or_create(db: Session, model, lookup: dict, **values):
    """Busca por `lookup`; si no existe lo crea con lookup + values."""

    instance = db.scalar(select(model).filter_by(**lookup))

    if instance:
        return instance, False

    instance = model(**lookup, **values)
    db.add(instance)
    db.flush()

    return instance, True


def email_de(nombre: str) -> str:
    """'LUIS FERNANDO VARGAS' -> 'luis.fernando.vargas@example.com'"""

    limpio = (
        nombre.lower()
        .replace("ñ", "n")
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )

    return ".".join(limpio.split()) + "@example.com"


def telefono(documento: str) -> str:
    return "300" + documento[-7:]


def numero_trimestre(fecha: date) -> int:
    """Índice consecutivo de trimestre, para contar trimestres entre fechas."""

    return fecha.year * 4 + (fecha.month - 1) // 3


def check_total(nombre: str, datos: list) -> None:
    if len(datos) != TOTAL:
        raise ValueError(f"{nombre}: se esperaban {TOTAL} registros y hay {len(datos)}")


# ======================================================================
# Carga
# ======================================================================

def seed(db: Session) -> None:
    creados = 0

    def track(result):
        nonlocal creados
        instance, created = result
        creados += int(created)
        return instance

    for nombre, datos in [
        ("Sedes", SEDES),
        ("Programas", PROGRAMAS),
        ("Instructores", INSTRUCTORES),
        ("Aprendices", APRENDICES),
    ]:
        check_total(nombre, datos)

    # ------------------------------------------------------------------
    # Calendario: catálogos de tamaño fijo
    # ------------------------------------------------------------------
    manana = track(get_or_create(db, Jornada, {"nombre": "MAÑANA"}))
    tarde = track(get_or_create(db, Jornada, {"nombre": "TARDE"}))
    noche = track(get_or_create(db, Jornada, {"nombre": "NOCHE"}))
    jornadas = [manana, tarde, noche]

    franjas_def = [
        (manana, time(6, 15), time(9, 0), 1),
        (manana, time(9, 0), time(12, 0), 2),
        (tarde, time(12, 0), time(15, 0), 3),
        (tarde, time(15, 0), time(18, 0), 4),
        (noche, time(18, 0), time(20, 0), 5),
        (noche, time(20, 0), time(22, 0), 6),
    ]

    franjas = {}
    for jornada, inicio, fin, orden in franjas_def:
        franjas[orden] = track(get_or_create(
            db,
            FranjaHoraria,
            {"orden": orden},
            jornada=jornada,
            hora_inicio=inicio,
            hora_fin=fin,
        ))

    # Las 2 franjas de cada jornada, en orden
    franjas_por_jornada = {
        manana.id: [franjas[1], franjas[2]],
        tarde.id: [franjas[3], franjas[4]],
        noche.id: [franjas[5], franjas[6]],
    }

    dias = {}
    for numero, nombre in enumerate(
        ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO"],
        start=1,
    ):
        dias[numero] = track(get_or_create(db, DiaSemana, {"numero": numero}, nombre=nombre))

    # ------------------------------------------------------------------
    # Trimestres: 2020-T1 ... 2027-T2 (30)
    # ------------------------------------------------------------------
    trimestres = []
    for indice in range(TOTAL):
        anio = 2020 + indice // 4
        numero = indice % 4 + 1
        (mes_ini, dia_ini), (mes_fin, dia_fin) = FECHAS_TRIMESTRE[numero]

        if (anio, numero) < TRIMESTRE_ACTIVO:
            estado = EstadoTrimestre.CERRADO
        elif (anio, numero) == TRIMESTRE_ACTIVO:
            estado = EstadoTrimestre.ACTIVO
        else:
            estado = EstadoTrimestre.PLANEACION

        trimestres.append(track(get_or_create(
            db,
            Trimestre,
            {"anio": anio, "numero": numero},
            fecha_inicio=date(anio, mes_ini, dia_ini),
            fecha_fin=date(anio, mes_fin, dia_fin),
            estado=estado,
        )))

    trimestre_por_clave = {(t.anio, t.numero): t for t in trimestres}
    trimestre_activo = trimestre_por_clave[TRIMESTRE_ACTIVO]

    # ------------------------------------------------------------------
    # Infraestructura: sedes y ambientes (30 c/u)
    # ------------------------------------------------------------------
    sedes = [
        track(get_or_create(db, Sede, {"nombre": nombre}, direccion=direccion, tipo=tipo))
        for nombre, direccion, tipo in SEDES
    ]
    fontibon = sedes[2]

    ambientes = [
        track(get_or_create(
            db,
            Ambiente,
            {"sede_id": fontibon.id, "nombre": nombre},
            capacidad=30,
        ))
        for nombre in ["202 A", "304 A", "304 B"]
    ]

    for i, nombre in enumerate(NOMBRES_AMBIENTES):
        sede = sedes[i + 3]
        ambientes.append(track(get_or_create(
            db,
            Ambiente,
            {"sede_id": sede.id, "nombre": nombre},
            capacidad=20 + (i % 5) * 5,
        )))

    check_total("Ambientes", ambientes)

    # ------------------------------------------------------------------
    # Estructura académica: coordinaciones, programas, competencias (30 c/u)
    # ------------------------------------------------------------------
    coordinaciones = []
    programas = []
    competencias = []

    for i, (nombre_coord, codigo, nombre_prog, nivel) in enumerate(PROGRAMAS):
        coordinacion = track(get_or_create(db, Coordinacion, {"nombre": nombre_coord}))

        # Cada coordinación opera en 2 sedes
        for sede in (sedes[i], sedes[(i + 10) % TOTAL]):
            if sede not in coordinacion.sedes:
                coordinacion.sedes.append(sede)

        programa = track(get_or_create(
            db,
            Programa,
            {"codigo": codigo},
            nombre=nombre_prog,
            nivel=nivel,
            coordinacion=coordinacion,
        ))

        descripcion = (
            "Competencia de prueba del programa de mercadeo"
            if i == 0
            else f"Ejecutar los procesos propios de {nombre_prog.lower()} según la normativa vigente"
        )

        competencia = track(get_or_create(
            db,
            Competencia,
            {"programa_id": programa.id, "codigo": "COMP-01"},
            descripcion=descripcion,
        ))

        coordinaciones.append(coordinacion)
        programas.append(programa)
        competencias.append(competencia)

    # ------------------------------------------------------------------
    # Resultados de aprendizaje (30) y actividades (30)
    # ------------------------------------------------------------------
    resultados = []
    resultado_por_programa = {}

    for codigo, descripcion in RESULTADOS_MERCADEO:
        resultados.append(track(get_or_create(
            db,
            ResultadoAprendizaje,
            {"competencia_id": competencias[0].id, "codigo": codigo},
            descripcion=descripcion,
        )))

    resultados_mercadeo = {r.codigo: r for r in resultados}

    for i, descripcion in enumerate(RESULTADOS_OTROS, start=1):
        resultado = track(get_or_create(
            db,
            ResultadoAprendizaje,
            {"competencia_id": competencias[i].id, "codigo": "01"},
            descripcion=descripcion,
        ))
        resultados.append(resultado)
        resultado_por_programa[programas[i].id] = resultado

    check_total("Resultados de aprendizaje", resultados)

    actividades = []
    for i, resultado in enumerate(resultados):
        tipo, duracion = TIPOS_ACTIVIDAD[i % len(TIPOS_ACTIVIDAD)]
        actividades.append(track(get_or_create(
            db,
            ActividadAprendizaje,
            {"resultado_id": resultado.id, "codigo": "ACT-01"},
            descripcion=f"{tipo.capitalize()} para: {resultado.descripcion[:120]}",
            tipo=tipo,
            duracion_minutos=duracion,
        )))

    check_total("Actividades de aprendizaje", actividades)

    # ------------------------------------------------------------------
    # Usuarios: 30 instructores, 30 aprendices y 1 coordinador
    # ------------------------------------------------------------------
    def crear_usuario(documento, nombre, email, password, role):
        return track(get_or_create(
            db,
            User,
            {"document_number": documento},
            name=nombre,
            email=email or email_de(nombre),
            phone=telefono(documento),
            password_hash=hash_password(password),
            role=role,
        ))

    instructores = [
        crear_usuario(doc, nombre, email, INSTRUCTOR_PASSWORD, UserRole.INSTRUCTOR)
        for doc, nombre, email in INSTRUCTORES
    ]

    aprendices = [
        crear_usuario(doc, nombre, email, APRENDIZ_PASSWORD, UserRole.APRENDIZ)
        for doc, nombre, email in APRENDICES
    ]

    coordinador = crear_usuario(*COORDINADOR, COORDINADOR_PASSWORD, UserRole.COORDINADOR)

    if coordinador.coordinacion_id is None:
        coordinador.coordinacion = coordinaciones[0]

    # ------------------------------------------------------------------
    # Fichas (30)
    #   0       -> 3141665, la del PDF (tarde, en formación)
    #   1 a 25  -> en formación, programadas en el trimestre activo
    #   26 y 27 -> finalizadas
    #   28 y 29 -> canceladas
    # ------------------------------------------------------------------
    codigos = ["3141665"] + [str(2786540 + i * 12347) for i in range(1, TOTAL)]
    inicios = [date(2024, 7, 15), date(2025, 1, 20), date(2025, 4, 14), date(2025, 7, 7), date(2026, 1, 19), date(2026, 4, 13)]

    fichas = []
    for i, codigo in enumerate(codigos):
        if i == 0:
            datos = dict(
                programa=programas[0],
                jornada=tarde,
                modalidad=ModalidadFicha.PRESENCIAL,
                estado=EstadoFicha.EN_FORMACION,
                fecha_inicio=date(2024, 10, 1),
                fecha_fin=date(2026, 12, 31),
            )
        else:
            if i <= 25:
                estado = EstadoFicha.EN_FORMACION
                inicio = inicios[i % len(inicios)]
            elif i <= 27:
                estado = EstadoFicha.FINALIZADA
                inicio = date(2023, 1, 23)
            else:
                estado = EstadoFicha.CANCELADA
                inicio = date(2025, 1, 20)

            if i % 7 == 3:
                modalidad = ModalidadFicha.VIRTUAL
            elif i % 7 == 5:
                modalidad = ModalidadFicha.MIXTA
            else:
                modalidad = ModalidadFicha.PRESENCIAL

            datos = dict(
                programa=programas[i],
                jornada=jornadas[i % 3],
                modalidad=modalidad,
                estado=estado,
                fecha_inicio=inicio,
                fecha_fin=inicio.replace(year=inicio.year + 2),
            )

        fichas.append(track(get_or_create(db, Ficha, {"codigo": codigo}, **datos)))

    # Aprendices: los 2 del PDF en la 3141665 y uno por ficha en las demás
    asignacion = [(aprendices[0], fichas[0]), (aprendices[1], fichas[0])]
    asignacion += [(aprendices[k], fichas[k - 1]) for k in range(2, TOTAL)]

    for aprendiz, ficha in asignacion:
        if aprendiz not in ficha.aprendices:
            ficha.aprendices.append(aprendiz)

    # ------------------------------------------------------------------
    # Programación ficha-trimestre (30): una por ficha
    # ------------------------------------------------------------------
    fichas_trimestre = []
    for i, ficha in enumerate(fichas):
        if i == 0:
            trimestre, numero, horas = trimestre_activo, 7, 24
        else:
            if ficha.estado == EstadoFicha.FINALIZADA:
                trimestre = trimestre_por_clave[(2024, 3)]
            elif ficha.estado == EstadoFicha.CANCELADA:
                trimestre = trimestre_por_clave[(2025, 2)]
            else:
                trimestre = trimestre_activo

            numero = max(1, numero_trimestre(trimestre.fecha_inicio) - numero_trimestre(ficha.fecha_inicio) + 1)
            horas = [24, 30, 36, 40][i % 4]

        fichas_trimestre.append(track(get_or_create(
            db,
            FichaTrimestre,
            {"ficha_id": ficha.id, "trimestre_id": trimestre.id},
            trimestre_ficha=numero,
            horas_semanales=horas,
        )))

    # ------------------------------------------------------------------
    # Horarios (30 casillas en el trimestre activo)
    #   - 8 de la ficha 3141665 (las del PDF)
    #   - 2 por cada ficha de la 1 a la 11 (22)
    # Para que no haya choques, cada casilla nueva usa un instructor y un
    # ambiente distintos, y las franjas de la jornada de su ficha.
    # ------------------------------------------------------------------
    casillas = []

    for dia, codigo_resultado, instructor, modalidad, ambiente in [
        (1, "15", 0, ModalidadClase.SINCRONICO, None),
        (2, "15", 0, ModalidadClase.PRESENCIAL, 0),
        (4, "14", 1, ModalidadClase.PRESENCIAL, 1),
        (5, "13", 2, ModalidadClase.PRESENCIAL, 2),
    ]:
        for orden_franja in (3, 4):
            casillas.append(dict(
                ficha_trimestre=fichas_trimestre[0],
                dia=dias[dia],
                franja=franjas[orden_franja],
                resultado=resultados_mercadeo[codigo_resultado],
                instructor=instructores[instructor],
                modalidad=modalidad,
                ambiente=ambientes[ambiente] if ambiente is not None else None,
            ))

    siguiente_instructor = 3
    siguiente_ambiente = 3

    for i in range(1, 12):
        ficha = fichas[i]
        resultado = resultado_por_programa.get(ficha.programa_id)

        if resultado is None:
            continue

        franjas_ficha = franjas_por_jornada[ficha.jornada_id]
        dias_ficha = [dias[i % 6 + 1], dias[(i + 3) % 6 + 1]]

        for n in range(2):
            sincronica = (
                ficha.modalidad == ModalidadFicha.VIRTUAL
                or (n == 1 and i % 3 == 0)
            )

            ambiente = None
            if not sincronica:
                ambiente = ambientes[siguiente_ambiente]
                siguiente_ambiente += 1

            casillas.append(dict(
                ficha_trimestre=fichas_trimestre[i],
                dia=dias_ficha[n],
                franja=franjas_ficha[n],
                resultado=resultado,
                instructor=instructores[siguiente_instructor],
                modalidad=ModalidadClase.SINCRONICO if sincronica else ModalidadClase.PRESENCIAL,
                ambiente=ambiente,
            ))
            siguiente_instructor += 1

    check_total("Horarios", casillas)

    # ------------------------------------------------------------------
    # Reparto de ambientes entre coordinaciones (solo los que no tienen)
    # ------------------------------------------------------------------
    for casilla in casillas:
        ambiente = casilla["ambiente"]

        if ambiente is not None and ambiente.coordinacion_id is None:
            ambiente.coordinacion_id = casilla["ficha_trimestre"].ficha.programa.coordinacion_id

    for ambiente in ambientes:
        if ambiente.coordinacion_id is None:
            ambiente.coordinacion = coordinaciones[0]

    db.flush()

    omitidas = []

    for casilla in casillas:
        ficha_trimestre = casilla["ficha_trimestre"]

        existe = db.scalar(select(Horario).filter_by(
            ficha_trimestre_id=ficha_trimestre.id,
            dia_id=casilla["dia"].id,
            franja_id=casilla["franja"].id,
        ))

        if existe:
            continue

        # Cada casilla va en su propio SAVEPOINT: si choca con un horario que
        # ya estaba en la BD, se omite sin deshacer el resto de la carga.
        try:
            with db.begin_nested():
                db.add(Horario(trimestre_id=ficha_trimestre.trimestre_id, **casilla))
                db.flush()
            creados += 1
        except DBAPIError as error:
            omitidas.append((ficha_trimestre.ficha.codigo, casilla["dia"].nombre, str(error.orig).splitlines()[0]))

    db.commit()

    # ------------------------------------------------------------------
    # Resumen
    # ------------------------------------------------------------------
    print(f"Registros nuevos: {creados}")

    if omitidas:
        print()
        print("Casillas omitidas por chocar con datos que ya existían:")
        for codigo, dia, motivo in omitidas:
            print(f"  ficha {codigo} ({dia}): {motivo}")

    print()
    print("Totales en la base de datos:")
    for etiqueta, model, filtro in [
        ("Sedes", Sede, None),
        ("Ambientes", Ambiente, None),
        ("Coordinaciones", Coordinacion, None),
        ("Programas", Programa, None),
        ("Competencias", Competencia, None),
        ("Resultados de aprendizaje", ResultadoAprendizaje, None),
        ("Actividades de aprendizaje", ActividadAprendizaje, None),
        ("Jornadas", Jornada, None),
        ("Franjas horarias", FranjaHoraria, None),
        ("Días de la semana", DiaSemana, None),
        ("Trimestres", Trimestre, None),
        ("Fichas", Ficha, None),
        ("Fichas por trimestre", FichaTrimestre, None),
        ("Horarios", Horario, None),
        ("Instructores", User, User.role == UserRole.INSTRUCTOR),
        ("Aprendices", User, User.role == UserRole.APRENDIZ),
        ("Coordinadores", User, User.role == UserRole.COORDINADOR),
    ]:
        consulta = select(func.count()).select_from(model)
        if filtro is not None:
            consulta = consulta.where(filtro)
        print(f"  {etiqueta:<28} {db.scalar(consulta)}")

    print()
    print("UUIDs útiles para Swagger:")
    print(f"  ficha_trimestre 3141665 (grilla) : {fichas_trimestre[0].uuid}")
    print(f"  ficha 3141665                    : {fichas[0].uuid}")
    print(f"  trimestre 2026-T3 (activo)       : {trimestre_activo.uuid}")

    print()
    print("Cuentas de prueba (correo / contraseña):")
    print(f"  coordinador {coordinador.email:<36} {COORDINADOR_PASSWORD}  ({coordinador.coordinacion.nombre})")
    for user in instructores[:3]:
        print(f"  instructor  {user.email:<36} {INSTRUCTOR_PASSWORD}")
    for user in aprendices[:3]:
        print(f"  aprendiz    {user.email:<36} {APRENDIZ_PASSWORD}")
    print("  (los demás instructores y aprendices usan la misma contraseña de su rol)")


def main():
    db = SessionLocal()

    try:
        seed(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

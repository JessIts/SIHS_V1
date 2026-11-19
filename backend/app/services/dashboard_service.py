from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.scope import UNRESTRICTED, AccessScope
from app.models.ambiente import Ambiente
from app.models.coordinacion import Coordinacion
from app.models.enums import EstadoTrimestre
from app.models.ficha import Ficha
from app.models.ficha_trimestre import FichaTrimestre
from app.models.horario import Horario
from app.models.programa import Programa
from app.models.sede import Sede
from app.models.trimestre import Trimestre
from app.models.user import User
from app.services.horario_service import HorarioService


class DashboardService:
    """
    Resumen para los tableros de administración y coordinación.
    Para un coordinador, ambientes, programas, fichas, horarios y
    programaciones se limitan a su coordinación.
    """

    def __init__(self, db: Session, scope: AccessScope = UNRESTRICTED):
        self.db = db
        self.scope = scope

    def _contar(self, model, *conditions, solo_activos: bool = True) -> int:
        statement = select(func.count()).select_from(model)

        if solo_activos:
            statement = statement.where(model.is_active.is_(True))

        if conditions:
            statement = statement.where(*conditions)

        return self.db.scalar(statement) or 0

    def _contar_activos(self, model) -> int:
        return self._contar(model)

    def _de_la_coordinacion(self) -> dict:
        """Condiciones por modelo según el alcance (vacías para el admin)."""

        if not self.scope.restricted:
            return {"ambiente": [], "programa": [], "ficha": [], "horario": [], "ficha_trimestre": []}

        cid = self.scope.coordinacion_id
        ficha = Ficha.programa.has(Programa.coordinacion_id == cid)

        return {
            "ambiente": [Ambiente.coordinacion_id == cid],
            "programa": [Programa.coordinacion_id == cid],
            "ficha": [ficha],
            "ficha_trimestre": [FichaTrimestre.ficha.has(ficha)],
            "horario": [Horario.ficha_trimestre.has(FichaTrimestre.ficha.has(ficha))],
        }

    def get_resumen(self) -> dict:
        usuarios = dict(
            self.db.execute(
                select(User.role, func.count())
                .where(User.is_active.is_(True))
                .group_by(User.role)
            ).all()
        )

        trimestres_vigentes = list(
            self.db.scalars(
                select(Trimestre)
                .where(
                    Trimestre.is_active.is_(True),
                    Trimestre.estado.in_([EstadoTrimestre.ACTIVO, EstadoTrimestre.PLANEACION]),
                )
                .order_by(Trimestre.anio.desc(), Trimestre.numero.desc())
            ).all()
        )

        alcance = self._de_la_coordinacion()

        programaciones = []

        if trimestres_vigentes:
            fichas_trimestre = self.db.scalars(
                select(FichaTrimestre)
                .where(
                    FichaTrimestre.is_active.is_(True),
                    FichaTrimestre.trimestre_id.in_([t.id for t in trimestres_vigentes]),
                    *alcance["ficha_trimestre"],
                )
            ).unique().all()

            for ft in fichas_trimestre:
                horas = sum(
                    HorarioService.duracion_horas(h.franja) for h in ft.horarios
                )

                programaciones.append({
                    "ficha_trimestre_uuid": ft.uuid,
                    "ficha": ft.ficha.codigo,
                    "programa": ft.ficha.programa.nombre,
                    "trimestre_ficha": ft.trimestre_ficha,
                    "trimestre": f"{ft.trimestre.anio}-T{ft.trimestre.numero}",
                    "horas_semanales": ft.horas_semanales,
                    "horas_programadas": round(horas, 2),
                })

            # Primero las que tienen menos horas programadas (las que faltan por armar)
            programaciones.sort(
                key=lambda p: (p["horas_programadas"] / p["horas_semanales"], p["ficha"])
            )

        coordinacion = None

        if self.scope.restricted:
            coordinacion = self.db.scalar(
                select(Coordinacion.nombre).where(Coordinacion.id == self.scope.coordinacion_id)
            )

        return {
            "coordinacion": coordinacion,
            "conteos": {
                "sedes": self._contar_activos(Sede),
                "ambientes": self._contar(Ambiente, *alcance["ambiente"]),
                "programas": self._contar(Programa, *alcance["programa"]),
                "fichas": self._contar(Ficha, *alcance["ficha"]),
                "trimestres": self._contar_activos(Trimestre),
                "horarios": self._contar(Horario, *alcance["horario"], solo_activos=False),
            },
            "usuarios": {role.value: total for role, total in usuarios.items()},
            "trimestres_activos": [
                t for t in trimestres_vigentes if t.estado == EstadoTrimestre.ACTIVO
            ],
            "programaciones": programaciones,
        }

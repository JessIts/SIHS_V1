from uuid import UUID

from sqlalchemy import select

from app.core.exceptions import ConflictException
from app.models.ambiente import Ambiente
from app.models.coordinacion import Coordinacion
from app.models.ficha import Ficha
from app.models.ficha_trimestre import FichaTrimestre
from app.models.horario import Horario
from app.models.programa import Programa
from app.models.sede import Sede
from app.repositories.ambiente_repository import AmbienteRepository
from app.repositories.coordinacion_repository import CoordinacionRepository
from app.repositories.sede_repository import SedeRepository
from app.schemas.ambiente import AmbienteCreate
from app.services.base_service import BaseService


class AmbienteService(BaseService[Ambiente]):
    """
    Cada ambiente puede asignarse a UNA coordinación. Solo esa coordinación
    puede programar clases en él; un coordinador solo ve los suyos.
    """

    repository_class = AmbienteRepository
    entity_label = "ambiente"

    constraint_messages = {
        "uq_ambientes_sede_nombre": "Ya existe un ambiente con ese nombre en la sede.",
        "ck_ambientes_capacidad": "La capacidad debe ser mayor que cero.",
    }

    def scope_conditions(self) -> list:
        return [Ambiente.coordinacion_id == self.scope.coordinacion_id]

    def _sede(self, sede_uuid: UUID) -> Sede:
        return self.resolve(
            SedeRepository,
            sede_uuid,
            "La sede indicada no existe o está inactiva.",
        )

    def _coordinacion(self, coordinacion_uuid: UUID | None) -> Coordinacion | None:
        if coordinacion_uuid is None:
            return None

        return self.resolve(
            CoordinacionRepository,
            coordinacion_uuid,
            "La coordinación indicada no existe o está inactiva.",
        )

    def build_conditions(
        self,
        sede_uuid: UUID | None = None,
        coordinacion_uuid: UUID | None = None,
        sin_coordinacion: bool | None = None,
    ) -> list:
        conditions = []

        if sede_uuid:
            conditions.append(Ambiente.sede.has(Sede.uuid == sede_uuid))

        if coordinacion_uuid:
            conditions.append(Ambiente.coordinacion.has(Coordinacion.uuid == coordinacion_uuid))

        if sin_coordinacion:
            conditions.append(Ambiente.coordinacion_id.is_(None))

        return conditions

    def build_entity(self, data: AmbienteCreate) -> Ambiente:
        values = data.model_dump(exclude={"sede_uuid", "coordinacion_uuid"})

        return Ambiente(
            **values,
            sede=self._sede(data.sede_uuid),
            coordinacion=self._coordinacion(data.coordinacion_uuid),
        )

    def apply_update(self, entity: Ambiente, update_data: dict) -> None:
        if "sede_uuid" in update_data:
            sede_uuid = update_data.pop("sede_uuid")

            if sede_uuid is not None:
                entity.sede = self._sede(sede_uuid)

        if "coordinacion_uuid" in update_data:
            coordinacion = self._coordinacion(update_data.pop("coordinacion_uuid"))
            self._validar_reasignacion(entity, coordinacion)
            entity.coordinacion = coordinacion

        super().apply_update(entity, update_data)

    def _validar_reasignacion(
        self,
        entity: Ambiente,
        coordinacion: Coordinacion | None,
    ) -> None:
        """
        No se puede pasar el ambiente a otra coordinación si ya tiene clases
        de fichas de una coordinación distinta: quedarían clases en un
        ambiente ajeno. Dejarlo sin asignar sí se permite.
        """

        if coordinacion is None or coordinacion.id == entity.coordinacion_id:
            return

        ficha_ajena = self.db.scalar(
            select(Ficha.codigo)
            .join(FichaTrimestre, FichaTrimestre.ficha_id == Ficha.id)
            .join(Horario, Horario.ficha_trimestre_id == FichaTrimestre.id)
            .join(Programa, Programa.id == Ficha.programa_id)
            .where(
                Horario.ambiente_id == entity.id,
                Programa.coordinacion_id != coordinacion.id,
            )
            .limit(1)
        )

        if ficha_ajena:
            raise ConflictException(
                f"No se puede asignar el ambiente a {coordinacion.nombre}: tiene clases "
                f"programadas de otra coordinación (ficha {ficha_ajena}). "
                "Reprograma o elimina esas clases primero."
            )

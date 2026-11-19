from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.briefs import CoordinacionBrief, SedeBrief


class AmbienteCreate(BaseModel):
    sede_uuid: UUID
    nombre: str = Field(min_length=1, max_length=100, examples=["202 A"])
    capacidad: int | None = Field(default=None, gt=0, examples=[30])
    coordinacion_uuid: UUID | None = Field(
        default=None,
        description="Coordinación dueña del ambiente. Vacío = sin asignar.",
    )


class AmbienteUpdate(BaseModel):
    sede_uuid: UUID | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    capacidad: int | None = Field(default=None, gt=0)
    coordinacion_uuid: UUID | None = Field(
        default=None,
        description="Enviar null para dejar el ambiente sin coordinación.",
    )


class AmbienteResponse(BaseModel):
    uuid: UUID
    nombre: str
    capacidad: int | None
    sede: SedeBrief
    coordinacion: CoordinacionBrief | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

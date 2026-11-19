from dataclasses import dataclass


@dataclass(frozen=True)
class AccessScope:
    """
    Alcance de datos del usuario que hace la petición.

    coordinacion_id = None  -> sin restricción (administrador)
    coordinacion_id = N     -> solo los datos de la coordinación N (coordinador):
                               sus ambientes, las fichas de sus programas y
                               los horarios de esas fichas.
    """

    coordinacion_id: int | None = None

    @property
    def restricted(self) -> bool:
        return self.coordinacion_id is not None


UNRESTRICTED = AccessScope()

"""Alta de tickets de soporte."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Ticket:
    titulo: str
    descripcion: str
    cliente: str
    creado: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def crear_ticket(titulo: str, descripcion: str, cliente: str) -> Ticket:
    if not titulo.strip():
        raise ValueError("El título es obligatorio")
    return Ticket(titulo=titulo.strip(), descripcion=descripcion.strip(), cliente=cliente.strip())

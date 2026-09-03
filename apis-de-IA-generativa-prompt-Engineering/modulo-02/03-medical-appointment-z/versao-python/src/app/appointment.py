"""Regras determinísticas do domínio de consultas médicas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Callable


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


@dataclass(frozen=True)
class Professional:
    id: int
    name: str
    specialty: str

    def __post_init__(self) -> None:
        if self.id <= 0 or not self.name.strip() or not self.specialty.strip():
            raise ValueError("Profissional inválido")


@dataclass(frozen=True)
class Appointment:
    professional_id: int
    professional_name: str
    patient_name: str
    datetime: datetime
    reason: str

    def __post_init__(self) -> None:
        if not self.patient_name.strip() or not self.reason.strip():
            raise ValueError("Dados da consulta incompletos")
        object.__setattr__(self, "datetime", _utc(self.datetime))


@dataclass
class AppointmentCatalog:
    professionals: list[Professional] = field(default_factory=list)
    appointments: list[Appointment] = field(default_factory=list)
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def professional_by_id(self, professional_id: int) -> Professional:
        for item in self.professionals:
            if item.id == professional_id:
                return item
        raise ValueError("Profissional não encontrado")

    def find(self, professional_id: int, when: datetime, patient_name: str | None = None) -> Appointment | None:
        target = _utc(when)
        return next((item for item in self.appointments if item.professional_id == professional_id and item.datetime == target and (patient_name is None or item.patient_name.casefold() == patient_name.casefold())), None)

    def book(self, professional_id: int, when: datetime, patient_name: str, reason: str) -> Appointment:
        target = _utc(when)
        if not patient_name.strip() or not reason.strip():
            raise ValueError("Informe nome do paciente e motivo")
        professional = self.professional_by_id(professional_id)
        if target <= _utc(self.now()):
            raise ValueError("A data da consulta deve ser futura")
        with self._lock:
            if self.find(professional_id, target):
                raise ValueError("Horário indisponível para este profissional")
            appointment = Appointment(professional_id, professional.name, patient_name.strip(), target, reason.strip())
            self.appointments.append(appointment)
            return appointment

    def cancel(self, professional_id: int, when: datetime, patient_name: str) -> Appointment:
        with self._lock:
            appointment = self.find(professional_id, when, patient_name.strip())
            if appointment is None:
                raise ValueError("Consulta não encontrada para cancelamento")
            self.appointments.remove(appointment)
            return appointment


def default_catalog() -> AppointmentCatalog:
    return AppointmentCatalog(professionals=[Professional(1, "Dr. Alicio da Silva", "Cardiologia"), Professional(2, "Dra. Ana Pereira", "Dermatologia"), Professional(3, "Dra. Carol Gomes", "Neurologia")])

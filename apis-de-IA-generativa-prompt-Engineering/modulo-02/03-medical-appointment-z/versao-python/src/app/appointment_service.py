"""Serviço canônico das regras de domínio em memória."""

from app.appointment import Appointment, AppointmentCatalog, Professional, default_catalog

__all__ = ["Appointment", "AppointmentCatalog", "Professional", "default_catalog"]

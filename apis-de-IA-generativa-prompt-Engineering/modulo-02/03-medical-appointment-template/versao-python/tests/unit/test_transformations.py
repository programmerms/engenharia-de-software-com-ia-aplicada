from datetime import datetime, timedelta, timezone
from langchain_intro.appointment import AppointmentCatalog, Professional


def test_catalog_has_deterministic_professionals() -> None:
    catalog = AppointmentCatalog(professionals=[Professional(1, "Dra. Ana", "Dermatologia")])
    assert catalog.professional_by_id(1).specialty == "Dermatologia"


def test_catalog_normalizes_naive_datetime() -> None:
    now = datetime.now(timezone.utc)
    catalog = AppointmentCatalog(professionals=[Professional(1, "Dra. Ana", "Dermatologia")], now=lambda: now)
    appointment = catalog.book(1, (now + timedelta(days=1)).replace(tzinfo=None), "Maria Santos", "avaliação")
    assert appointment.datetime.tzinfo == timezone.utc

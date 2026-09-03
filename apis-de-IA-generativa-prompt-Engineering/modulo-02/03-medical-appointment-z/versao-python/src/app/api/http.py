"""Fachada canônica para o adaptador FastAPI existente."""

from app.app import ChatRequest, MedicalResponse, app, chat, run

__all__ = ["ChatRequest", "MedicalResponse", "app", "chat", "run"]
